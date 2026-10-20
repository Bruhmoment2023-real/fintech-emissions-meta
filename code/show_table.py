"""Show the first table blocks of a full text that contain a fintech-type variable with a coefficient. Handles pypdf-flat rows and PyMuPDF one-cell-per-line tables.
Usage: python show_table.py <safe_doi> [blocks=2] [lines=40]"""
import re, sys, os
HERE = os.path.dirname(os.path.abspath(__file__))
name = sys.argv[1]; nb = int(sys.argv[2]) if len(sys.argv) > 2 else 2; nl = int(sys.argv[3]) if len(sys.argv) > 3 else 40
L = open(os.path.join(HERE, '..', 'data', 'fulltext', name + '.txt'), encoding='utf-8', errors='replace').read().split('\n')
fin = re.compile(r'fintech|fin-tech|financial technolog|digital (inclusive )?financ|\bDIF\b|\bDFI\b|\bDF\b|\bFT\b|\bFin\b|\bFINT\w*|\bDIFI\b|\bDFII?\b|\bIDF\b|\bDIFI\w*|index of digital|mobile payment|\bFTI\b|\bFTD\b|\bFD\b|ln\s?DIF|lnDF|\bDIFIN\b|\bDFA\b|\bFTech\b|\bFinTech', re.I)
num = re.compile(r'[-−‒–]?\d+\.\d{2,6}')
cap = re.compile(r'^\s*(Table|TABLE)\s*[A-Z]?\d+')
def coefline(i):
    l = L[i]
    if not fin.search(l[:26]): return False
    window = ' '.join(L[i:i + 5])
    return len(num.findall(window)) >= 1 and bool(re.search(r'\*|\(\s*[-−‒]?\d|\[\s*[-−‒]?\d', window)) and not re.search(r'granger|cause|descriptive|mean|std', l, re.I) and len(l) < 260
def compact(lines):
    rows = []; cur = ''
    for x in lines:
        x = x.strip().replace('​', '')
        if not x: continue
        newrow = bool(re.match(r'^[A-Za-z_][A-Za-z0-9_ ./&-]*$', x)) and not re.match(r'^[*]+$', x)
        if newrow and cur: rows.append(cur); cur = x
        else: cur = (cur + ' ' + x).strip()
    if cur: rows.append(cur)
    return rows
shown = []; done_to = -1
for i in range(len(L)):
    if i <= done_to: continue
    if coefline(i):
        j = i
        while j > 0 and not cap.match(L[j]) and i - j < 90: j -= 1
        start = j if cap.match(L[j]) else max(0, i - 12)
        print(f'--- block from line {start} (hit at {i}) ---')
        for r in compact(L[start:start + nl * 3])[:nl]: print(r[:240])
        done_to = start + nl * 3; shown.append(i)
        if len(shown) >= nb: break
if not shown: print('NO COEFFICIENT-LIKE FINTECH LINES')
