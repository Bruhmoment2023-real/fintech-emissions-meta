# Data dictionary, pack 14

## extraction/estimates.csv (analysis-ready; one row per extracted estimate; only rows verified against the full text)
| Column | Meaning |
|---|---|
| study_id | Lower-case DOI of the study |
| est_id | study_id plus # and a running number (order in the entry file) |
| primary | 1 = the pre-specified primary estimate (first column of the main table on the headline emissions outcome); 0 = secondary (fully specified column or alternative) |
| in_main_table | 1 if the estimate comes from the paper's main results table |
| first_author, year, venue, pub_status | From the Crossref/OpenAlex record (HTML tags stripped) |
| venue_flag | 1 if venue or publisher matches a Kscien non-recommended list or a Beall list (leads, not verdicts) |
| in_doaj | yes/no from the DOAJ API by ISSN |
| region, region_orig | Coarse group (China, other Asia, multi-country, other) and the original label |
| unit | Unit of analysis (firm, household, city, province, country) |
| period, sample_mid_year | Sample years as printed; midpoint where two years are given |
| fintech_measure, fintech_type | Name of the fintech measure and a type (index, adoption, infrastructure, component, ...) |
| emissions_measure, emissions_type, log_form | Outcome name; type (co2_total, co2_pc, intensity, agricultural, household, firm); log, level or unknown |
| estimator | Estimator of the extracted column (FE_OLS, GMM_IV, ARDL_TS, ...) |
| b, se, t, p | Coefficient, standard error, t statistic and p value as printed (numbers parsed from b_str etc.; SIGN_NEG rows had the sign restored from the authors' text) |
| n_obs, n_units | Observations and cross-sectional units |
| k_reg, k_reg_reported | Regressors excluding intercept and fixed effects; k_reg_reported = 0 when imputed |
| table, page, model_label | Where the estimate is in the paper |
| inconsistent_flag | 1 if printed stars contradict the printed SE or t |
| n_inferred_flag | 1 if N was inferred (units times years) rather than printed |
| primary_fallback_flag | 1 if the first column could not be used and a later column stood in |
| retracted_flag, sample_overlap_flag | Retracted (none included; 2 excluded at full text) and same index/unit/period/N across studies |
| notes, evidence_snippet | Extractor notes and the exact text span that verified b and SE or t |
| ci_low ... vi | Added by `code/meta_analysis.R` in `results/tables/estimates_with_effect_sizes.csv`: df, t used, partial correlation ri, se_r, Fisher z (zi) and its variance (vi) |

## extraction/studies.csv
study_id, first_author, first_author_full, year, title, venue, publisher, issn, in_doaj, pub_status, venue_flag, venue_flag_detail, is_retracted (from OpenAlex).

## screening/
- stage1_decisions.csv: key (DOI or t: plus normalised title), title, year, venue, decision (include or exclude), reason_code (I included; E1 not fintech or digital finance; E2 not an emissions outcome; E3 not an empirical regression estimate; E4 other environmental outcome only; E5 duplicate or version of another record; E8 retracted or retraction notice), reason, screened_utc.
- stage2_decisions.txt: doi|excluded|code|reason; codes X2 outcome not emissions, X3 no usable coefficient or SE, X4 interaction, polynomial, ECM or threshold only, X6 retracted, X7 unusable N or table layout.
- stage0_rule_exclusions.csv: records removed by a lexical rule before hand screening, with the rule.
- double_screen_sample.csv: random 10% (118) of stage-1 decisions with blank columns for a second human screener; random_state 20261017.

## data/
raw (API responses and search log), clean/candidates.csv (merged, de-duplicated), fulltext (text copies of opened papers; not for redistribution), predatory (warning lists as fetched), venue_flags.csv, cache (HTTP cache, SQLite).
