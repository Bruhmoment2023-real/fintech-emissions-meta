"""Print extraction hints for one opened full text (data/fulltext/<name>.txt): dependent-variable lines, sample-size lines, and table lines that contain a fintech-type
variable next to coefficient-like numbers. Usage: python extract_helper.py <safe_doi> [maxsnips]. I read the output and code estimates by hand into extraction/estimates.csv."""
import re, sys, os
HERE = os.path.dirname(os.path.abspath(__file__))
name = sys.argv[1]; mx = int(sys.argv[2]) if len(sys.argv) > 2 else 14
t = open(os.path.join(HERE, '..', 'data', 'fulltext', name + '.txt'), encoding='utf-8', errors='replace').read()
pages = re.split(r'=====PAGE (\d+)=====', t); P = {}
for i in range(1, len(pages), 2): P[int(pages[i])] = pages[i + 1]
fin = re.compile(r'fintech|fin-tech|financial technolog|digital (inclusive )?financ|\bDIF\b|\bDFI\b|\bDF\b|\bFT\b|\bFin\b|\bFINT\w*|inclusive finance|mobile payment|digital financial inclusion|DIFI|index of digital', re.I)
num = re.compile(r'[-−–]?\d+\.\d{2,5}\s*(\*{1,3})?')
dep = re.compile(r'dependent variable|explained variable|outcome variable|response variable|carbon (emission|intensity)|CO2', re.I)
smp = re.compile(r'observations|\bobs\b|\bN\s*=|sample (period|size|covers|consists)|panel of|from \d{4} to \d{4}|\d{4}\s*[-–]\s*\d{4}|provinces|prefecture|cities|countries', re.I)
print('FILE', name, 'pages', len(P))
c = 0
for pg, tx in sorted(P.items()):
    for l in tx.split('\n'):
        if re.search(r'dependent variable|explained variable', l, re.I) and c < 4: print(f'[DEP p{pg}]', l.strip()[:200]); c += 1
c = 0
for pg, tx in sorted(P.items()):
    for l in tx.split('\n'):
        if re.search(r'\b(observations|obs\.?|N)\b\s*[=:]?\s*\d|\d[\d,]{2,}\s*(observations|obs)', l, re.I) and c < 6: print(f'[N p{pg}]', l.strip()[:160]); c += 1
c = 0
for pg, tx in sorted(P.items()):
    lines = tx.split('\n')
    for i, l in enumerate(lines):
        if fin.search(l) and num.search(l) and c < mx:
            print(f'[TAB p{pg}]', l.strip()[:170], '||', (lines[i + 1].strip()[:90] if i + 1 < len(lines) else '')); c += 1
