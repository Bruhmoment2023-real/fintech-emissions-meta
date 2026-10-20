"""Copy legal open-access PDFs already fetched for included studies (E:\\Research-Staging\\...\\pdfs) into bibliometrics/pdfs for the core set: the included studies with the most local
citations in the corpus, up to 28 files and 300 MB. Europe PMC texts have no PDF and are skipped. Writes pdfs/pdf-download-log.csv (appends to what evidence.py pdfs wrote)."""
import os, re, shutil, csv
import pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); PACK = os.path.dirname(HERE)
SRC = 'E:/Research-Staging/14-fintech-emissions-meta/pdfs/'; DST = os.path.join(PACK, 'bibliometrics', 'pdfs'); os.makedirs(DST, exist_ok=True)
m = pd.read_csv(os.path.join(PACK, 'bibliometrics', 'data', 'clean', 'master.csv'), dtype=str, encoding='utf-8-sig').fillna('')
st = pd.read_csv(os.path.join(PACK, 'extraction', 'studies.csv'), dtype=str)
m['d'] = m.doi.str.lower(); m['lc'] = pd.to_numeric(m.local_citations, errors='coerce').fillna(0)
m = m[m.d.isin(set(st.study_id))].sort_values('lc', ascending=False)
rows = []; total = 0; n = 0
for _, r in m.iterrows():
    safe = re.sub(r'[^a-z0-9]+', '_', r.d).strip('_'); f = SRC + safe + '.pdf'
    if not os.path.exists(f): continue
    sz = os.path.getsize(f)
    if n >= 28 or total + sz > 300 * 1024 * 1024: break
    fa = re.sub(r'[^A-Za-z]', '', (r.authors.split(';')[0].strip().split(' ') or ['x'])[-1])[:20] or 'anon'
    fn = f'C{n+1:02d}_{fa}_{r.year}_{safe[:40]}.pdf'; shutil.copy(f, os.path.join(DST, fn)); total += sz; n += 1
    rows.append([n, r.title, fn, 'copied from the open full texts fetched for extraction (publisher or repository open access)', r.doi, sz])
with open(os.path.join(DST, 'pdf-copy-log.csv'), 'w', newline='', encoding='utf-8-sig') as fh:
    w = csv.writer(fh); w.writerow(['n', 'title', 'file', 'status', 'doi', 'bytes']); w.writerows(rows)
print('copied', n, round(total / 1e6, 1), 'MB')
