"""Print the abstract region and a few key sentences (data, sample, limitation) of an extracted full text, with PDF page numbers, to choose verbatim quotes for reading notes.
Usage: python excerpt.py <doi> [chars=1600]"""
import re, sys, os
HERE = os.path.dirname(os.path.abspath(__file__))
doi = sys.argv[1]; n = int(sys.argv[2]) if len(sys.argv) > 2 else 1600
safe = re.sub(r'[^a-z0-9]+', '_', doi.lower()).strip('_')
t = open(os.path.join(HERE, '..', 'data', 'fulltext', safe + '.txt'), encoding='utf-8', errors='replace').read()
parts = re.split(r'=====PAGE (\d+)=====', t)
pages = {int(parts[i]): parts[i + 1] for i in range(1, len(parts), 2)} if len(parts) > 1 else {0: t}
print('#### ', doi, 'pages', len(pages), 'chars', len(t))
first = pages[min(pages)]
m = re.search(r'abstract', first, re.I); s = m.start() if m else 0
print(re.sub(r'\s+', ' ', first[s:s + n]))
print('--- key sentences')
pat = re.compile(r'(limitation|future research|data (are|were) (obtained|collected|from)|we (use|employ|select|collect)\w* .{0,60}(panel|sample|data)|our sample|sample (period|covers)|endogene|robust(ness)?)', re.I)
seen = 0
for pg, tx in pages.items():
    flat = re.sub(r'\s+', ' ', tx)
    for sent in re.split(r'(?<=[.;]) ', flat):
        if 60 < len(sent) < 330 and pat.search(sent) and seen < 9 and re.search(r'limitation|future|sample|collect|obtained', sent, re.I):
            print(f'[p{pg}]', sent); seen += 1
