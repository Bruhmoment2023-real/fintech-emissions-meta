"""Merge all search sources, de-duplicate, apply the protocol's rule-based pre-screen (clear exclusions only), write data/clean/candidates.csv and the screening log
for rule-excluded records. Everything not rule-excluded goes to hand screening (screening/handscreen_queue.csv). Re-run after any new search source arrives."""
import os, json, re, csv, glob, unicodedata
import pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); os.chdir(HERE)
RAW = '../data/raw/'; OUT = '../data/clean/'; SCR = '../screening/'
os.makedirs(OUT, exist_ok=True); os.makedirs(SCR, exist_ok=True)
rows = []
for f in sorted(glob.glob(RAW + 'records_*.jsonl')):
    for l in open(f, encoding='utf-8'): rows.append(json.loads(l))
def nt(t): return re.sub(r'[^a-z0-9]+', ' ', unicodedata.normalize('NFKD', (t or '').lower())).strip()
recs = {}; title_idx = {}
for r in rows:
    r['doi'] = (r.get('doi') or '').lower().replace('https://doi.org/', '')
    key = r['doi'] or ('t:' + nt(r.get('title'))[:120])
    tk = nt(r.get('title'))[:120]
    if not r['doi'] and tk in title_idx: key = title_idx[tk]
    elif r['doi'] and tk in title_idx and title_idx[tk] != key and title_idx[tk] in recs: key = title_idx[tk]  # same title, different doi form: merge
    if key in recs:
        c = recs[key]; c['sources'].add(r['source'])
        for k in ('abstract', 'venue', 'publisher', 'url', 'openalex_id', 'oa_status', 'first_author', 'cited_by', 'language', 'issn'):
            if not c.get(k) and r.get(k): c[k] = r[k]
        if len(r.get('abstract') or '') > len(c.get('abstract') or ''): c['abstract'] = r['abstract']
        if not c.get('doi') and r['doi']: c['doi'] = r['doi']
    else:
        c = dict(r); c['sources'] = {r['source']}; recs[key] = c; title_idx[tk] = key
df = pd.DataFrame(recs.values()); df['sources'] = df['sources'].apply(lambda s: '+'.join(sorted(s)))
df['year'] = pd.to_numeric(df['year'], errors='coerce')
fin = re.compile(r"fin-?tech|financial technolog|digital financ|digital inclusive|inclusive finance|digital financial|mobile (payment|money|banking)|internet financ|digital payment|crypto|blockchain|peer-to-peer|online lending|digital banking|financial innovation", re.I)
emi = re.compile(r"carbon|co2|co\s?2|emission|greenhouse|ghg|decarboni|net.zero", re.I)
rev = re.compile(r"\b(bibliometric|scientometric|systematic (literature )?review|literature review|scoping review|meta-analysis|review of the literature|research agenda|state of the art|science mapping)\b", re.I)
enr_p = '../data/clean/abstract_enrichment.csv'
if os.path.exists(enr_p):
    en = pd.read_csv(enr_p, dtype=str).dropna(subset=['abstract']); en = en[en.abstract.str.len() > 80].drop_duplicates('doi').set_index('doi')['abstract']
    miss = df['abstract'].fillna('').str.len() < 80
    df.loc[miss, 'abstract'] = df.loc[miss, 'doi'].map(en).fillna(df.loc[miss, 'abstract'])
df['text'] = (df['title'].fillna('') + ' ' + df['abstract'].fillna('')).str.strip()
df['has_abstract'] = df['abstract'].fillna('').str.len() > 80
df['fin_hit'] = df['text'].str.contains(fin); df['emi_hit'] = df['text'].str.contains(emi)
def rule(r):
    if pd.notna(r['year']) and r['year'] < 2015: return 'out of period'
    if r.get('language') and isinstance(r['language'], str) and r['language'] not in ('en', 'EN', ''): return 'non-English'
    if r['has_abstract']:
        if not r['fin_hit']: return 'not fintech exposure (no fintech/digital-finance term in title or abstract)'
        if not r['emi_hit']: return 'not emissions outcome (no emissions term in title or abstract)'
    else:
        if not (r['fin_hit'] and r['emi_hit']): return 'NO_ABSTRACT_TITLE_LACKS_TERMS'
    if rev.search(r['title'] or '') and not re.search(r'empirical|panel|regression|evidence from', r['title'] or '', re.I): return 'review or bibliometric (title)'
    return ''
df['rule_exclude'] = df.apply(rule, axis=1)
df.drop(columns=['text']).to_csv(OUT + 'candidates.csv', index=False)
print('records in', len(rows), 'unique', len(df)); print(df['rule_exclude'].replace('', 'PASS').value_counts().to_string())
print(df.groupby('sources').size().to_string())
