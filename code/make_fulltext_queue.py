"""For every stage-1 included record with a DOI: OpenAlex single lookup (cached) for open-access status and candidate PDF URLs -> screening/fulltext_queue.csv.
Records without a DOI (title-only keys) are listed in screening/no_doi_included.csv for manual DOI lookup."""
import os, sys, re, csv, unicodedata
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from netcache import get
import pandas as pd
os.chdir(os.path.dirname(os.path.abspath(__file__)))
dec = pd.read_csv('../screening/stage1_decisions.csv', dtype=str)
inc = dec[dec.decision == 'include']
rows = []; nodoi = []
for _, r in inc.iterrows():
    k = r['key']
    if k.startswith('t:'): nodoi.append(r.to_dict()); continue
    s, j = get('https://api.openalex.org/works/doi:' + k, params={'select': 'id,open_access,best_oa_location,locations,is_retracted,type,publication_year'})
    if s != 200 or not isinstance(j, dict): rows.append(dict(doi=k, openalex_id='', oa_status='lookup_failed', is_oa='', pdf_url='', locs='', is_retracted='', title=r['title'], year=r['year'], venue=r['venue'])); continue
    locs = [l.get('pdf_url') for l in (j.get('locations') or []) if l and l.get('pdf_url')]
    best = (j.get('best_oa_location') or {}).get('pdf_url') or ''
    rows.append(dict(doi=k, openalex_id=j.get('id', ''), oa_status=(j.get('open_access') or {}).get('oa_status', ''), is_oa=(j.get('open_access') or {}).get('is_oa', ''), pdf_url=best, locs='|'.join(dict.fromkeys(locs)), is_retracted=j.get('is_retracted', ''), title=r['title'], year=r['year'], venue=r['venue']))
pd.DataFrame(rows).to_csv('../screening/fulltext_queue_all.csv', index=False)
pd.DataFrame(nodoi).to_csv('../screening/no_doi_included.csv', index=False)
q = pd.DataFrame(rows); print(q.oa_status.value_counts().to_dict(), 'retracted flagged:', (q.is_retracted.astype(str) == 'True').sum(), 'no-doi:', len(nodoi))
q[q.is_oa.astype(str) == 'True'].to_csv('../screening/fulltext_queue.csv', index=False); print('open-access queue', (q.is_oa.astype(str) == 'True').sum())
