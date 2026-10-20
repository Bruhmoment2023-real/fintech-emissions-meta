"""Build the literature-map corpus for pack 14 (fintech and carbon emissions) in the schema the shared Bibliometrix / figure / VOSviewer scripts read.
Inputs: ../../data/raw/openalex/page_*.json (full records), ../../screening/stage1_decisions.csv, ../../data/clean/candidates.csv, OpenAlex single-DOI lookups for records
found only by Crossref/DOAJ/Semantic Scholar (cached through ../../code/netcache.py), then reference resolution for references cited at least four times.
Corpus rule: every record the stage-1 hand screen judged to have a fintech or digital-finance exposure (all decisions except E1 not-fintech), plus every OpenAlex hit passing the
protocol's lexical test that has not yet been screened. Outputs: data/clean/master.csv, references.csv, search_counts.json."""
import os, sys, json, re, glob, csv, collections, unicodedata, math
import pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); BASE = os.path.dirname(HERE); PACK = os.path.dirname(BASE)
sys.path.insert(0, os.path.join(PACK, 'code'))
from netcache import get
CLEAN = os.path.join(BASE, 'data', 'clean'); os.makedirs(CLEAN, exist_ok=True)
SEL = 'id,doi,title,publication_year,publication_date,type,language,abstract_inverted_index,primary_location,best_oa_location,open_access,cited_by_count,authorships,referenced_works,keywords,primary_topic,is_retracted'
def abstract(w):
    if not w.get('abstract_inverted_index'): return ''
    pos = {}
    for k, ps in w['abstract_inverted_index'].items():
        for p in ps: pos[p] = k
    return ' '.join(pos[k] for k in sorted(pos))
def sid(x): return (x or '').replace('https://openalex.org/', '')
def up(s): return re.sub(r'\s+', ' ', unicodedata.normalize('NFKD', s or '').encode('ascii', 'ignore').decode().upper()).strip()
def au_short(name):
    parts = (name or '').replace('.', ' ').split()
    if not parts: return ''
    last = parts[-1]; ini = ''.join(p[0] for p in parts[:-1])
    return up(f'{last} {ini}').strip()
# ---- 1 collect OpenAlex works
works = {}
for f in glob.glob(os.path.join(PACK, 'data', 'raw', 'openalex', 'page_*.json')):
    for w in json.load(open(f, encoding='utf-8'))['results']: works[sid(w['id'])] = w
n_oa_search = len(works)
dec = pd.read_csv(os.path.join(PACK, 'screening', 'stage1_decisions.csv'), dtype=str) if os.path.exists(os.path.join(PACK, 'screening', 'stage1_decisions.csv')) else pd.DataFrame(columns=['key', 'reason_code'])
cand = pd.read_csv(os.path.join(PACK, 'data', 'clean', 'candidates.csv'), dtype=str)
def nt(t): return re.sub(r'[^a-z0-9]+', ' ', unicodedata.normalize('NFKD', (t or '').lower())).strip()
cand['key'] = cand.apply(lambda r: r['doi'] if isinstance(r['doi'], str) and r['doi'] else 't:' + nt(r['title'])[:100], axis=1)
dmap = dict(zip(dec['key'], dec['reason_code']))
keep_dois = [r['doi'] for _, r in cand.iterrows() if isinstance(r['doi'], str) and dmap.get(r['key'], '') not in ('E1', 'E6', 'E7') and (r['key'] in dmap or r['rule_exclude'] != r['rule_exclude'])]
# ---- 2 lookups for DOIs not yet in works
have_doi = {(w.get('doi') or '').replace('https://doi.org/', '').lower(): k for k, w in works.items()}
miss = [d for d in keep_dois if d.lower() not in have_doi]
print('openalex search works', n_oa_search, '| keep dois', len(keep_dois), '| single lookups needed', len(miss), flush=True)
for i, d in enumerate(miss):
    s, j = get('https://api.openalex.org/works/doi:' + d, params={'select': SEL})
    if s == 200 and isinstance(j, dict) and j.get('id'): works[sid(j['id'])] = j
    if i % 50 == 0: print('lookup', i, len(miss), flush=True)
# ---- 3 rows
lex_fin = re.compile(r"fin-?tech|financial technolog|digital (inclusive )?financ|digital financial|inclusive finance|mobile (payment|money|banking)|online lending|digital banking|internet financ", re.I)
lex_emi = re.compile(r"carbon|co2|co\s?2|emission|greenhouse|ghg|decarboni", re.I)
rows = []; refrows = []
dec_by_doi = {r['doi']: dmap.get(r['key'], '') for _, r in cand.iterrows() if isinstance(r['doi'], str)}
for k, w in works.items():
    doi = (w.get('doi') or '').replace('https://doi.org/', '').lower()
    title = w.get('title') or ''; ab = abstract(w); text = title + ' ' + ab
    code = dec_by_doi.get(doi, '')
    in_scope = (code not in ('E1', 'E6', 'E7') and (code or (lex_fin.search(text) and lex_emi.search(text))))
    if not in_scope: continue
    if (w.get('language') or 'en') != 'en' and code == '': continue
    yr = w.get('publication_year')
    if yr is None or yr < 2015: continue
    loc = w.get('primary_location') or {}; src = loc.get('source') or {}
    ships = w.get('authorships') or []
    authors = [(a.get('author') or {}).get('display_name') or '' for a in ships]
    insts = []; pairs = []; ccs = []; rp = []; corr_cc = ''
    for a in ships:
        ai = a.get('institutions') or []
        for i in ai:
            insts.append(i.get('display_name') or ''); pairs.append(f"{i.get('display_name') or ''} [{i.get('country_code') or ''}]")
            if a.get('is_corresponding'): rp.append(f"{i.get('display_name') or ''} [{i.get('country_code') or ''}]"); corr_cc = corr_cc or (i.get('country_code') or '')
        cc = next((i.get('country_code') for i in ai if i.get('country_code')), None)
        if cc: ccs.append(cc)
    if not corr_cc and ccs: corr_cc = ccs[0]
    kws = [x.get('display_name') for x in (w.get('keywords') or []) if x.get('display_name')]
    pt = w.get('primary_topic') or {}
    refs = [sid(x) for x in (w.get('referenced_works') or [])]
    for r in refs: refrows.append((k, r))
    t = w.get('type') or 'article'
    lexical = bool(lex_fin.search(text) and lex_emi.search(text))
    if code in ('E3',) or re.search(r'review|bibliometric|literature|survey', title, re.I): sub = 'R'
    elif code == 'I' or (code == '' and lexical): sub = 'C'
    else: sub = 'O'
    fa = au_short(authors[0]) if authors else ''
    so = up(src.get('display_name') or '')
    rows.append(dict(id=k, title=title, abstract=ab, year=yr, pub_date=w.get('publication_date'), venue=src.get('display_name') or '', doc_type=('review' if t == 'review' else 'article'),
        authors='; '.join(authors), author_ids='', n_authors=len(authors), doi=doi, url=loc.get('landing_page_url') or '', oa_pdf_url=(w.get('best_oa_location') or {}).get('pdf_url') or '',
        cited_by=w.get('cited_by_count') or 0, cited_by_openalex=w.get('cited_by_count') or 0, ref_count_reported=len(refs), refs_listed=len(refs), refs_in_corpus=0, local_citations=0,
        sublits=sub, primary_sublit=sub, found_in='openalex_search' if k in set(list(works)[:n_oa_search]) else 'crossref_doaj_s2', merged_versions='', snowball=0, forced_seed=0, in_semantic_scholar='',
        openalex_id=k, openalex_type=t, institutions='; '.join(dict.fromkeys(insts)), author_institutions='', affil_pairs='; '.join(pairs), reprint_affil='; '.join(rp), countries=';'.join(dict.fromkeys(ccs)),
        author_countries_all=';'.join(ccs), first_author_country=ccs[0] if ccs else '', corresponding_country=corr_cc, openalex_keywords='; '.join(kws), openalex_topic=pt.get('display_name') or '',
        openalex_subfield=(pt.get('subfield') or {}).get('display_name') or '', openalex_field=(pt.get('field') or {}).get('display_name') or '', is_oa=str((w.get('open_access') or {}).get('is_oa')),
        language=w.get('language') or 'en', stage1_code=code or 'unscreened', is_retracted=str(w.get('is_retracted')), AU=';'.join(au_short(a) for a in authors), SO=so, SR=f'{fa}, {yr}, {so}'))
m = pd.DataFrame(rows).drop_duplicates('id')
# title/year de-duplication of preprint vs published versions
m['tk'] = m.title.map(lambda t: nt(t)[:90]); m = m.sort_values(['tk', 'year']).reset_index(drop=True)
dup = m.duplicated('tk', keep='last'); m.loc[m['tk'].isin(m[dup]['tk']) & ~dup, 'merged_versions'] = 'merged'; removed = int(dup.sum()); m = m[~dup].drop(columns='tk')
ids = set(m.id)
refs = pd.DataFrame(refrows, columns=['citing', 'cited']); refs = refs[refs.citing.isin(ids)].drop_duplicates()
cnt = refs.cited.value_counts(); m['local_citations'] = m.id.map(lambda i: int(cnt.get(i, 0))); rc = refs[refs.cited.isin(ids)].citing.value_counts(); m['refs_in_corpus'] = m.id.map(lambda i: int(rc.get(i, 0)))
# resolve cited references cited >= 4 times (single lookups)
todo = [c for c, n in cnt.items() if n >= 4]
print('references to resolve', len(todo), 'of', cnt.shape[0], flush=True)
meta = {}
cache_f = os.path.join(BASE, 'data', 'raw', 'ref_meta.json')
if os.path.exists(cache_f): meta = json.load(open(cache_f, encoding='utf-8'))
for i, c in enumerate(todo):
    if c in meta: continue
    s, j = get('https://api.openalex.org/works/' + c, params={'select': 'id,doi,title,publication_year,primary_location,authorships'})
    if s == 200 and isinstance(j, dict):
        a = ((j.get('authorships') or [{}])[0].get('author') or {}).get('display_name') or ''
        meta[c] = dict(title=j.get('title') or '', year=j.get('publication_year') or '', venue=((j.get('primary_location') or {}).get('source') or {}).get('display_name') or '', doi=(j.get('doi') or '').replace('https://doi.org/', ''), first=a)
    if i % 100 == 0: print('ref', i, len(todo), flush=True); json.dump(meta, open(cache_f, 'w', encoding='utf-8'))
json.dump(meta, open(cache_f, 'w', encoding='utf-8'))
def cr(c):
    x = meta.get(c)
    if not x or not x['first']: return ''
    return f"{au_short(x['first'])}, {x['year']}, {up(x['venue'])}" + (f", DOI {x['doi'].upper()}" if x['doi'] else '')
refs['cited_title'] = refs.cited.map(lambda c: meta.get(c, {}).get('title', '')); refs['cited_year'] = refs.cited.map(lambda c: meta.get(c, {}).get('year', ''))
refs['cited_first_author'] = refs.cited.map(lambda c: meta.get(c, {}).get('first', '')); refs['cited_venue'] = refs.cited.map(lambda c: meta.get(c, {}).get('venue', ''))
refs['cited_doi'] = refs.cited.map(lambda c: meta.get(c, {}).get('doi', '')); refs['cited_arxiv'] = ''; refs['cited_acl'] = ''; refs['in_corpus'] = refs.cited.isin(ids).astype(int); refs['cr'] = refs.cited.map(cr)
m.to_csv(os.path.join(CLEAN, 'master.csv'), index=False, encoding='utf-8-sig'); refs.to_csv(os.path.join(CLEAN, 'references.csv'), index=False, encoding='utf-8-sig')
json.dump(dict(openalex_search_works=n_oa_search, works_after_lookups=len(works), corpus=len(m), version_duplicates_removed=removed, reference_links=len(refs), refs_cited_2plus=len(todo), refs_resolved=len(meta),
               by_sublit=m.primary_sublit.value_counts().to_dict(), by_stage1=m.stage1_code.value_counts().to_dict()), open(os.path.join(CLEAN, 'search_counts.json'), 'w'), indent=1)
print(open(os.path.join(CLEAN, 'search_counts.json')).read())
