"""Pack 14 searches (protocol 02a section 3). Resumable: every response is cached (data/cache/http.sqlite; OpenAlex pages also as JSON in data/raw/openalex/).
No email or personal identifier is sent. Usage: python search14.py <source> where source is crossref | doaj | s2 | openalex
Each run appends one line per query to data/raw/search_log.csv (source, string, date-time UTC, hits reported, records saved)."""
import sys, os, json, csv, time, datetime as dt, re
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from netcache import get
import requests
RAW = os.path.join(HERE, '..', 'data', 'raw'); os.makedirs(RAW, exist_ok=True)
LOG = os.path.join(RAW, 'search_log.csv')
def log(src, q, total, saved, note=''):
    new = not os.path.exists(LOG)
    with open(LOG, 'a', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        if new: w.writerow(['source', 'query_string', 'run_utc', 'hits_reported', 'records_saved', 'note'])
        w.writerow([src, q, dt.datetime.now(dt.timezone.utc).strftime('%Y-%m-%d %H:%M:%S'), total, saved, note])
FIN = '(fintech OR "fin-tech" OR "financial technology" OR "digital finance" OR "digital financial" OR "digital inclusive finance" OR "digital financial inclusion")'
EMI = '(carbon OR CO2 OR emission OR emissions OR "greenhouse gas" OR decarbonization OR decarbonisation)'
CORE = FIN + ' AND ' + EMI
PHRASES = ['fintech carbon emissions', 'digital finance carbon emissions', 'financial technology CO2 emissions', 'digital inclusive finance carbon emissions',
           'fintech carbon neutrality', 'digital financial inclusion carbon emissions', 'fintech greenhouse gas emissions', 'fintech carbon intensity']
def save(src, rows):
    p = os.path.join(RAW, f'records_{src}.jsonl')
    with open(p, 'w', encoding='utf-8') as f:
        for r in rows: f.write(json.dumps(r, ensure_ascii=False) + '\n')
    return len(rows)

def run_crossref():
    rows = {}
    for q in PHRASES:
        n = 0; tot = None
        for off in range(0, 300, 100):
            s, j = get('https://api.crossref.org/works', params={'query.bibliographic': q, 'rows': 100, 'offset': off, 'filter': 'from-pub-date:2015-01-01,type:journal-article',
                       'select': 'DOI,title,container-title,publisher,issued,type,abstract,author,URL,subject,ISSN'})
            if s != 200: break
            tot = j['message'].get('total-results')
            for it in j['message']['items']:
                d = (it.get('DOI') or '').lower()
                rows.setdefault(d, dict(source='crossref', doi=d, title=(it.get('title') or [''])[0], abstract=re.sub('<[^>]+>', '', it.get('abstract') or ''), year=(it.get('issued', {}).get('date-parts') or [[None]])[0][0],
                    venue=(it.get('container-title') or [''])[0], publisher=it.get('publisher'), type=it.get('type'), issn=';'.join(it.get('ISSN') or []), url=it.get('URL'), queries=[]))['queries'].append(q); n += 1
        log('crossref', q + ' [query.bibliographic, rows 300, from 2015, journal-article]', tot, n)
        print('crossref', q, n, flush=True)
    print('crossref unique', save('crossref', list(rows.values())))

def run_doaj():
    rows = {}
    for q in [CORE.replace('"', '"'), 'fintech AND (carbon OR emissions)', '"digital finance" AND (carbon OR emissions)', '"digital inclusive finance" AND (carbon OR emissions)']:
        n = 0; tot = None
        for page in range(1, 8):
            s, j = get('https://doaj.org/api/search/articles/' + requests.utils.quote(q), params={'pageSize': 100, 'page': page})
            if s != 200 or not j.get('results'): break
            tot = j.get('total')
            for it in j['results']:
                b = it['bibjson']; doi = next((i['id'] for i in b.get('identifier', []) if i['type'] == 'doi'), '').lower()
                key = doi or b.get('title', '')[:80].lower()
                y = b.get('year')
                if y and int(y) < 2015: continue
                rows.setdefault(key, dict(source='doaj', doi=doi, title=b.get('title'), abstract=b.get('abstract', ''), year=int(y) if y else None, venue=b.get('journal', {}).get('title'),
                    publisher=b.get('journal', {}).get('publisher'), type='journal-article', issn=';'.join(b.get('journal', {}).get('issns', [])), url=next((l['url'] for l in b.get('link', [])), None), queries=[]))['queries'].append(q); n += 1
            if len(j['results']) < 100: break
        log('doaj', q + ' [DOAJ article search, from 2015 by filter in script]', tot, n)
        print('doaj', q[:50], tot, n, flush=True)
    print('doaj unique', save('doaj', list(rows.values())))

def run_s2():
    rows = {}
    for q in PHRASES[:5]:
        n = 0
        for off in (0, 100, 200):
            s, j = get('https://api.semanticscholar.org/graph/v1/paper/search', params={'query': q, 'limit': 100, 'offset': off, 'year': '2015-', 'fields': 'title,abstract,year,venue,publicationTypes,externalIds,openAccessPdf,isOpenAccess'}, tries=4)
            if s != 200 or not isinstance(j, dict): print('s2 fail', q, off, s); break
            for it in j.get('data', []):
                doi = ((it.get('externalIds') or {}).get('DOI') or '').lower(); key = doi or it['paperId']
                rows.setdefault(key, dict(source='semanticscholar', doi=doi, title=it.get('title'), abstract=it.get('abstract') or '', year=it.get('year'), venue=it.get('venue'), publisher=None,
                    type=','.join(it.get('publicationTypes') or []), issn='', url=(it.get('openAccessPdf') or {}).get('url'), queries=[]))['queries'].append(q); n += 1
            if len(j.get('data', [])) < 100: break
        log('semanticscholar', q + ' [paper/search, limit 100 x up to 3 pages, year 2015-]', '', n, 'rate limited: partial pages possible')
        print('s2', q, n, flush=True)
    print('s2 unique', save('semanticscholar', list(rows.values())))

def run_openalex():
    out = os.path.join(RAW, 'openalex'); os.makedirs(out, exist_ok=True)
    flt = f'title_and_abstract.search:{CORE},publication_year:2015-2026'
    sel = 'id,doi,title,publication_year,publication_date,type,language,abstract_inverted_index,primary_location,best_oa_location,locations,open_access,cited_by_count,authorships,referenced_works,keywords,primary_topic,biblio,is_retracted'
    page = 1; rows = []; tot = None
    while True:
        fp = os.path.join(out, f'page_{page}.json')
        if os.path.exists(fp): j = json.load(open(fp, encoding='utf-8'))
        else:
            while True:
                r = requests.get('https://api.openalex.org/works', params={'filter': flt, 'per-page': 200, 'page': page, 'select': sel}, headers={'User-Agent': 'ReproAuditResearch/1.0 (open-data research)'}, timeout=90)
                if r.status_code == 200: j = r.json(); json.dump(j, open(fp, 'w', encoding='utf-8')); break
                wait = int(r.headers.get('X-RateLimit-Reset', '600')) + 30 if r.status_code == 429 else 60
                print('openalex', r.status_code, 'waiting', wait, 's', flush=True); time.sleep(min(wait, 3600))
            time.sleep(1.0)
        tot = j['meta']['count']
        for w in j['results']:
            ab = ''
            if w.get('abstract_inverted_index'):
                pos = {}
                for k, ps in w['abstract_inverted_index'].items():
                    for p in ps: pos[p] = k
                ab = ' '.join(pos[k] for k in sorted(pos))
            loc = w.get('primary_location') or {}; src = loc.get('source') or {}; bo = w.get('best_oa_location') or {}
            rows.append(dict(source='openalex', doi=(w.get('doi') or '').replace('https://doi.org/', '').lower(), openalex_id=w['id'], title=w.get('title'), abstract=ab, year=w.get('publication_year'),
                venue=src.get('display_name'), publisher=src.get('host_organization_name'), type=w.get('type'), issn=src.get('issn_l') or '', url=bo.get('pdf_url') or bo.get('landing_page_url') or loc.get('landing_page_url'),
                oa_status=(w.get('open_access') or {}).get('oa_status'), cited_by=w.get('cited_by_count'), language=w.get('language'),
                first_author=(((w.get('authorships') or [{}])[0]).get('author') or {}).get('display_name'), queries=['core']))
        print('openalex page', page, len(j['results']), 'of', tot, flush=True)
        if len(j['results']) < 200 or page * 200 >= tot: break
        page += 1
    log('openalex', flt + ' [title_and_abstract.search]', tot, len(rows))
    print('openalex saved', save('openalex', rows))
if __name__ == '__main__':
    {'crossref': run_crossref, 'doaj': run_doaj, 's2': run_s2, 'openalex': run_openalex}[sys.argv[1]]()
