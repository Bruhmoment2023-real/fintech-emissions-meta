# Pack 14 results summary: does fintech go with lower carbon emissions?

All numbers come from `code/meta_analysis.R` run on `extraction/estimates.csv` (log: `results/meta_analysis_log.txt`; tables in `results/tables/`; figures in `results/figures/`). Effect size = partial correlation r = t / sqrt(t^2 + df), analysed as Fisher z; negative r = fintech goes with lower emissions. Every coefficient and SE or t was checked against the opened full text before entering the data (89 of 89 rows verified). After the author check of 22 Oct 2026 (docs/02b, amendment 11) one study was removed, one primary estimate changed column and N or k were corrected in 12 rows..

## What went in
- 54 studies, 89 main-table estimates (1 to 3 per study; 54 "primary" = first column of the main table on the headline emissions outcome, fixed in the protocol before results).
- Full texts: 117 opened in full; 63 excluded at full text with logged codes (X3 no usable coefficient 26, X2 outcome not emissions 17, X4 interaction/polynomial/ECM only 9, X7 unusable N or layout 8, X6 retracted 2, X1 no fintech exposure 1); 54 studies extracted.
- Only open full texts were read. 95 records had an open copy listed but not retrievable, and 124 were closed or unknown. The extractable set is not a random sample of the literature.
- Outcome mix across the 54 primary estimates: total CO2 26 studies, carbon intensity 15, CO2 per capita 8, other (agricultural, household, firm-level) 5. Region: China 39, other Asia 8, multi-country 4, other 3.

## Pooled effect
- Primary model (one estimate per study, REML, Knapp-Hartung): r = -0.155, 95% CI -0.232 to -0.076, p = 0.0003, k = 54.
- Multilevel model on all 89 estimates, CR2 robust: r = -0.160 (CI -0.227 to -0.092), p < 0.0001.
- Heterogeneity: tau^2 = 0.080, I^2 = 99.7%, Q(53) = 3635.1, p < 0.0001. 95% prediction interval -0.622 to +0.394, i.e. a new study could plausibly find a large reduction or a sizeable increase.
- Sign counts among the 54 primary estimates: 43 negative, 11 positive; median r = -0.152 (range -0.878 to +0.509); 37 negative and 7 positive are significant at the 5% level on the printed t.
- Leave-one-study-out range: r = -0.167 to -0.132 (no single study drives the result).

## Meta-regression (single moderators, Q-test)
- Estimator: QM = 4.25, p = 0.005, R^2 = 21%. ARDL time-series studies (5) average r = -0.53; fixed-effects OLS (35) -0.16; GMM or IV (3) +0.16. Small cells; treat as a lead.
- Log form: QM = 6.58, p = 0.003; studies that did not state the transformation (11) average r = -0.41, log (29) -0.11, level (14) -0.06.
- No detectable difference by region (p = 0.92), unit of analysis (p = 0.81), fintech type (p = 0.99), emissions type (p = 0.79; intensity -0.22, total CO2 -0.12, per capita -0.14), venue flag (p = 0.26), publication year (p = 0.58) or sample midpoint year (p = 0.16).

## Publication bias
- Egger-type test: weak evidence of asymmetry (z on SE, p = 0.089; rma-based p = 0.045). Begg rank test significant (tau = -0.24, p = 0.011). (Before the author check, Egger was p < 0.0001: the first-pass primary for Wang 2024, N = 965,344, was a near-zero column-2 estimate with a tiny SE, which dominated the precision-weighted regression.)
- PET intercept (bias-corrected r) = -0.158 (SE 0.146, p = 0.48); PEESE -0.153 (SE 0.109). The bias-corrected estimates are close to the uncorrected -0.155 but very imprecise. Caution: with 54 studies mostly sharing very small SEs (large N) the PET slope is driven by a few small-N, large-effect studies, and cluster-robust df are about 1 (slope p = 0.76). Read this as "the correction does not move the point estimate but cannot rule out zero".
- Trim-and-fill added no studies (k0 = 0), which is a different conclusion from Egger: the funnel is asymmetric because of a left tail of small-sample studies, not a gap on the right.

## Sensitivity (pooled r, primary model unless stated)
- Excluding studies whose regressor count k had to be imputed (53 studies; one imputed k remains): -0.143.
- Excluding studies on warning-list venues (4 flagged, 50 left): -0.168.
- Excluding rows whose printed stars contradict the printed SE or t (50 left): -0.162.
- Excluding studies with inferred N (38 left): -0.130.
- Excluding first-column fallbacks (53 left; one fallback remains): -0.154.
- Degrees of freedom from the number of units instead of N (33 studies): -0.342 (a stricter df rule gives a larger |r| for the same t; the subset is small and is shown only as a check on the df assumption).
- Excluding overlapping samples: no studies flagged by the automatic rule (same index, unit, period and N); this does not detect partial overlap in Peking University index panels.
- All studies were published articles (no preprints in the final 54; one preprint text was used for a journal paper and is noted in the entry).

## Venue and warning-list check (leads only, not verdicts)
- 4 of 54 included studies are in outlets that match a warning list in our snapshot: Pressacademia (Kscien non-recommended and Beall publishers), EconJournals / International Journal of Energy Economics and Policy (2 studies; Kscien non-recommended list), Boya Century Publishing / BCP Business and Management (Beall publishers). Beall's lists are 2016-2017 snapshots; Kscien is volunteer-run. DOAJ lists the venues of 20 of the 54 studies.

## Not done or limited
- RePEc/IDEAS and EconPapers were not searched (their search is a web form that needs a POST; the working rules forbid form submissions). Semantic Scholar returned only part of the planned queries because of rate limits.
- Single screener and single extractor, followed by a second check of a sample against the source with the first-pass answer visible (non-blind): 80 stage-1 decisions (76 agreed, 95.0%, kappa 0.88) and all 55 first-pass primary estimates (44 fully correct). Corrections are in `checks/` and docs/02b amendment 11.
- Elsevier, Wiley and SAGE open copies returned HTTP 403 to scripted requests; none were fetched, so those journals are underrepresented.
- One estimate type per study; elasticity-to-partial-correlation conversion uses the reported t and N (or an inferred N, flagged), not the original standard errors alone.
- The headline result is "negative on average and significant, with extreme heterogeneity and signs of selection"; it is not a causal estimate. Many included studies print stars that do not match their SE or t (flagged, sensitivity above).
