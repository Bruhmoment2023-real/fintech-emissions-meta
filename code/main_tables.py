"""Print the first candidate main-results tables (by caption keywords) of a text, plus sample-size hints. Usage: python main_tables.py <safe_doi> [n_tables=2] [rows=28]"""
import re, sys, os, subprocess
HERE = os.path.dirname(os.path.abspath(__file__)); name = sys.argv[1]; nt = int(sys.argv[2]) if len(sys.argv) > 2 else 2; nr = sys.argv[3] if len(sys.argv) > 3 else '28'
L = open(os.path.join(HERE, '..', 'data', 'fulltext', name + '.txt'), encoding='utf-8', errors='replace').read().split('\n')
capre = re.compile(r'^\s*(Table|TABLE)\s*([A-Z]?\d+)\b[.:]?\s*(.*)$')
good = re.compile(r'baseline|benchmark|regression|main (result|effect)|results of|impact|effect|estimat|panel|CS-?ARDL|ARDL|GMM|spatial|fixed', re.I)
bad = re.compile(r'descriptive|summary stat|unit root|VIF|correlation matrix|Hausman|Granger|robust|heterogene|mechanism|mediat|variables?\b.*(defin|descri)|cointegration|dependence|homogeneity|endogene|placebo|threshold|moderat', re.I)
picked = []
for i, l in enumerate(L):
    m = capre.match(l)
    if m and not re.match(r'(shows|reports|presents|displays|lists|summar|provides|is |are |reveals|indicates|above|below)', m.group(3), re.I):
        cap_text = m.group(3) + ' ' + ' '.join(L[i + 1:i + 3])
        if good.search(cap_text) and not bad.search(cap_text) and m.group(2) not in [p[1] for p in picked]: picked.append((i, m.group(2)))
print('FILE', name, '| candidate main tables:', [p[1] for p in picked][:6])
for i, n in picked[:nt]:
    print(f'===== Table {n} =====')
    r = subprocess.run([sys.executable, '-I', '-X', 'utf8', os.path.join(HERE, 'tbl.py'), name, n, nr], capture_output=True, text=True, encoding='utf-8'); print(r.stdout)
for l in L:
    if re.search(r'\b(Observations|Obs\.?|N)\b\s*[:=]?\s*[0-9,]{3,}|[0-9,]{3,}\s+(observations|city-year|province-year|firm-year|obs)', l, re.I):
        print('[N-hint]', l.strip()[:150]); break
