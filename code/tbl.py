"""Print table captions or one table compactly. Usage: python tbl.py <safe_doi> list | python tbl.py <safe_doi> <N> [rows=45] [occurrence=last]
Finds lines starting 'Table N' (not followed by a sentence verb such as 'shows/reports/presents'), prints the next lines with one-cell-per-line tables joined into rows."""
import re, sys, os
HERE = os.path.dirname(os.path.abspath(__file__))
name = sys.argv[1]; what = sys.argv[2]; nr = int(sys.argv[3]) if len(sys.argv) > 3 else 45
L = open(os.path.join(HERE, '..', 'data', 'fulltext', name + '.txt'), encoding='utf-8', errors='replace').read().split('\n')
def compact(lines):
    rows = []; cur = ''
    for x in lines:
        x = x.strip().replace('​', '')
        if not x: continue
        newrow = bool(re.match(r'^[A-Za-z_À-ſ][A-Za-z0-9_ ./&-]{0,38}$', x)) and not re.match(r'^[*]+$', x)
        if newrow and cur: rows.append(cur); cur = x
        else: cur = (cur + ' ' + x).strip()
    if cur: rows.append(cur)
    return rows
capre = re.compile(r'^\s*(Table|TABLE)\s*([A-Z]?\d+)\b[.:]?\s*(.*)$')
caps = [(i, m.group(2), m.group(3)) for i, l in enumerate(L) if (m := capre.match(l)) and not re.match(r'(shows|reports|presents|displays|lists|summar|provides|is |are |reveals|indicates)', m.group(3), re.I)]
if what == 'list':
    for i, n, t in caps: print(i, 'T' + n, t[:110])
else:
    c = [x for x in caps if x[1] == what]
    if not c: print('no such table; captions:', [x[1] for x in caps]); sys.exit()
    i = c[-1][0] if len(sys.argv) <= 4 or sys.argv[4] == 'last' else c[0][0]
    for r in compact(L[i:i + nr * 4])[:nr]: print(r[:250])
