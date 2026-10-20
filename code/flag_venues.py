"""Match each included study's venue and publisher against the parsed warning lists (Kscien non-recommended list, Beall's standalone journals and publishers, Beall's hijacked journals).
A match is exact on the normalised name, or difflib ratio >= 0.93 for names of 12+ characters; every match is printed for hand verification. Output: data/venue_flags.csv.
Warning-list membership is a flag to look at, not a verdict: Beall's list is a 2016-2017 snapshot for publishers/journals, Kscien is a volunteer list."""
import os, re, sys, csv, unicodedata, html, difflib
import pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); os.chdir(HERE)
def norm(s): return re.sub(r'[^a-z0-9]+', ' ', unicodedata.normalize('NFKD', html.unescape(str(s)).lower())).strip()
L = pd.read_csv('../data/predatory/lists_parsed.csv', dtype=str)
names = {}
for _, r in L.iterrows(): names.setdefault(r['normalised'], []).append(r['list'])
byfirst = {}
for n in names: byfirst.setdefault(n[:1], []).append(n)
def match(x):
    n = norm(x)
    if not n or len(n) < 6: return None
    if n in names: return (n, 'exact', names[n])
    if len(n) >= 12:
        best = max(((difflib.SequenceMatcher(None, n, c).ratio(), c) for c in byfirst.get(n[:1], [])), default=(0, ''))
        if best[0] >= 0.93: return (best[1], f'fuzzy {best[0]:.2f}', names[best[1]])
    return None
if __name__ == '__main__':
    inp = sys.argv[1] if len(sys.argv) > 1 else '../extraction/studies.csv'
    d = pd.read_csv(inp, dtype=str)
    out = []
    for _, r in d.iterrows():
        mv = match(r.get('venue', '')); mp = match(r.get('publisher', ''))
        out.append(dict(study_id=r.get('study_id', r.get('doi')), venue=r.get('venue'), publisher=r.get('publisher'), venue_match=str(mv) if mv else '', publisher_match=str(mp) if mp else ''))
    o = pd.DataFrame(out); o.to_csv('../data/venue_flags.csv', index=False)
    print(len(o), 'venues checked;', (o.venue_match != '').sum(), 'venue matches;', (o.publisher_match != '').sum(), 'publisher matches')
    print(o[(o.venue_match != '') | (o.publisher_match != '')].to_string())
