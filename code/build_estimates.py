"""Parse hand-coded entry lines (extraction/entries/*.txt), verify every coefficient and standard error against the opened full text, and write
extraction/estimates.csv and extraction/studies.csv.
Entry line format (pipe separated, one estimate per line, '#' lines ignored):
 doi|primary(1/0)|model_label|b_str|se_str|t_str|p_str|n_obs|n_units|k_reg|table|page|region|unit|period|fintech_measure|fintech_type|emissions_measure|emissions_type|log_form|estimator|notes
Strings b_str, se_str, t_str are copied exactly as printed (including minus sign and stars). k_reg = number of regressors excluding intercept and fixed effects (blank if not stated).
Verification: the printed b_str and (se_str or t_str) must occur in the study's extracted text, se within 500 characters after b (whitespace, stars and minus-sign variants ignored).
Rows that fail verification stay in the file with verified=0 and are excluded from analysis until corrected."""
import os, re, sys, csv, glob, unicodedata
import pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); os.chdir(HERE)
sys.path.insert(0, HERE)
FIELDS = ['doi', 'primary', 'model_label', 'b_str', 'se_str', 't_str', 'p_str', 'n_obs', 'n_units', 'k_reg', 'table', 'page', 'region', 'unit', 'period', 'fintech_measure', 'fintech_type', 'emissions_measure', 'emissions_type', 'log_form', 'estimator', 'notes']
def safe(d): return re.sub(r'[^a-z0-9]+', '_', d.lower()).strip('_')
def nz(s):
    s = unicodedata.normalize('NFKC', s).replace('−', '-').replace('–', '-').replace('—', '-').replace('‒', '-')
    return re.sub(r'[\s*]+', '', s)
def num(s):
    if s is None or str(s).strip() == '': return None
    t = nz(str(s)).replace('(', '').replace(')', '').replace('[', '').replace(']', '').replace(',', '')
    t = re.sub(r'[^0-9.\-eE]', '', t)
    try: return float(t)
    except: return None
rows = []
for f in sorted(glob.glob('../extraction/entries/*.txt')):
    for ln, l in enumerate(open(f, encoding='utf-8')):
        l = l.rstrip('\n')
        if not l.strip() or l.lstrip().startswith('#'): continue
        p = l.split('|')
        if len(p) < len(FIELDS): p += [''] * (len(FIELDS) - len(p))
        if len(p) > len(FIELDS): p = p[:len(FIELDS) - 1] + ['|'.join(p[len(FIELDS) - 1:])]
        r = dict(zip(FIELDS, [x.strip() for x in p])); r['entry_file'] = os.path.basename(f) + f':{ln+1}'
        rows.append(r)
txt_cache = {}
def text_of(doi):
    if doi not in txt_cache:
        fp = f'../data/fulltext/{safe(doi)}.txt'
        txt_cache[doi] = nz(open(fp, encoding='utf-8', errors='replace').read()) if os.path.exists(fp) else None
    return txt_cache[doi]
out = []
for r in rows:
    t = text_of(r['doi'].lower()); ver = 0; ev = ''
    bs, ss, ts = nz(r['b_str']), nz(r['se_str']).strip('()[]'), nz(r['t_str']).strip('()[]'); ps = nz(r['p_str']).strip('()[]')
    if t is None: ev = 'NO TEXT FILE'
    elif bs:
        for m in re.finditer(re.escape(bs), t):
            win = t[m.end():m.end() + 500]
            if (ss and ss in win) or (ts and ts in win) or (ps and ps in win) or (not ss and not ts and not ps):
                ver = 1; ev = t[max(0, m.start() - 60):m.end() + 140]; break
        if not ver: ev = 'NOT FOUND (b and se/t together)'
    elif ts:
        m = re.search(re.escape(ts), t); ver = int(bool(m)); ev = t[max(0, m.start() - 80):m.end() + 80] if m else 'NOT FOUND (t)'
    r['b'] = num(r['b_str']); r['se'] = (abs(num(r['se_str'])) if num(r['se_str']) is not None else None); r['t'] = num(r['t_str']); r['p'] = num(r['p_str'])
    if 'SIGN_NEG' in (r.get('notes') or '') and r['b'] is not None: r['b'] = -abs(r['b'])
    if 'SIGN_NEG' in (r.get('notes') or '') and r['t'] is not None: r['t'] = -abs(r['t'])
    r['verified'] = ver; r['evidence_snippet'] = ev
    out.append(r)
os.makedirs('../extraction', exist_ok=True)
est = pd.DataFrame(out)
if len(est):
    est['study_id'] = est['doi'].str.lower(); est['est_id'] = est['study_id'] + '#' + est.groupby('study_id').cumcount().astype(str)
    est['in_main_table'] = 1; est['k_reg_reported'] = est['k_reg'].astype(str).str.len().gt(0).astype(int)
    est.to_csv('../extraction/estimates_raw.csv', index=False)
    print('rows', len(est), '| verified', int(est.verified.sum()), '| unverified', int((est.verified == 0).sum()), '| studies', est.study_id.nunique())
    print(est[est.verified == 0][['entry_file', 'doi', 'b_str', 'se_str', 'evidence_snippet']].to_string())
