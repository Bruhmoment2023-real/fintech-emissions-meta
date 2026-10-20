"""Fetch missing abstracts (and OA info) by single-record OpenAlex lookup (free) for records with a DOI, no abstract, and a fintech term in the title. Cached.
Output data/clean/abstract_enrichment.csv (doi, abstract, oa_status, best_pdf, openalex_id)."""
import sys, os, csv
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from netcache import get
import pandas as pd
os.chdir(os.path.dirname(os.path.abspath(__file__)))
d = pd.read_csv('../data/clean/candidates.csv', dtype=str)
x = d[(d.has_abstract == 'False') & d.doi.notna() & ((d.fin_hit == 'True'))]
done = {}
p = '../data/clean/abstract_enrichment.csv'
if os.path.exists(p): done = {r['doi']: r for r in csv.DictReader(open(p, encoding='utf-8'))}
out = list(done.values())
for doi in x.doi:
    if doi in done: continue
    s, j = get('https://api.openalex.org/works/doi:' + doi, params={'select': 'id,abstract_inverted_index,open_access,best_oa_location'})
    ab = ''
    if s == 200 and j.get('abstract_inverted_index'):
        pos = {}
        for w, ps in j['abstract_inverted_index'].items():
            for q in ps: pos[q] = w
        ab = ' '.join(pos[k] for k in sorted(pos))
    out.append(dict(doi=doi, abstract=ab, oa_status=(j.get('open_access') or {}).get('oa_status') if s == 200 else '', best_pdf=((j.get('best_oa_location') or {}).get('pdf_url') or '') if s == 200 else '', openalex_id=j.get('id', '') if s == 200 else ''))
w = csv.DictWriter(open(p, 'w', newline='', encoding='utf-8'), fieldnames=['doi', 'abstract', 'oa_status', 'best_pdf', 'openalex_id']); w.writeheader(); w.writerows(out)
print(len(out), sum(1 for r in out if r['abstract']))
