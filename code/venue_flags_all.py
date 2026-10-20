"""Warning-list matches for every record that passed stage 1 (include) and for the 55 extracted studies. Output data/venue_flags.csv. Matches are leads to inspect, not verdicts."""
import os, sys, re, html
import pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); os.chdir(HERE); sys.path.insert(0, HERE)
from flag_venues import match
d = pd.read_csv('../screening/stage1_decisions.csv', dtype=str); inc = d[d.decision == 'include']
c = pd.read_csv('../data/clean/candidates.csv', dtype=str)
c['key'] = c.apply(lambda r: r['doi'] if isinstance(r['doi'], str) and r['doi'] else 't:' + re.sub(r'[^a-z0-9]+', ' ', str(r['title']).lower()).strip()[:100], axis=1)
m = inc.merge(c[['key', 'publisher', 'issn']].drop_duplicates('key'), on='key', how='left')
ext = set(pd.read_csv('../extraction/studies.csv', dtype=str).study_id)
rows = []
for _, r in m.iterrows():
    v = html.unescape(str(r['venue']) if isinstance(r['venue'], str) else ''); p = html.unescape(str(r['publisher']) if isinstance(r['publisher'], str) else '')
    mv, mp = match(v), match(p)
    rows.append(dict(key=r['key'], venue=v, publisher=p, flag=int(bool(mv or mp)), detail=(str(mv) if mv else '') + (' | ' + str(mp) if mp else ''), extracted=int(str(r['key']).lower() in ext)))
o = pd.DataFrame(rows); o.to_csv('../data/venue_flags.csv', index=False)
print('stage1 included', len(o), 'flagged', int(o.flag.sum()), '| extracted studies in file', int(o.extracted.sum()), 'flagged among them', int(o[o.extracted == 1].flag.sum()))
print(o[o.flag == 1].groupby(['venue', 'publisher']).size().sort_values(ascending=False).to_string())
