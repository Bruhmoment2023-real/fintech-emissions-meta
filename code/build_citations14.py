"""Builds depth/citations/references.bib and references.ris from Crossref's own BibTeX/RIS transforms (no hand-typed fields).
DOI sources: the 55 included studies (extraction/studies.csv), method sources and the two closest prior syntheses found by code/priorwork14.py."""
import sys, os, csv, re
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE); os.chdir(HERE)
from netcache import get
dois = {}
def add(d, why): dois.setdefault(d.lower(), set()).add(why)
for r in csv.DictReader(open('../extraction/studies.csv', encoding='utf-8')): add(r['study_id'], 'included study in the meta-analysis')
for d, w in [('10.18637/jss.v036.i03', 'metafor (Viechtbauer 2010)'), ('10.1136/bmj.n71', 'PRISMA 2020 statement'), ('10.1002/jrsm.1095', 'PET-PEESE (Stanley and Doucouliagos, Res Synth Methods)'),
             ('10.1136/bmj.315.7109.629', 'Egger test (Egger et al. 1997)'), ('10.1080/07350015.2016.1247004', 'small-sample cluster-robust variance estimation CR2 (clubSandwich package; Pustejovsky and Tipton)'),
             ('10.1111/joes.12008', 'MAER-Net reporting guidelines for meta-analysis of economics research (Stanley et al.)'), ('10.1111/ecoj.12461', 'Power of bias in economics research (Ioannidis, Stanley, Doucouliagos)'),
             ('10.1007/s11356-020-07641-7', 'closest prior meta-regression: financial development and emissions (metadata only, closed access)'),
             ('10.1007/s43546-026-01083-y', 'closest prior synthesis: financial inclusion and emissions (metadata only, closed access)')]: add(d, w)
bib, ris, fail = [], [], []
for d in sorted(dois):
    s1, b = get('https://api.crossref.org/works/' + d + '/transform/application/x-bibtex', as_json=False)
    s2, r = get('https://api.crossref.org/works/' + d + '/transform/application/x-research-info-systems', as_json=False)
    if s1 == 200 and isinstance(b, str) and b.strip().startswith('@'):
        b = b.strip(); b = b[:-1].rstrip() + ',\n  note = {' + '; '.join(sorted(dois[d])) + '; metadata from Crossref}\n}' if b.endswith('}') else b
        bib.append(b)
    else: fail.append((d, s1))
    if s2 == 200 and isinstance(r, str) and 'TY  -' in r: ris.append(r.strip())
os.makedirs('../depth/citations', exist_ok=True)
open('../depth/citations/references.bib', 'w', encoding='utf-8').write('\n\n'.join(bib) + '\n')
open('../depth/citations/references.ris', 'w', encoding='utf-8').write('\n\n'.join(ris) + '\n')
open('../depth/citations/README.md', 'w', encoding='utf-8').write(f"""# Citation library (pack 14)
- `references.bib` ({len(bib)} entries) and `references.ris` ({len(ris)} entries), built from Crossref's BibTeX and RIS transforms by `code/build_citations14.py`; every BibTeX entry carries a `note` saying why it is in the pack. {len(dois)} unique DOIs requested.
- Scope: the {len(dois) - 9} included studies, seven method sources (metafor, PRISMA 2020, PET-PEESE, Egger, CR2 cluster-robust variance, MAER-Net guidelines, power of bias) and the two closest prior syntheses (metadata only; both are closed access).
- DOIs for which Crossref returned no BibTeX: {fail}.
- Import into Zotero: File > Import and choose `references.ris` (or `references.bib`). Check titles after import; Crossref sometimes keeps HTML entities.
""")
print(len(bib), len(ris), len(dois), fail)
