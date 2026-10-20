"""Retrieve open full texts for records in screening/fulltext_queue.csv (columns: doi, openalex_id optional, pdf_url optional, landing optional).
Routes, in order, each a plain GET with an honest user agent; a 403/Cloudflare block is logged and the next legitimate route tried (no evasion of blocks):
 1 Europe PMC full-text XML (via DOI lookup)    2 Springer content PDF (OA articles)    3 nature.com PDF    4 MDPI article PDF on MDPI's file CDN (mdpi.com itself returns 403 to scripts)
 5 URLs from OpenAlex locations (publisher or repository PDF)    6 arXiv/Zenodo/Research Square if present among OpenAlex locations
PDFs -> E:\\Research-Staging\\14-fintech-emissions-meta\\pdfs\\ ; extracted text -> data/fulltext/<safe_doi>.txt ; log -> data/fulltext_log.csv. Resumable."""
import os, re, sys, csv, json, time, html
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from netcache import get
import requests
from pypdf import PdfReader
STAGE = 'E:/Research-Staging/14-fintech-emissions-meta/pdfs/'; os.makedirs(STAGE, exist_ok=True)
TXT = os.path.join(HERE, '..', 'data', 'fulltext'); os.makedirs(TXT, exist_ok=True)
LOGF = os.path.join(HERE, '..', 'data', 'fulltext_log.csv')
H = {'User-Agent': 'ReproAuditResearch/1.0 (open-data research; contact via repository)'}
MDPI_SLUG = {'su': 'sustainability', 'en': 'energies', 'ijerph': 'ijerph', 'jrfm': 'jrfm', 'admsci': 'admsci', 'economies': 'economies', 'land': 'land', 'systems': 'systems', 'fintech': 'fintech', 'ijfs': 'ijfs',
             'risks': 'risks', 'math': 'mathematics', 'ijgi': 'ijgi', 'agriculture': 'agriculture', 'atmosphere': 'atmosphere', 'buildings': 'buildings', 'w': 'water', 'f': 'forests', 'app': 'applsci', 'electronics': 'electronics',
             'energies': 'energies', 'sustainability': 'sustainability', 'mathematics': 'mathematics', 'entropy': 'entropy', 'ijms': 'ijms', 'cli': 'climate', 'urbansci': 'urbansci', 'resources': 'resources', 'sensors': 'sensors',
             'jtaer': 'jtaer', 'jopen': 'joitmc', 'joitmc': 'joitmc', 'ijerph ': 'ijerph', 'foods': 'foods', 'smartcities': 'smartcities', 'data': 'data', 'information': 'information', 'logistics': 'logistics', 'commodities': 'commodities'}
def safe(d): return re.sub(r'[^a-z0-9]+', '_', d.lower()).strip('_')
def pdf_to_text(path):
    rd = PdfReader(path); t = ''
    for i, p in enumerate(rd.pages): t += f'\n\n=====PAGE {i+1}=====\n' + (p.extract_text() or '')
    return t, len(rd.pages)
def try_pdf(url, name):
    try:
        r = requests.get(url, headers=H, timeout=90, allow_redirects=True)
    except Exception as e: return 0, 'err ' + str(e)[:40]
    if r.content[:4] == b'%PDF':
        fp = STAGE + name + '.pdf'; open(fp, 'wb').write(r.content)
        try:
            t, n = pdf_to_text(fp); open(os.path.join(TXT, name + '.txt'), 'w', encoding='utf-8').write(t); return 200, f'pdf {n} pages'
        except Exception as e: return 200, 'pdf unreadable ' + str(e)[:40]
    return r.status_code, 'not pdf'
def epmc(doi, name):
    try:
        j = requests.get('https://www.ebi.ac.uk/europepmc/webservices/rest/search', params={'query': f'DOI:"{doi}"', 'format': 'json', 'resultType': 'lite'}, headers=H, timeout=60).json()
        res = j['resultList']['result']
        if not res or not res[0].get('pmcid'): return 404, 'no PMC record'
        x = requests.get(f"https://www.ebi.ac.uk/europepmc/webservices/rest/{res[0]['pmcid']}/fullTextXML", headers=H, timeout=90)
        if x.status_code != 200 or len(x.text) < 5000: return x.status_code, 'no OA xml'
        z = re.sub(r'</(p|title|tr|sec|label|caption)>', '\n', x.text); z = re.sub(r'</t[dh]>', ' | ', z); z = re.sub(r'<[^>]+>', '', z)
        open(os.path.join(TXT, name + '.txt'), 'w', encoding='utf-8').write('=====PAGE 0=====\n' + html.unescape(z)); return 200, 'epmc ' + res[0]['pmcid']
    except Exception as e: return 0, 'err ' + str(e)[:40]
def routes(doi, locs):
    r = [('epmc', None)]
    if doi.startswith('10.1007/') or doi.startswith('10.1186/') or doi.startswith('10.1057/') or doi.startswith('10.1038/s41599') or doi.startswith('10.1007'):
        r.append(('springer', f'https://link.springer.com/content/pdf/{doi}.pdf'))
    if doi.startswith('10.1038/'): r.append(('nature', f"https://www.nature.com/articles/{doi.split('/')[1]}.pdf"))
    m = re.match(r'10\.3390/([a-z]+?)(\d{2})(\d{1,2})(\d{4,5})$', doi)
    if m:
        code, vol, iss, art = m.groups(); slug = MDPI_SLUG.get(code)
        if slug: r.append(('mdpi-cdn', f'https://mdpi-res.com/d_attachment/{slug}/{slug if slug != "jrfm" else "jrfm"}-{int(vol)}-{int(art):05d}/article_deploy/{slug}-{int(vol)}-{int(art):05d}.pdf'))
    m2 = re.match(r'10\.3390/([a-z]+)(\d{1,2})(\d{2})(\d{4,5})$', doi)
    for u in locs: r.append(('openalex-loc', u))
    return r
def main(queue):
    done = {}
    if os.path.exists(LOGF): done = {r['doi']: r for r in csv.DictReader(open(LOGF, encoding='utf-8'))}
    out = list(done.values())
    for row in csv.DictReader(open(queue, encoding='utf-8')):
        doi = row['doi'].lower()
        if doi in done: continue
        name = safe(doi); locs = [u for u in (row.get('pdf_url'), ) if u] + [u for u in (row.get('locs') or '').split('|') if u]
        status = 'none'; route = ''; note = ''
        for rt, url in routes(doi, locs):
            if rt == 'epmc': c, n = epmc(doi, name)
            else: c, n = try_pdf(url, name)
            note += f'{rt}:{c}:{n}; '
            if (rt == 'epmc' and c == 200) or n.startswith('pdf '): status, route = 'ok', rt; break
            time.sleep(0.5)
        out = [o for o in out if o['doi'] != doi]; out.append(dict(doi=doi, status=status, route=route, note=note[:400]))
        print(doi, status, route, flush=True)
        w = csv.DictWriter(open(LOGF, 'w', newline='', encoding='utf-8'), fieldnames=['doi', 'status', 'route', 'note']); w.writeheader(); w.writerows(out)
if __name__ == '__main__': main(sys.argv[1])
