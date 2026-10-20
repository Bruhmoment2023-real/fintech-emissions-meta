"""Rule-based stage-1 exclusions for clear cases (validated against my hand decisions on the first 413 records before use on the rest).
R-core: no core fintech/digital-finance term in title+abstract (blockchain, crypto, peer-to-peer or 'financial innovation' alone do not count) -> E1.
R-rev: abstract carries a review/conceptual cue and NO empirical cue -> E3.
Writes screening/stage1_auto_validation.json and (with arg 'apply') appends the auto decisions to stage1_decisions.csv with the reason prefixed 'AUTO RULE'."""
import os, re, sys, unicodedata, csv, json, datetime
import pandas as pd
os.chdir(os.path.dirname(os.path.abspath(__file__)))
d = pd.read_csv('../data/clean/candidates.csv', dtype=str)
def nt(t): return re.sub(r'[^a-z0-9]+', ' ', unicodedata.normalize('NFKD', (t or '').lower())).strip()
d['key'] = d.apply(lambda r: r['doi'] if isinstance(r['doi'], str) and r['doi'] else 't:' + nt(r['title'])[:100], axis=1)
core = re.compile(r"fin-?tech|financial technolog|digital (inclusive )?financ|digital financial|inclusive finance|mobile (payment|money|banking)|digital payment|online lending|internet financ|digital banking|financial inclusion", re.I)
rev = re.compile(r"\b(review|bibliometric|scoping|systematic literature|literature (review|survey)|conceptual|framework paper|state of the art|research agenda|we propose a (framework|platform|architecture)|case study of|perspective)\b", re.I)
emp = re.compile(r"panel|regression|GMM|ARDL|fixed.effect|data (from|for|of|on)|using data|estimat|econometric|empirical|evidence from|difference.in.difference|quantile|cointegration|spatial|provinc|prefecture|cities|countries|firm-level|listed (compan|firm)|sample", re.I)
d['text'] = (d['title'].fillna('') + ' ' + d['abstract'].fillna(''))
def auto(r):
    t = r['text']
    if not core.search(t): return 'E1', 'AUTO RULE: no core fintech or digital-finance term in title or abstract'
    if r['abstract'] == r['abstract'] and len(str(r['abstract'])) > 150 and rev.search(t) and not emp.search(str(r['abstract'])): return 'E3', 'AUTO RULE: review or conceptual cue and no empirical cue in the abstract'
    return None, None
fp = '../screening/stage1_decisions.csv'; dec = pd.read_csv(fp, dtype=str); hand = dict(zip(dec['key'], dec['reason_code']))
d['auto_code'], d['auto_reason'] = zip(*d.apply(auto, axis=1))
chk = d[d.key.isin(hand) & d.auto_code.notna()]
bad = chk[chk.key.map(hand) == 'I']
val = dict(hand_screened=len(hand), auto_flagged_among_hand=len(chk), auto_would_exclude_a_hand_INCLUDE=len(bad), details=bad[['key', 'title', 'auto_code']].values.tolist()[:20],
           agreement_pct_on_flagged=round(100 * (chk.auto_code == chk.key.map(hand)).mean(), 1) if len(chk) else None)
json.dump(val, open('../screening/stage1_auto_validation.json', 'w'), indent=1, default=str); print(json.dumps(val, indent=1, default=str)[:1500])
q = d[(d.rule_exclude.isna()) & (~d.key.isin(hand)) & d.auto_code.notna()]
print('unscreened', int(((d.rule_exclude.isna()) & (~d.key.isin(hand))).sum()), '| auto-excludable', len(q), q.auto_code.value_counts().to_dict())
if len(sys.argv) > 1 and sys.argv[1] == 'apply':
    t = datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%d %H:%M')
    with open(fp, 'a', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        for _, r in q.iterrows(): w.writerow([r['key'], r['title'], r['year'], r['venue'], 'exclude', r['auto_code'], r['auto_reason'], t])
    print('applied', len(q))
