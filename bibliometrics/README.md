# Literature map, pack 14 (fintech, digital finance and carbon emissions)

Corpus: 972 records, 2016 to 2026 (almost all 2021 onward), OpenAlex-led, pulled 16 to 17 Oct 2026; 460 sources, 1,926 authors (`tables/OA01_main_information.csv`). No Scopus or Web of Science data: none supplied, none run (strings in `scopus-queries.md`).

## Contents
- `search-protocol.md` strings, dates, rules, counts, limits. `scopus-queries.md` Scopus and WoS strings (not run). `gap-analysis.md` bullets and five papers to read first.
- `data/clean/` `master.csv` (cleaned corpus), `references.csv`, `M.rds` (Bibliometrix frame), `search_counts.json`; `data/p2_build.log`, `data/bibliometrix_run.log`.
- `R/` scripts `01_build_M.R`, `02_bibliometrix.R`, `common.R`; `tables/OA*.csv` and `figures/OA*.png` (main information, annual production, citations per year, sources and Bradford, source dynamics, authors and Lotka, affiliations, countries and collaboration map, local and global cited documents and references, RPYS, keywords, word cloud, treemap, trend topics, co-occurrence network, thematic map and evolution, co-citation, bibliographic coupling, historiograph, collaboration networks, three-field plot).
- `python/` `p2_build_master.py`, `figures_py.py` (P01 interactive citation network HTML, P02 timeline, P03 year by sub-literature, P04 coverage heat map, P05 main path), `vosviewer_export.py`, `evidence.py`, `make_docs.py` (not used; its template did not fit this corpus, captions and protocol were composed separately).
- `network/` Kleinberg bursts and main-path analysis (`code/network_depth14.py`): `keyword_bursts.csv`, `main_path_papers.csv`, `key_route_papers.csv`, `network_summary.json`, with figures `N01`, `N02` in `figures/`.
- `vosviewer/` map and network files for co-authorship, keyword co-occurrence, direct citation, bibliographic coupling and co-citation of references (open in VOSviewer with File, Open, VOSviewer map file and the matching network file; VOSviewer itself was not rendered here).
- `evidence-table.csv` 50 papers (ranked by keyword relevance and local citations). Of these, 8 are in the meta-analysis and 4 were excluded at full text; 24 passed screening but have no open full text; 13 were excluded at title and abstract. "Main finding" cells are sentences copied from abstracts; 26 rows have no abstract (read status says so).
- `pdfs/` 30 open-access PDFs (28 of the included studies with most in-corpus citations, copied from the extraction downloads; 2 from `evidence.py pdfs`); `pdf-copy-log.csv`, `pdf-download-log.csv`. 38 MB.
- `figures/captions.md` captions for every figure (what, data and settings, caution).

## Regenerate
```
cd python
python p2_build_master.py            # needs the pack's data\raw and screening files; cached; about 35 minutes with rate limits
cd ..\R
Rscript 01_build_M.R
Rscript 02_bibliometrix.R M.rds OA ID "Fintech/digital finance and emissions literature, OpenAlex-led (972 records)" 2022,2024   # about 20 minutes
cd ..\python
python figures_py.py ; python vosviewer_export.py
cd ..\..\code
python make_evidence_notes.py ; python network_depth14.py ; python copy_core_pdfs.py
cd ..\bibliometrics\python ; python evidence.py
```
Python: `D:\Research-Publishing\_tools\biblio-venv`; R 4.5.3 with bibliometrix, packages in `D:\Research-Publishing\_tools\R-lib` (do not set R_LIBS_USER, it hides the default library where bibliometrix lives).

## Limits and fixes made
- Bibliometrix cites "at least twice" in its message; the build resolved references cited at least four times (1,165 of 1,166).
- `config.json` regular expressions had unescaped backslashes (invalid JSON); fixed by `code/fix_config_json.py`. `01_build_M.R` was changed to make short-reference keys unique (`make.unique`).
- The corpus mixes hand-screened records and 125 unscreened lexical hits; 16 records have an OpenAlex retraction flag; 30 SSRN and 17 Zenodo records may duplicate journal papers.
- OpenAlex keywords are algorithmic; 188 records lack an abstract. Reference lists exist for 625 records.
- Most top-ranked papers have no legal open copy found by script (publisher links returned 403 or none), so the PDF set is the included studies, not the top of the evidence table.
