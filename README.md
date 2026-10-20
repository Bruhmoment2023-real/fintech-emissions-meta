# Does fintech go with lower carbon emissions? A systematic review and meta-analysis of regression estimates

Sean Solano Paul, Independent researcher, Bengaluru, India. Funding: none. Competing interests: none.

## Summary

A fast-growing literature, mostly from China since 2021, reports that fintech and digital finance reduce carbon emissions. This repository contains the protocol (written and SHA-256 hashed before screening, with amendments), the screening log, the dataset of 91 main-table regression estimates from 55 studies (each checked against its source table and converted to partial correlations), the meta-analysis code (R, metafor and clubSandwich) and the results. Searches covered OpenAlex, Crossref, DOAJ and Semantic Scholar (3,585 unique records); 117 open full texts were read. The pre-specified pooled partial correlation was r = -0.151 (95% CI -0.227 to -0.073), with extreme heterogeneity and signs of small-study effects.

## Repository layout

```
docs/            protocol (02a-PROTOCOL.md + .sha256), amendments, design, prior-work review, data dictionary, rerun script, citations
code/            search, screening, extraction-verification, effect-size and meta-analysis scripts (meta_analysis.R)
extraction/      estimates.csv (analysis-ready), estimates_raw.csv (as hand-coded), studies.csv, entries/ (coded entry file)
screening/       screening log: stage-0 rule exclusions, stage-1 decisions, stage-2 full-text decisions, queues, double-screen sample
data/            venue_flags.csv, search_log.csv, build log
results/         pooled estimates, leave-one-out, meta-regression, publication-bias tests, figures F0-F3, logs, RESULTS-SUMMARY.md
bibliometrics/   literature map: scripts (Python and R), tables, figures, VOSviewer files, search protocol, gap analysis
```

## How to reproduce

- Python 3.12 (`pip install -r requirements.txt`) and R 4.5 with `metafor` 5.2.1 and `clubSandwich` 0.7.0. The bibliometrics scripts also use `bibliometrix`, `igraph`, `Matrix`, `data.table`, `jsonlite`, `ggplot2`, `dplyr`, `tidyr`, `stringr`, `ggrepel`.
- Order (see `docs/appendix/rerun.ps1`): `code/build_estimates.py` (verifies each hand-coded entry against the full text and builds the analysis file), `code/build_studies.py`, then from `code/`: `Rscript meta_analysis.R ../extraction/estimates.csv ../results/`, then `prisma14.py` and `venue_flags_all.py`. Four extra Table 3 sensitivity rows (same 34 studies with standard df, China only, outside China, clustered) come from `code/sensitivity_extra.py` (standard library only), run from the repo root as `python -I code/sensitivity_extra.py results/tables/estimates_with_effect_sizes.csv`; its saved output is `results/sensitivity_extra_output.txt`.
- The scripts were written against a working tree rooted at `D:\Research-Publishing\14-fintech-emissions-meta`; adjust the root paths at the top of the scripts. Steps that verify entries against full text need the full texts, which are not redistributed (fetch them with `code/fetch_fulltext.py` from `screening/fulltext_queue.csv`); `extraction/estimates.csv` and the R step run without them.
- Search and download steps (`search14.py`, `fetch_fulltext.py`) use public APIs and are rate-limited.

## Data sources and licences

| Source | Used for | Terms |
|---|---|---|
| OpenAlex, Crossref, DOAJ, Semantic Scholar APIs | search and screening metadata (titles, DOIs, venues, years) | open metadata; abstracts removed from the released corpus |
| 55 included studies | regression coefficients, standard errors, sample sizes transcribed with table/page pointers | publisher/author copyright in the papers; only numbers and pointers released |
| Beall's List archive, Kscien non-recommended lists | venue warning flags (`data/venue_flags.csv`) | third-party lists, parsed by code; pages not redistributed |

No Scopus or Web of Science data were used; the search strings in `bibliometrics/scopus-queries.md` were not run.

## Not included and why

- Full-text PDFs and extracted full text of the papers (copyright): obtain via the DOIs in `screening/` and `extraction/studies.csv`.
- Raw API responses, HTTP cache and fetched warning-list web pages (`data/raw/`, `data/cache/`, `data/predatory/`): regenerate with `search14.py` and `fetch_warning_lists.py`.
- Large candidate tables (`data/clean/candidates.csv`, abstract enrichment) and bibliometrix R-object snapshots (`.rds`): regenerate with the scripts.
- Abstract column of the bibliographic corpus (`master.csv`) and abstract sentences in the evidence table; per-paper reading notes (they contain quotations); bundled HTML-widget libraries and interactive HTML figures (PNG/SVG versions are included).
- The 28 PDFs in the source `bibliometrics/pdfs/` folder.

## Citation

Solano Paul, S. (2026). Does fintech go with lower carbon emissions? A systematic review and meta-analysis of regression estimates. Code and data repository. See `CITATION.cff`. A Zenodo DOI will be added when the repository is made public.

## Licences

Code: MIT (`LICENSE`). Author-derived data, results and figures: CC BY 4.0 (`LICENSE-DATA.md`). Third-party source data keep their own terms.
