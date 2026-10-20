# Search protocol for the literature map (pack 14)

The systematic-review protocol (frozen before screening) is `../02a-PROTOCOL.md`; this file covers the literature map in this folder, which uses the same searches plus a wider corpus.

## 1 Databases and dates
- OpenAlex works API (primary), `title_and_abstract.search`, run 16 Oct 2026 23:13 UTC; 1,701 hits, 1,700 distinct works loaded.
- Crossref `query.bibliographic` (eight phrase queries, 300 rows each, journal articles from 2015), DOAJ article search (five strings), Semantic Scholar Graph API (rate limited: most queries returned nothing; partial). Exact strings, times and counts: `../data/raw/search_log.csv`.
- Not searched: RePEc/IDEAS and EconPapers (form POST needed), Scopus, Web of Science (no login); equivalent strings in `scopus-queries.md`. `scopus-drop\` was not provided, so no Scopus export was merged.

## 2 Core string (OpenAlex syntax)
`(fintech OR "fin-tech" OR "financial technology" OR "digital finance" OR "digital financial" OR "digital inclusive finance" OR "digital financial inclusion") AND (carbon OR CO2 OR emission OR emissions OR "greenhouse gas" OR decarbonization OR decarbonisation)`, publication years 2015 to 2026.

## 3 Sub-literatures (set by the stage-1 hand screen; priority R, then C, then O)
- C: empirical studies of fintech or digital finance and emissions (stage-1 include, or an unscreened hit with both a fintech and an emissions term in title or abstract).
- R: reviews and conceptual or non-empirical papers (stage-1 code E3, or "review", "bibliometric", "literature", "survey" in the title).
- O: fintech exposure with another outcome (energy, pollution, innovation, efficiency, ESG).

## 4 Corpus rule and cleaning
- Keep every record the hand screen did not judge "no fintech exposure" (E1) or out of scope, plus unscreened OpenAlex hits that pass the lexical test; drop non-English unscreened records and anything before 2015.
- Version duplicates (preprint plus published) merged by DOI and by normalised title: 63 removed. 13 DOIs found by other sources were looked up singly in OpenAlex.
- References resolved to titles only if cited at least four times inside the corpus (1,166 candidates, 1,165 resolved) because of rate limits; this is stricter than the "at least twice" wording printed by some Bibliometrix messages.
- Corpus after cleaning: 972 records (`data/clean/master.csv`). Stage-1 codes in the corpus: I 324, E2 262, E3 224, E4 23, E8 12, E5 2, unscreened 125. Sub-literature counts: C 395, O 299, R 278.

## 5 PRISMA-style counts for the map
| Step | Records |
|---|---|
| OpenAlex works loaded from the core search | 1,700 |
| plus single OpenAlex lookups for records found by Crossref, DOAJ or Semantic Scholar | 11 |
| Works examined | 1,711 |
| Version duplicates merged | 63 |
| Out of scope (stage-1 E1, E6, E7; unscreened without both terms; pre-2015; non-English unscreened) | 676 |
| Final corpus | 972 |
The "out of scope" row is computed as 1,711 minus 63 minus 972 and not counted separately; treat it as approximate.

## 6 Limits
- OpenAlex has no author keywords; keyword analyses use OpenAlex's algorithmic keywords (field ID in Bibliometrix).
- Coverage is open-metadata coverage: 625 of 972 records have an OpenAlex reference list, 188 have no abstract.
- Repository copies (SSRN 30, Zenodo 17) may duplicate journal papers.
- Hand screening was done by one AI assistant, not a human reviewer; Sean should re-screen a sample (`../screening/double_screen_sample.csv`).
