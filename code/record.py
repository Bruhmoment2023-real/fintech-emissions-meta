"""Record stage-1 decisions for the first batch shown by queue_view.py. Usage: python record.py "0:E3,1:I,2:E2" [note-file-free]
Codes: I include for full-text; E1 not fintech/digital-finance exposure; E2 not an emissions outcome (other outcome); E3 not an empirical regression estimate (review, theory, simulation, ML, descriptive);
E4 other environmental outcome only (LCF, footprint, pollution); E5 duplicate or version; E6 non-English; E7 out of period; E8 retracted study or retraction notice. Appends to screening/stage1_decisions.csv with UTC time."""
import sys, os, re, unicodedata, csv, datetime
import pandas as pd
os.chdir(os.path.dirname(os.path.abspath(__file__)))
REASONS = {'I': 'include for full-text assessment', 'E1': 'not fintech or digital-finance exposure', 'E2': 'not an emissions outcome (other outcome)', 'E3': 'not an empirical regression estimate (review, theory, simulation, ML or descriptive)',
           'E4': 'other environmental outcome only (load capacity factor, footprint, pollutant)', 'E5': 'duplicate or version of another record', 'E6': 'non-English', 'E7': 'out of period', 'E8': 'retracted or retraction notice'}
spec = sys.argv[1]; n_show = max(int(x.split(':')[0]) for x in spec.split(',')) + 1
d = pd.read_csv('../data/clean/candidates.csv', dtype=str)
def nt(t): return re.sub(r'[^a-z0-9]+', ' ', unicodedata.normalize('NFKD', (t or '').lower())).strip()
d['key'] = d.apply(lambda r: r['doi'] if isinstance(r['doi'], str) and r['doi'] else 't:' + nt(r['title'])[:100], axis=1)
q = d[d.rule_exclude.isna()].copy()
fp = '../screening/stage1_decisions.csv'; done = set()
if os.path.exists(fp): done = set(pd.read_csv(fp, dtype=str)['key'])
q = q[~q.key.isin(done)].sort_values('title').reset_index(drop=True)
new = not os.path.exists(fp)
w = csv.writer(open(fp, 'a', newline='', encoding='utf-8'))
if new: w.writerow(['key', 'title', 'year', 'venue', 'decision', 'reason_code', 'reason', 'screened_utc'])
t = datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%d %H:%M')
cnt = 0
for part in spec.split(','):
    i, code = part.split(':'); i = int(i); r = q.iloc[i]
    w.writerow([r['key'], r['title'], r['year'], r['venue'], 'include' if code == 'I' else 'exclude', code, REASONS[code], t]); cnt += 1
print('recorded', cnt)
