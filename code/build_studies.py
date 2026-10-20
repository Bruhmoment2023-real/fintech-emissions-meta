"""Build extraction/studies.csv and the analysis-ready extraction/estimates.csv from estimates_raw.csv.
Study metadata from data/clean/candidates.csv; first author from OpenAlex single lookups (cached); DOAJ status by ISSN (DOAJ API, cached);
warning-list flags from flag_venues.match (Kscien non-recommended lists, Beall's publishers/standalone journals/hijacked journals).
Only rows with verified == 1 enter estimates.csv."""
import os, sys, re, json
import pandas as pd, html
def clean(x): return re.sub('[' + chr(0x2010) + chr(0x2011) + chr(0x2012) + ']', '-', re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', '', html.unescape(str(x or ''))))).strip()
HERE = os.path.dirname(os.path.abspath(__file__)); os.chdir(HERE); sys.path.insert(0, HERE)
from netcache import get
from flag_venues import match
est = pd.read_csv('../extraction/estimates_raw.csv', dtype=str)
cand = pd.read_csv('../data/clean/candidates.csv', dtype=str); cand['doi_l'] = cand['doi'].str.lower()
rows = []
for doi in est.study_id.unique():
    c = cand[cand.doi_l == doi]
    c = c.iloc[0] if len(c) else None
    s, j = get('https://api.openalex.org/works/doi:' + doi, params={'select': 'id,title,publication_year,type,authorships,primary_location,is_retracted,open_access'})
    j = j if (s == 200 and isinstance(j, dict)) else {}
    src = (j.get('primary_location') or {}).get('source') or {}
    fa = (((j.get('authorships') or [{}])[0].get('author') or {}).get('display_name')) or ''
    venue = (c['venue'] if c is not None and isinstance(c['venue'], str) else '') or src.get('display_name') or ''
    pub = (c['publisher'] if c is not None and isinstance(c['publisher'], str) else '') or src.get('host_organization_name') or ''
    issn = (c['issn'] if c is not None and isinstance(c['issn'], str) else '') or src.get('issn_l') or ''
    title = (c['title'] if c is not None else '') or j.get('title') or ''
    year = (c['year'] if c is not None else '') or j.get('publication_year') or ''
    indoaj = ''
    for i in re.split(r'[;,]', issn):
        i = i.strip()
        if i:
            s2, d = get('https://doaj.org/api/search/journals/issn:' + i)
            indoaj = 'yes' if (s2 == 200 and isinstance(d, dict) and d.get('results')) else 'no'
            if indoaj == 'yes': break
    venue, pub, title, fa = clean(venue), clean(pub), clean(title), clean(fa)
    mv, mp = match(venue), match(pub)
    typ = (j.get('type') or (c['type'] if c is not None else '') or '')
    status = 'preprint' if (re.search(r'ssrn|research square|arxiv|preprint|zenodo', venue, re.I) or typ == 'preprint') else 'journal'
    rows.append(dict(study_id=doi, first_author=(fa.split()[-1] if fa else ''), first_author_full=fa, year=year, title=title, venue=venue, publisher=pub, issn=issn, in_doaj=indoaj, pub_status=status,
                     venue_flag=int(bool(mv or mp)), venue_flag_detail=(str(mv) if mv else '') + (' | ' + str(mp) if mp else ''), is_retracted=j.get('is_retracted', '')))
    print(doi, venue[:30], indoaj, int(bool(mv or mp)), flush=True)
st = pd.DataFrame(rows); st.to_csv('../extraction/studies.csv', index=False)
e = est[est.verified == '1'].merge(st[['study_id', 'first_author', 'year', 'venue', 'publisher', 'in_doaj', 'pub_status', 'venue_flag']], on='study_id', how='left')
e['inconsistent_flag'] = e.notes.fillna('').str.contains('INCONSISTENT').astype(int)
e['n_inferred_flag'] = e.notes.fillna('').str.contains('N_inferred|N inferred|inferred', case=False).astype(int)
e['primary_fallback_flag'] = e.notes.fillna('').str.contains('primary_fallback').astype(int)
e['retracted_flag'] = 0
e['sample_overlap_flag'] = 0
dupkey = e[e.primary == '1'].groupby(['fintech_measure', 'unit', 'period', 'n_obs']).study_id.transform('nunique')
e.loc[dupkey[dupkey > 1].index, 'sample_overlap_flag'] = 1
# sample midpoint year from period strings
def mid(p):
    ys = re.findall(r'(20\d\d)', str(p))
    return (int(ys[0]) + int(ys[1])) / 2 if len(ys) >= 2 else None
e['sample_mid_year'] = e.period.map(mid)
# coarse region for the moderator
def region(r):
    x = str(r).lower()
    if x.startswith('china'): return 'China'
    if 'asia' in x: return 'other Asia'
    if 'brics' in x or 'multi' in x or 'g20' in x: return 'multi-country'
    return 'other'
e['region_group'] = e.region.map(region)
keep = ['study_id', 'est_id', 'primary', 'in_main_table', 'first_author', 'year', 'venue', 'pub_status', 'venue_flag', 'in_doaj', 'region', 'region_group', 'unit', 'period', 'sample_mid_year', 'fintech_measure', 'fintech_type',
        'emissions_measure', 'emissions_type', 'log_form', 'estimator', 'b', 'se', 't', 'p', 'n_obs', 'n_units', 'k_reg', 'k_reg_reported', 'table', 'page', 'model_label', 'inconsistent_flag', 'n_inferred_flag',
        'primary_fallback_flag', 'retracted_flag', 'sample_overlap_flag', 'notes', 'evidence_snippet']
e = e[keep].copy()
e['region_orig'] = e['region']; e['region'] = e['region_group']; e = e.drop(columns=['region_group'])
e.to_csv('../extraction/estimates.csv', index=False)
print('studies', len(st), 'estimates', len(e), 'primary', int((e.primary == '1').sum()))
