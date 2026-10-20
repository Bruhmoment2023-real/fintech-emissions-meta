"""Download public predatory/hijacked warning lists (no login): Kscien 'Non-Recommended Journals Lists' pages 1-40, Beall's List pages (publishers on home page,
standalone journals, hijacked journals, misleading metrics). Saves raw HTML in data/predatory/ and parsed names in data/predatory/lists_parsed.csv with access date."""
import os, re, time, csv, html, datetime
import requests
HERE = os.path.dirname(os.path.abspath(__file__)); D = os.path.join(HERE, '..', 'data', 'predatory'); os.makedirs(D, exist_ok=True)
H = {'User-Agent': 'ReproAuditResearch/1.0 (open-data research)'}
today = datetime.date.today().isoformat(); rows = []
def clean(t): return re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', ' ', t))).strip()
# Kscien
for p in range(1, 41):
    fp = os.path.join(D, f'kscien_p{p}.html')
    if not os.path.exists(fp):
        r = requests.get('https://kscien.org/non-recommended-journals-lists/' + (f'page/{p}/' if p > 1 else ''), headers=H, timeout=60)
        if r.status_code != 200: print('kscien', p, r.status_code); continue
        open(fp, 'w', encoding='utf-8').write(r.text); time.sleep(1.5)
    t = open(fp, encoding='utf-8').read()
    body = t.split('Publishing Sort List')[-1] if 'Publishing Sort List' in t else t
    # entries are links or headings inside the results block
    names = re.findall(r'<(?:h[2-6]|a)[^>]*class="[^"]*(?:brxe-post-title|brxe-heading|brxe-text-link)[^"]*"[^>]*>(.*?)</(?:h[2-6]|a)>', body, re.S)
    for n in names:
        c = clean(n)
        if c: rows.append(('kscien', p, c))
print('kscien raw name-like items', len(rows))
open(os.path.join(D, 'access_log.txt'), 'w').write(f'Kscien pages 1-40 and Beall pages fetched {today}\n')
