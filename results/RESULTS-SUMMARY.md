# Pack 14 results summary: does fintech go with lower carbon emissions?

All numbers come from `code/meta_analysis.R` run on `extraction/estimates.csv` (log: `results/meta_analysis_log.txt`; tables in `results/tables/`; figures in `results/figures/`). Effect size = partial correlation r = t / sqrt(t^2 + df), analysed as Fisher z; negative r = fintech goes with lower emissions. Every coefficient and SE or t was checked against the opened full text before entering the data (91 of 91 rows verified).

## What went in
- 55 studies, 91 main-table estimates (1 to 3 per study; 55 "primary" = first column of the main table on the headline emissions outcome, fixed in the protocol before results).
- Full texts: 117 opened in full; 62 excluded at full text with logged codes (X3 no usable coefficient 27, X2 outcome not emissions 16, X4 interaction/polynomial/ECM only 9, X7 unusable N or layout 8, X6 retracted 2); 55 studies extracted.
- Only open full texts were read. 94 records had an open copy listed but not retrievable, and 125 were closed or unknown. The extractable set is not a random sample of the literature.
- Outcome mix across the 55 primary estimates: total CO2 26 studies, carbon intensity 15, CO2 per capita 8, other (agricultural, household, firm-level) 6. Region: China 40, other Asia 8, multi-country 4, other 3.

## Pooled effect
- Primary model (one estimate per study, REML, Knapp-Hartung): r = -0.151, 95% CI -0.227 to -0.073, p = 0.0003, k = 55.
- Multilevel model on all 91 estimates, CR2 robust: r = -0.156 (CI -0.223 to -0.089), p < 0.0001.
- Heterogeneity: tau^2 = 0.078, I^2 = 99.7%, Q(54) = 1989.9, p < 0.0001. 95% prediction interval -0.615 to +0.391, i.e. a new study could plausibly find a large reduction or a sizeable increase.
- Sign counts among the 55 primary estimates: 44 negative, 11 positive; median r = -0.148 (range -0.878 to +0.509); 38 negative and 7 positive are significant at the 5% level on the printed t.
- Leave-one-study-out range: r = -0.163 to -0.129 (no single study drives the result).

## Meta-regression (single moderators, Q-test)
- Estimator: QM = 4.30, p = 0.005, R^2 = 21%. ARDL time-series studies (5) average r = -0.53; fixed-effects OLS (36) -0.15; GMM or IV (3) +0.16. Small cells; treat as a lead.
- Log form: QM = 6.85, p = 0.002; studies that did not state the transformation (11) average r = -0.41, log (29) -0.10, level (15) -0.07.
- No detectable difference by region (p = 0.89), unit of analysis (p = 0.70), fintech type (p = 0.98), emissions type (p = 0.75; intensity -0.22, total CO2 -0.11, per capita -0.15), venue flag (p = 0.27), publication year (p = 0.58) or sample midpoint year (p = 0.20).

## Publication bias
- Egger-type test: strongly significant asymmetry (z on SE, p < 0.0001; rma-based p = 0.031). Begg rank test not significant (p = 0.82).
- PET intercept (bias-corrected r) = 0.001 (SE 0.006, p = 0.90), so the PET-PEESE conditional estimate is close to zero. Caution: with 55 studies mostly sharing very small SEs (large N) the PET slope is driven by a few small-N, large-effect studies, and cluster-robust df are about 1 (slope p = 0.12). Read this as "the pooled effect is not robust to small-study effects", not as a proof of no effect.
- Trim-and-fill added no studies (k0 = 0), which is a different conclusion from Egger: the funnel is asymmetric because of a left tail of small-sample studies, not a gap on the right.

## Sensitivity (pooled r, primary model unless stated)
- Excluding studies whose regressor count k had to be imputed (48 studies): -0.140.
- Excluding studies on warning-list venues (4 flagged, 51 left): -0.163.
- Excluding rows whose printed stars contradict the printed SE or t (51 left): -0.157.
- Excluding studies with inferred N (39 left): -0.126.
- Excluding first-column fallbacks (53 left): -0.153.
- Degrees of freedom from the number of units instead of N (34 studies): -0.334 (a stricter df rule gives a larger |r| for the same t; the subset is small and is shown only as a check on the df assumption).
- Excluding overlapping samples: no studies flagged by the automatic rule (same index, unit, period and N); this does not detect partial overlap in Peking University index panels.
- All studies were published articles (no preprints in the final 55; one preprint text was used for a journal paper and is noted in the entry).

## Venue and warning-list check (leads only, not verdicts)
- 4 of 55 included studies are in outlets that match a warning list in our snapshot: Pressacademia (Kscien non-recommended and Beall publishers), EconJournals / International Journal of Energy Economics and Policy (2 studies; Kscien non-recommended list), Boya Century Publishing / BCP Business and Management (Beall publishers). Beall's lists are 2016-2017 snapshots; Kscien is volunteer-run. DOAJ lists 21 of the 55 venues.

## Not done or limited
- RePEc/IDEAS and EconPapers were not searched (their search is a web form that needs a POST; the working rules forbid form submissions). Semantic Scholar returned only part of the planned queries because of rate limits.
- Single screener and single extractor; a 10% random sample for a second human screener is in `screening/double_screen_sample.csv` (118 records, columns blank).
- Elsevier, Wiley and SAGE open copies returned HTTP 403 to scripted requests; none were fetched, so those journals are underrepresented.
- One estimate type per study; elasticity-to-partial-correlation conversion uses the reported t and N (or an inferred N, flagged), not the original standard errors alone.
- The headline result is "negative on average and significant, with extreme heterogeneity and signs of selection"; it is not a causal estimate. Many included studies print stars that do not match their SE or t (flagged, sensitivity above).
