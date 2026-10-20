# Meta-analysis of fintech -> carbon emissions partial correlations (protocol 02a sections 5-6).
# Usage: Rscript meta_analysis.R <estimates.csv> <outdir>
# Run with R_LIBS_USER=D:\Research-Publishing\_tools\R-lib (metafor, clubSandwich installed there).
.libPaths(c('D:/Research-Publishing/_tools/R-lib', .libPaths()))
suppressMessages({library(metafor); library(clubSandwich)})
args <- commandArgs(trailingOnly = TRUE)
inp <- ifelse(length(args) >= 1, args[1], '../extraction/estimates.csv'); out <- ifelse(length(args) >= 2, args[2], '../results/')
dir.create(out, showWarnings = FALSE, recursive = TRUE); dir.create(file.path(out, 'figures'), showWarnings = FALSE); dir.create(file.path(out, 'tables'), showWarnings = FALSE)
sink(file.path(out, 'meta_analysis_log.txt'), split = TRUE)
cat('metafor', as.character(packageVersion('metafor')), '| clubSandwich', as.character(packageVersion('clubSandwich')), '| R', R.version.string, '\n')
set.seed(20261017)
d <- read.csv(inp, stringsAsFactors = FALSE, na.strings = c('', 'NA'))
num <- function(x) suppressWarnings(as.numeric(x))
for (v in c('ci_low','ci_high','n_units','p','t','se','b')) if (!(v %in% names(d))) d[[v]] <- NA
for (v in c('inconsistent_flag','n_inferred_flag','primary_fallback_flag','venue_flag','sample_overlap_flag')) if (!(v %in% names(d))) d[[v]] <- 0
for (v in c('b', 'se', 't', 'p', 'ci_low', 'ci_high', 'n_obs', 'n_units', 'k_reg', 'year')) d[[v]] <- num(d[[v]])
# ---- t statistic: reported t, else b/se, else from p and df, else from CI
kmed <- median(d$k_reg[d$k_reg_reported == 1], na.rm = TRUE); if (is.na(kmed)) kmed <- 8
cat('median reported k (regressors excluding intercept):', kmed, '\n')
d$k_used <- ifelse(is.na(d$k_reg), kmed, d$k_reg); d$k_imputed <- is.na(d$k_reg)
d$se_from_ci <- ifelse(is.na(d$se) & !is.na(d$ci_low) & !is.na(d$ci_high), (d$ci_high - d$ci_low) / (2 * 1.96), NA)
d$se_use <- ifelse(is.na(d$se), d$se_from_ci, d$se)
d$df <- d$n_obs - d$k_used - 1
d$t_use <- ifelse(!is.na(d$t), d$t, ifelse(!is.na(d$b) & !is.na(d$se_use), d$b / d$se_use,
                  ifelse(!is.na(d$p) & !is.na(d$b), sign(d$b) * qt(1 - d$p / 2, d$df), NA)))
d <- d[!is.na(d$t_use) & !is.na(d$n_obs) & d$df > 3, ]
d$ri <- d$t_use / sqrt(d$t_use^2 + d$df)           # partial correlation; negative = more fintech, less emissions
d$se_r <- sqrt((1 - d$ri^2) / d$df)
es <- escalc(measure = 'ZPCOR', ti = d$t_use, ni = d$n_obs, mi = d$k_used, data = d)   # Fisher z of partial r, var = 1/(ni - mi - 3)
d$zi <- es$yi; d$vi <- es$vi
prim <- d[d$primary == 1, ]
cat('\nEstimates usable:', nrow(d), '| primary (one per study-sample):', nrow(prim), '| studies:', length(unique(prim$study_id)), '\n')
write.csv(d, file.path(out, 'tables', 'estimates_with_effect_sizes.csv'), row.names = FALSE) -> tmp
res_row <- function(m, label) {
  data.frame(model = label, k = m$k, r = tanh(as.numeric(m$beta[1])), ci_lb = tanh(m$ci.lb[1]), ci_ub = tanh(m$ci.ub[1]), pval = m$pval[1], tau2 = m$tau2, I2 = if (!is.null(m$I2)) m$I2 else NA, QEp = m$QEp)
}
tabs <- list()
m1 <- rma(zi, vi, data = prim, method = 'REML', test = 'knha'); print(summary(m1))
pi1 <- predict(m1, transf = tanh); cat('\n95% prediction interval for r:', round(pi1$pi.lb, 3), 'to', round(pi1$pi.ub, 3), '\n')
tabs[['primary_RE']] <- res_row(m1, 'Primary: RE, one estimate per study-sample, REML + Knapp-Hartung')
# ---- dependence: all estimates, multilevel with cluster-robust inference
allm <- d[d$in_main_table == 1, ]
if (nrow(allm) > nrow(prim) && length(unique(allm$study_id)) >= 5) {
  m2 <- rma.mv(zi, vi, random = ~ 1 | study_id / est_id, data = allm, method = 'REML')
  r2 <- robust(m2, cluster = allm$study_id, clubSandwich = TRUE); print(r2)
  tabs[['allest_MV']] <- data.frame(model = 'All main-table estimates: multilevel, CR2 robust', k = m2$k, r = tanh(as.numeric(r2$beta[1])), ci_lb = tanh(r2$ci.lb[1]), ci_ub = tanh(r2$ci.ub[1]), pval = r2$pval[1], tau2 = sum(m2$sigma2), I2 = NA, QEp = m2$QEp)
}
# ---- sensitivity
sens <- function(sub, label) { if (nrow(sub) >= 5) tabs[[label]] <<- res_row(rma(zi, vi, data = sub, method = 'REML', test = 'knha'), label) }
sens(prim[!prim$k_imputed, ], 'Excluding studies with imputed k')
sens(prim[prim$pub_status == 'journal', ], 'Journal articles only')
sens(prim[prim$venue_flag == 0, ], 'Excluding flagged venues')
sens(prim[prim$sample_overlap_flag == 0, ], 'Excluding overlapping samples')
sens(prim[prim$inconsistent_flag == 0, ], 'Excluding rows whose stars contradict the printed SE or t')
sens(prim[prim$n_inferred_flag == 0, ], 'Excluding studies with inferred N')
sens(prim[prim$primary_fallback_flag == 0, ], 'Excluding first-column fallbacks')
if ('n_units' %in% names(prim)) { pu <- prim[!is.na(prim$n_units) & prim$n_units > 8, ]; if (nrow(pu) >= 5) {
  e2 <- escalc(measure = 'ZPCOR', ti = pu$t_use, ni = pu$n_units, mi = pu$k_used, data = pu); tabs[['units_df']] <- res_row(rma(yi, vi, data = e2, method = 'REML', test = 'knha'), 'df based on number of units instead of N') } }
sens(prim[prim$fintech_type != 'policy_dummy', ], 'Excluding policy-dummy fintech measures')
# leave-one-out
if (m1$k >= 6) { loo <- leave1out(m1, transf = tanh); write.csv(data.frame(study = prim$study_id, r = loo$estimate, lb = loo$ci.lb, ub = loo$ci.ub, I2 = loo$I2), file.path(out, 'tables', 'leave_one_out.csv'), row.names = FALSE) }
# ---- moderators (one at a time; levels with < 3 studies are collapsed to 'other' automatically)
modtab <- list()
for (mv in c('region', 'unit', 'fintech_type', 'emissions_type', 'estimator', 'pub_status', 'venue_flag', 'log_form')) {
  if (!(mv %in% names(prim))) next
  x <- as.character(prim[[mv]]); x[is.na(x)] <- 'unknown'; tt <- table(x); x[x %in% names(tt)[tt < 3]] <- 'other(<3)'
  pp <- prim; pp$.mod <- factor(x)
  if (nlevels(pp$.mod) < 2) next
  mm <- try(rma(zi, vi, mods = ~ .mod, data = pp, method = 'REML', test = 'knha'), silent = TRUE)
  if (inherits(mm, 'try-error')) next
  lv <- levels(pp$.mod); sub <- sapply(lv, function(l) { s <- try(rma(zi, vi, data = pp[pp$.mod == l, ], method = 'REML', test = 'knha'), silent = TRUE); if (inherits(s, 'try-error')) NA else tanh(as.numeric(s$beta[1])) })
  modtab[[mv]] <- data.frame(moderator = mv, QM = mm$QM, QMdf = mm$m, QMp = mm$QMp, R2 = mm$R2, levels = paste(paste0(lv, '=', table(pp$.mod)[lv], ' studies, r=', round(sub, 3)), collapse = '; '))
}
for (mv in c('year', 'sample_mid_year')) if (mv %in% names(prim) && sum(!is.na(prim[[mv]])) >= 8) {
  pp <- prim[!is.na(prim[[mv]]), ]; pp$.x <- scale(num(pp[[mv]]), scale = FALSE)[, 1]
  mm <- rma(zi, vi, mods = ~ .x, data = pp, method = 'REML', test = 'knha')
  modtab[[mv]] <- data.frame(moderator = mv, QM = mm$QM, QMdf = mm$m, QMp = mm$QMp, R2 = mm$R2, levels = paste0('slope per year on z = ', round(mm$beta[2], 4)))
}
if (length(modtab)) write.csv(do.call(rbind, modtab), file.path(out, 'tables', 'meta_regression_single_moderators.csv'), row.names = FALSE)
# ---- publication bias
pb <- list()
pb$egger_z <- regtest(m1, model = 'lm', predictor = 'sei'); cat('\nEgger-type regression (z on SE):\n'); print(pb$egger_z)
pb$egger_rma <- regtest(m1, model = 'rma', predictor = 'sei'); print(pb$egger_rma)
pb$begg <- ranktest(m1); print(pb$begg)
pr <- prim; pr$w <- 1 / pr$se_r^2
pet <- lm(ri ~ se_r, data = pr, weights = w); pet_cr <- coef_test(pet, vcov = 'CR2', cluster = pr$study_id)
peese <- lm(ri ~ I(se_r^2), data = pr, weights = w); peese_cr <- coef_test(peese, vcov = 'CR2', cluster = pr$study_id)
cat('\nPET (r on SE, WLS, CR2 clustered):\n'); print(pet_cr); cat('\nPEESE (r on SE^2):\n'); print(peese_cr)
pet_p <- pet_cr$p_Satt[1]; used <- ifelse(pet_p < 0.10, 'PEESE', 'PET')
cat('PET intercept p =', round(pet_p, 4), '-> conditional estimate uses', used, '\n')
cond <- if (used == 'PEESE') peese_cr else pet_cr
tf <- trimfill(m1); cat('\nTrim-and-fill: k0 =', tf$k0, ' adjusted r =', round(tanh(as.numeric(tf$beta[1])), 4), '\n')
bias <- data.frame(test = c('Egger (lm, z on SE) intercept z', 'Egger (rma) z', 'Begg rank tau', 'PET intercept (bias-corrected r)', 'PEESE intercept (bias-corrected r)', 'Conditional PET-PEESE estimate', 'Trim-and-fill adjusted r', 'Uncorrected primary RE r'),
  estimate = c(pb$egger_z$zval, pb$egger_rma$zval, pb$begg$tau, pet_cr$beta[1], peese_cr$beta[1], cond$beta[1], tanh(as.numeric(tf$beta[1])), tanh(as.numeric(m1$beta[1]))),
  p_or_se = c(pb$egger_z$pval, pb$egger_rma$pval, pb$begg$pval, pet_cr$p_Satt[1], peese_cr$p_Satt[1], cond$p_Satt[1], NA, m1$pval[1]),
  note = c('', '', '', paste('SE', round(pet_cr$SE[1], 4)), paste('SE', round(peese_cr$SE[1], 4)), used, paste('k0 =', tf$k0), ''))
write.csv(bias, file.path(out, 'tables', 'publication_bias_tests.csv'), row.names = FALSE)
write.csv(do.call(rbind, tabs), file.path(out, 'tables', 'pooled_estimates.csv'), row.names = FALSE)
# ---- figures
png(file.path(out, 'figures', 'F1_forest_primary.png'), width = 1800, height = max(900, 38 * m1$k + 300), res = 200)
forest(m1, slab = paste(prim$first_author, prim$year), transf = tanh, xlab = 'Partial correlation r (negative = fintech goes with lower emissions)', header = c('Study', 'r [95% CI]'), cex = 0.6, refline = 0, mlab = 'Random-effects (REML, Knapp-Hartung)')
dev.off()
png(file.path(out, 'figures', 'F2_funnel_contour.png'), width = 1600, height = 1400, res = 200)
funnel(m1, level = c(90, 95, 99), shade = c('white', 'gray85', 'gray70'), refline = 0, legend = TRUE, xlab = 'Fisher z of partial correlation (negative = fintech goes with lower emissions)', ylab = 'Standard error')
dev.off()
png(file.path(out, 'figures', 'F3_pet_peese.png'), width = 1600, height = 1200, res = 200)
plot(pr$se_r, pr$ri, xlab = 'Standard error of partial r', ylab = 'Partial correlation r', pch = 19, col = '#2c7fb860', main = 'PET and PEESE fits (primary estimates)')
xs <- seq(0, max(pr$se_r), length.out = 100); lines(xs, coef(pet)[1] + coef(pet)[2] * xs, col = '#c0392b', lwd = 2); lines(xs, coef(peese)[1] + coef(peese)[2] * xs^2, col = '#27ae60', lwd = 2)
abline(h = 0, lty = 3); legend('topright', c('PET', 'PEESE'), col = c('#c0392b', '#27ae60'), lwd = 2)
dev.off()
cat('\nsessionInfo:\n'); print(sessionInfo()); sink()
