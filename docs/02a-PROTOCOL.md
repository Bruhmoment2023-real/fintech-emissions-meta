# Protocol: Does fintech reduce carbon emissions? A systematic review and meta-analysis of regression estimates

Written 17 October 2026, 03:40 IST, **before any record was screened and before any effect size was extracted or seen**. A SHA-256 of this file is stored in `02a-PROTOCOL.sha256` at the moment it was frozen; any later change goes into `02b-PROTOCOL-AMENDMENTS.md` with a date and a reason. Format follows PRISMA-P 2015 headings and the PRISMA 2020 items for the final report (Page et al. 2021, BMJ 372:n71, opened in full via Europe PMC). Not registered on PROSPERO or OSF (registration needs a login; the signed hash and date stand in for it and this is stated in any write-up).

What was already known when this was written (to be transparent about order of work): Track B's scoping count of about 549 OpenAlex papers (title/abstract search, 13 Oct 2026); the existence of two nearby syntheses, Gok (2020) on financial development and Irikefe, Yee and Zainudin (2026) on financial inclusion (neither opened by me before freezing; see `01-prior-work.md`); and that I had looked at no emissions estimates from fintech studies.

## 1. Question and hypotheses
- **Primary question:** across published quantitative studies, what is the average partial association between a fintech or digital-finance measure and carbon emissions, and how much does it vary?
- **H1:** the pooled partial correlation is negative (fintech goes with lower emissions).
- **H2:** funnel asymmetry exists and the bias-corrected estimate (PET-PEESE) is smaller in absolute value than the uncorrected random-effects estimate.
- **H3:** heterogeneity is high (I-squared above 75 percent).
- **Exploratory (no directional prediction fixed in advance):** moderators listed in section 6; whether estimates differ by region, unit of analysis, fintech measure, emissions measure, estimator, and publication venue quality.

## 2. Eligibility (PECOS)
Include a study when all hold:
- **Population/setting:** any panel or time-series of countries, regions, provinces, cities, industries or firms.
- **Exposure:** a quantitative fintech, digital finance, digital inclusive finance, or financial-technology measure entered as a continuous regressor (an index, a count, a share, a patent measure, a text-derived measure). Binary treatment or policy-pilot dummies are coded as a separate "policy dummy" type and analysed only in a sensitivity analysis.
- **Outcome:** a carbon-emissions measure where higher means more emissions: CO2 total, CO2 per capita, carbon (CO2) intensity, greenhouse-gas emissions. Ecological footprint, load capacity factor, environmental-quality or carbon-efficiency indices are **not** primary outcomes (their direction or meaning differs) and are listed separately as "other environmental outcome".
- **Design:** regression-based observational study reporting, for the fintech variable on the emissions outcome, a coefficient with a standard error, t-statistic, p-value or confidence interval, and the number of observations.
- **Period and language:** published or posted 1 January 2015 to the search date; English text.
- **Publication form:** journal articles and working papers/preprints (flagged); no theses, conference abstracts without results, or news.
- **Full text:** must be openly readable by me without login. Studies that meet every other criterion but have no open full text are counted and listed as "eligible, not extractable", never silently dropped; closed-access studies are not extracted.

Exclude: reviews and meta-analyses (kept for prior-work); studies with only interaction terms and no main effect; studies where fintech is the dependent variable or only a mediator; duplicate reports of the same sample (keep the version with the fuller reporting; log both); studies whose sample overlaps another included study exactly are kept but flagged for a leave-one-out check.

## 3. Information sources and search (dates logged by the scripts)
Sources: OpenAlex (title-and-abstract search; budget-limited and run after the daily quota reset), Crossref REST (bibliographic search), Semantic Scholar Graph API (relevance search), RePEc/IDEAS and EconPapers (web search form, if automated access is permitted; blocked access is reported), DOAJ API. Reference lists of included studies and of the two nearest syntheses are snowballed one level.
Core string (adapted to each source's syntax; the exact string run and its date are saved in `data/raw/search_log.csv`):
`(fintech OR "fin-tech" OR "financial technology" OR "digital finance" OR "digital financial" OR "digital inclusive finance" OR "digital financial inclusion") AND (carbon OR CO2 OR "CO 2" OR emission* OR "greenhouse gas" OR decarboni*)`, 2015 onwards. Sources that cannot take Boolean syntax get the four phrase pairs "fintech carbon emissions", "digital finance carbon emissions", "financial technology CO2", "digital inclusive finance carbon".
Records are de-duplicated by DOI, then by normalised title and year; versions of the same work (preprint and journal) are merged and the journal version kept.

## 4. Selection process
- Stage 1, title and abstract: each record is coded include / exclude / unclear with a reason from a fixed list (not fintech exposure; not emissions outcome; not empirical regression; review; other environmental outcome; duplicate; non-English; out of period; other). Rule-based pre-screening is allowed only for clear exclusions on text I can read (no fintech term and no emissions term in title and abstract), and its list is saved. Everything else is read.
- Stage 2, full text: open full text is retrieved from legal open sources; each record is coded eligible/ineligible with a reason, or "no open full text".
- One screener (an AI assistant) with a documented rule list; Sean should double-screen a random 10 percent before publication; agreement will be reported if he does. This single-screener limit is stated up front.

## 5. Data extraction and effect size
Extracted per estimate (columns in `extraction/estimates.csv`): study id, DOI, authors, year, venue, publication status; country or region; unit of analysis; sample period; fintech measure and type; emissions measure and type; log or level form; estimator; coefficient (b), standard error, t, p, or CI limits as reported; number of observations (N), number of cross-sectional units, number of regressors (k) where stated; table and page where the estimate sits; quotation or cell text as evidence; whether instrumented or lagged.
**Selected estimate rule (fixed before extraction):** one primary estimate per study-sample: the full-sample baseline model, taken from the first column of the main results table that includes the fintech variable on the paper's headline emissions outcome. The rule does not use significance or sign. Studies with separate main-table samples (for example several country groups reported as the paper's headline findings) contribute one estimate per sample. A secondary data set contains every estimate in the main results tables (not appendix or robustness checks), capped at six per study, for the multi-level model.
**Effect size:** the partial correlation, r = t / sqrt(t^2 + df), with df = N - k where k counts all regressors reported (if k is not stated, I impute the median k of studies that report it and run a sensitivity analysis without imputed studies). Analysis uses Fisher's z for the partial correlation, z = atanh(r), variance 1 / (N - k - 3), as implemented in metafor's `escalc(measure = "ZPCOR")`. If only b and SE are reported, t = b / SE; if only a p-value, t is recovered from p and df; if only a CI, SE = (upper - lower) / (2 x 1.96). Nonlinear specifications: only the linear fintech term is used when a squared term is present, and these studies are flagged. Sign: negative r means more fintech goes with lower emissions.
Panel caveat: in fixed-effects panels the software's df is less than N - k, so df = N - k overstates precision. Sensitivity analysis replaces N with the number of cross-sectional units where reported.

## 6. Analysis plan
1. Random-effects meta-analysis of z (REML; Knapp-Hartung adjustment; back-transform to r), with tau-squared, I-squared, Cochran's Q and the 95 percent prediction interval.
2. Dependence: estimates clustered within study; sensitivity using `rma.mv` with random effects for study and estimate, and cluster-robust variance (robust, cluster = study).
3. Meta-regression with study features, one at a time and then jointly if the number of studies allows (at least ten per moderator level for inference; fewer is reported as descriptive): region (China, other Asia, other single country, multi-country/global), unit of analysis (country, province, city, firm/industry), fintech measure type (composite index, fintech patent or count, adoption/usage, policy dummy), emissions measure (CO2 total, per capita, intensity, other GHG), estimator (OLS/FE panel, GMM/IV, ARDL-type, quantile, other), publication status (journal, preprint), venue-quality flag, publication year, mean sample year, log-form outcome.
4. Publication bias: contour-enhanced funnel plot of r against its standard error; Egger-type regression (metafor `regtest`, with SE and with sample-size predictor); Begg rank correlation; PET-PEESE (weighted regressions of r on SE, then on SE-squared if the PET intercept differs from zero at p < 0.10); trim-and-fill reported as a sensitivity check only. Interpretation caveats written in advance: Egger and PET-PEESE are unreliable with high heterogeneity and few studies; estimates from small panels may be small for reasons other than selection.
5. Sensitivity: leave-one-out; exclude imputed-k studies; exclude preprints; exclude flagged-venue studies; exclude studies with sample overlap; df based on units; the policy-dummy set analysed separately.
6. If fewer than 10 studies have comparable usable estimates, no pooled estimate is reported as a result and a structured scoping review of what the literature measures and finds is delivered instead (decision rule fixed here).

## 7. Venue quality and predatory-journal flags
Record each study's venue and publisher. A venue is flagged only if it appears on a warning list I can open and query myself (candidate lists: Beall's List archive, the Kscien predatory-journal list, the Retraction Watch Hijacked Journal Checker), and its DOAJ inclusion status is recorded (DOAJ listing is a positive signal, not proof of quality). The list used, access date and match are logged. "Not flagged" is not an endorsement.

## 8. Risk-of-bias items (descriptive, not used to weight)
Endogeneity addressed (IV, GMM, lagged regressor); fixed effects reported; standard errors clustered or robust; N and k reported; data source stated; sign and size reported in the abstract versus main table; data or code shared.

## 9. Reporting
PRISMA 2020 flow diagram with counts and reasons at each stage; all screening decisions with reasons in `screening/`; all extracted values with page evidence in `extraction/`; R scripts rebuilding every table and figure; software versions logged.

## 10. Known limitations declared in advance
Open-full-text restriction will drop many Elsevier and Wiley studies; the corpus therefore over-represents open-access and MDPI-type venues, which is itself a selection risk and is analysed through the venue moderator; single screener and single extractor; English only; partial correlations are comparable in direction and scale but not in economic units; data in the primary studies are shared and reused (Peking University index, World Bank, CEADs), so estimates are not independent.
