# 02 Design (pointer and additions)

The full protocol, written before screening and hashed, is `02a-PROTOCOL.md` (SHA-256 in `02a-PROTOCOL.sha256`). Later clarifications are in `02b-PROTOCOL-AMENDMENTS.md` (none are allowed to change a decision after results were seen without being listed there).

## Research question and hypotheses
See protocol section 1: pooled partial correlation of fintech on emissions (H1 negative), publication selection (H2 bias-corrected effect smaller in absolute size), heterogeneity (H3 I-squared above 75 percent).

## Data sources, licences, access dates (all 17 Oct 2026 unless stated)
- OpenAlex works API (CC0), title-and-abstract search; run after the daily quota reset (see `data/raw/search_log.csv`).
- Crossref REST (metadata free to reuse), Semantic Scholar Graph API (API licence), DOAJ article search API (metadata CC BY-SA).
- RePEc/IDEAS and EconPapers: only searchable by POSTing the site's search form; not done because the working rules forbid form submissions.
- Open full texts: Europe PMC open-access XML, publisher open-access PDFs (Springer, Nature, MDPI file CDN, Frontiers, PLOS, Wiley/Elsevier only where not blocked), repositories. Elsevier and Wiley sites returned HTTP 403 to scripted requests; nothing was fetched through them.
- Warning lists for venue quality: Kscien "Non-Recommended Journals Lists" (pages 1-40) and Beall's List (publishers on the home page, standalone journals, hijacked journals), fetched 17 Oct 2026 into `data/predatory/`. Beall's publisher and journal lists are 2016-2017 snapshots (the pages carry "Last updated" dates in 2016) and its hijacked list was updated in 2024; Kscien is a volunteer list. Flags are leads to inspect, not verdicts.
- Software: R 4.5.3 with metafor 5.2.1 and clubSandwich 0.7.0 in `D:\Research-Publishing\_tools\R-lib`; Python 3.12 venv in `_tools\biblio-venv`.

## Analysis plan
Protocol section 6. R script `code/meta_analysis.R` (tested on simulated data before any real estimate existed; the simulated file lives outside the pack).

## Threats to validity (in addition to protocol section 10)
- Retracted papers and retraction notices were found in the corpus (12 stage-1 exclusions coded E8 and 2 full-text exclusions coded X6); they are excluded and listed in the screening logs.
- Studies by the same teams on the same Chinese panels (the Peking University Digital Financial Inclusion Index, 2011 onward) overlap in data; the cluster-robust model and the overlap flag address this only partly.
- The partial correlation uses reported t-statistics and sample sizes; a few studies report no number of regressors (imputed).
- Open full text requirement: the extractable set is not a random sample of the literature.
