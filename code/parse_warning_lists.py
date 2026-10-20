"""Parse saved Kscien and Beall pages into data/predatory/lists_parsed.csv (list, name, normalised). No judgement is made here."""
import os, re, csv, glob, html, unicodedata
D = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data', 'predatory')
def norm(s): return re.sub(r'[^a-z0-9]+', ' ', unicodedata.normalize('NFKD', html.unescape(s).lower())).strip()
rows = []
for f in sorted(glob.glob(D + '/kscien_p*.html'), key=lambda x: int(re.findall(r'_p(\d+)', x)[0])):
    t = open(f, encoding='utf-8').read()
    if 'Sorted by Date' not in t: continue
    body = t.split('Sorted by Date')[-1]
    txt = re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', '\n', body)))
    for part in txt.split('Visit Website')[:-1]:
        n = part.strip()
        if 3 < len(n) < 200: rows.append(('kscien_non_recommended', n))
for name, f in [('beall_standalone_journals', 'beall_standalone-journals.html'), ('beall_publishers', 'beall_home.html'), ('beall_hijacked_journals', 'beall_hijacked-journals.html')]:
    t = open(os.path.join(D, f), encoding='utf-8').read()
    for l in re.findall(r'<li[^>]*>(.*?)</li>', t, re.S):
        n = re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', ' ', l))).strip()
        if 3 < len(n) < 200: rows.append((name, n))
seen = set(); out = []
for l, n in rows:
    k = (l, norm(n))
    if k in seen or not norm(n): continue
    seen.add(k); out.append((l, n, norm(n)))
with open(D + '/lists_parsed.csv', 'w', newline='', encoding='utf-8') as f:
    w = csv.writer(f); w.writerow(['list', 'name', 'normalised']); w.writerows(out)
import collections; print(collections.Counter(l for l, _, _ in out))
