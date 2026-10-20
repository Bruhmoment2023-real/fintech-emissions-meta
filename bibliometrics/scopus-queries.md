# Scopus and Web of Science strings (to paste; not run here, no login)

These reproduce the pack's core question in the two commercial databases. Run them from a library login, export CSV (Scopus) or tab-delimited full record with cited references (WoS), save into `bibliometrics\scopus-drop\` (currently empty or absent: no Scopus export was supplied for this pack) and re-run `python\p2_build_master.py` after adding a loader. Counts below were NOT obtained; fill in on the date you run them.

## Core string, Scopus advanced search
```
TITLE-ABS-KEY ( ( fintech OR "fin-tech" OR "financial technology" OR "digital finance" OR "digital financial" OR "digital inclusive finance" OR "digital financial inclusion" )
  AND ( carbon OR co2 OR "co 2" OR emission* OR "greenhouse gas" OR decarboni* ) )
AND PUBYEAR > 2014 AND PUBYEAR < 2027 AND LANGUAGE ( english )
AND ( LIMIT-TO ( DOCTYPE , "ar" ) )
```
Record the date, the hit count and the filters used. Do not let a book-series or proceedings field leak in: add `AND NOT SRCTYPE ( k )` to drop book series, and inspect any document whose source title is a book series before keeping it (the pack-10 audit found this contamination on a related topic).

## Narrow string for the empirical core (fintech exposure in the title)
```
TITLE ( fintech OR "financial technology" OR "digital finance" OR "digital inclusive finance" OR "digital financial inclusion" )
AND TITLE-ABS-KEY ( carbon OR co2 OR emission* OR "carbon intensity" OR "carbon neutrality" )
AND PUBYEAR > 2014 AND DOCTYPE ( ar )
```

## Reviews and meta-analyses (sub-literature R)
```
TITLE-ABS-KEY ( ( fintech OR "financial technology" OR "digital finance" OR "digital financial inclusion" ) AND ( carbon OR emission* ) AND ( "meta-analysis" OR "meta analysis" OR "meta-regression" OR "systematic review" OR "systematic literature review" OR bibliometric* ) )
AND PUBYEAR > 2014
```

## Web of Science Core Collection (advanced search)
```
TS=((fintech OR "fin-tech" OR "financial technology" OR "digital finance" OR "digital financial" OR "digital inclusive finance" OR "digital financial inclusion")
    AND (carbon OR CO2 OR emission* OR "greenhouse gas" OR decarboni*))
AND PY=(2015-2026) AND LA=(English) AND DT=(Article)
```

## What was run instead (all dated 16 to 17 Oct 2026, exact strings in `..\data\raw\search_log.csv`)
- OpenAlex works API, `title_and_abstract.search` with the core string above and `publication_year:2015-2026`: 1,701 hits, all saved.
- Crossref `query.bibliographic` (relevance-ranked, 300 rows each, journal articles from 2015) for eight phrase queries; the hit totals Crossref reports (hundreds of thousands) are loose relevance matches and not meaningful counts.
- DOAJ article search with the core string and four shorter strings.
- Semantic Scholar Graph API paper search: several queries returned nothing because of rate limiting (log shows 0 saved); treat as partial.
- Not run: RePEc/IDEAS and EconPapers (a form POST is needed), Scopus, Web of Science.
