"""View the next unscreened batch from the hand-screening queue. Usage: python queue_view.py <batch_size> [offset_from_first_unscreened]
Queue = candidates not rule-excluded, minus those already in screening/stage1_decisions.csv. Prints idx|year|venue|title|abstract[:N]."""
import sys, os, re, unicodedata, csv
import pandas as pd
os.chdir(os.path.dirname(os.path.abspath(__file__)))
n = int(sys.argv[1]); N_AB = int(sys.argv[2]) if len(sys.argv) > 2 else 520
d = pd.read_csv('../data/clean/candidates.csv', dtype=str)
enr = '../data/clean/abstract_enrichment.csv'
def nt(t): return re.sub(r'[^a-z0-9]+', ' ', unicodedata.normalize('NFKD', (t or '').lower())).strip()
d['key'] = d.apply(lambda r: r['doi'] if isinstance(r['doi'], str) and r['doi'] else 't:' + nt(r['title'])[:100], axis=1)
q = d[d.rule_exclude.isna()].copy()
done = set()
fp = '../screening/stage1_decisions.csv'
if os.path.exists(fp): done = set(pd.read_csv(fp, dtype=str)['key'])
q = q[~q.key.isin(done)].sort_values('title')
print('unscreened remaining:', len(q))
for i, (_, r) in enumerate(q.head(n).iterrows()):
    ab = (r['abstract'] if isinstance(r['abstract'], str) else '')[:N_AB].replace('\n', ' ')
    print(f"[{i}] {r['key']} | {r['year']} | {str(r['venue'])[:40]} | {r['title']}\n     {ab}")
