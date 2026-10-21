# Shared-panel and channel analyses (Sections 3.7 and 3.8, Table 5 of the paper).
# Reads the effect sizes written by meta_analysis.R and the sheet 'panels_and_channels' of the data workbook.
# Usage: Rscript panel_dependence.R <meta-analysis-data.xlsx> <results/tables/estimates_with_effect_sizes.csv> [output.txt]
.libPaths(c('D:/Research-Publishing/_tools/R-lib', .libPaths()))
suppressMessages({library(metafor); library(clubSandwich); library(readxl)})
a <- commandArgs(trailingOnly = TRUE)
if (length(a) >= 3) sink(a[3], split = TRUE)
cat('metafor', as.character(packageVersion('metafor')), '| clubSandwich', as.character(packageVersion('clubSandwich')), '|', R.version.string, '
')
pc <- as.data.frame(read_excel(a[1], sheet = 'panels_and_channels'))
d <- read.csv(a[2], stringsAsFactors = FALSE)
cat('primary rows', sum(d$primary == 1), '| main-table rows', sum(d$in_main_table == 1), '| coding rows', nrow(pc), '\n')
pc$pA <- ifelse(pc$panel_rule_A == 'own panel', pc$study_id, pc$panel_rule_A)
pc$pB <- ifelse(pc$panel_rule_B == 'own panel', pc$study_id, pc$panel_rule_B)
d <- merge(d, pc[, c('study_id', 'pA', 'pB', 'kept_one_per_panel_A', 'kept_one_per_panel_B', 'channels_tested', 'n_obs')], by = 'study_id', suffixes = c('', '.pc'))
prim <- d[d$primary == 1, ]; allm <- d[d$in_main_table == 1, ]
cat('n_obs mismatches between sheets:', sum(prim$n_obs != prim$n_obs.pc), '\n')
cat('rule A panels', length(unique(prim$pA)), '| shared:', sum(duplicated(prim$pA) | duplicated(prim$pA, fromLast = TRUE)), '\n'); print(table(prim$pA[prim$pA %in% prim$pA[duplicated(prim$pA)]]))
cat('rule B panels', length(unique(prim$pB)), '| shared:', sum(duplicated(prim$pB) | duplicated(prim$pB, fromLast = TRUE)), '\n'); print(table(prim$pB[prim$pB %in% prim$pB[duplicated(prim$pB)]]))
# kept flag = largest N in its panel?
for (r in c('A', 'B')) { clv <- prim[[paste0("p", r)]]; k <- prim[[paste0('kept_one_per_panel_', r)]]
  mx <- ave(prim$n_obs, clv, FUN = max); cat('rule', r, 'kept rows', sum(k), '| kept row not the largest N:', sum(k == 1 & prim$n_obs != mx), '| panels with !=1 kept:', sum(tapply(k, clv, sum) != 1), '\n') }
f <- function(x) sprintf('%.3f', x)
row <- function(lab, m) cat(sprintf('%-55s k=%3d r=%s (%s to %s) p=%.3f\n', lab, m$k, f(tanh(m$b[1])), f(tanh(m$ci.lb[1])), f(tanh(m$ci.ub[1])), m$pval[1]))
m1 <- rma(zi, vi, data = prim, method = 'REML', test = 'knha'); row('primary (reproduces Table 3)', m1)
m2 <- rma.mv(zi, vi, random = ~ 1 | study_id / est_id, data = allm, method = 'REML'); r2 <- robust(m2, cluster = allm$study_id, clubSandwich = TRUE)
cat(sprintf('multilevel, CR2 by study (reproduces Section 3.2): r=%s (%s to %s)
', sprintf('%.3f', tanh(r2$b[1])), sprintf('%.3f', tanh(r2$ci.lb)), sprintf('%.3f', tanh(r2$ci.ub))))
# clustered row of Table 3 (sensitivity_extra.py): Chinese province/city panels using an inclusion index, by unit
t3 <- ifelse(prim$region == 'China' & prim$unit %in% c('province', 'city') & grepl('PKU|Peking|inclusive finance|financial inclusion|DFI|DIF', prim$fintech_measure, ignore.case = TRUE), paste0('CN-index-', prim$unit), prim$study_id)
cr1 <- function(m, cl) { w <- 1 / (m$vi + m$tau2); mu <- as.numeric(m$b); C <- length(unique(cl))
  s <- tapply(w * (m$yi - mu), cl, sum); se <- sqrt(C / (C - 1) * sum(s^2) / sum(w)^2); h <- qt(0.975, C - 1) * se
  cat(sprintf('   CR1 clusters=%d r=%s (%s to %s)\n', C, f(tanh(mu)), f(tanh(mu - h)), f(tanh(mu + h)))) }
cat('clustered row of Table 3:'); cr1(m1, t3)
for (r in c('A', 'B')) {
  clv <- prim[[paste0("p", r)]]
  row(paste('one per panel, largest N, rule', r), rma(zi, vi, data = prim[prim[[paste0('kept_one_per_panel_', r)]] == 1, ], method = 'REML', test = 'knha'))
  set.seed(20261021); dr <- t(replicate(2000, { i <- tapply(seq_len(nrow(prim)), clv, function(ix) if (length(ix) == 1) ix else sample(ix, 1))
    m <- rma(zi, vi, data = prim[i, ], method = 'REML', test = 'knha'); c(tanh(m$b[1]), m$ci.lb < 0 & m$ci.ub < 0 | m$ci.lb > 0 & m$ci.ub > 0) }))
  cat(sprintf('   random draws rule %s: median %s, 2.5%%-97.5%% %s to %s, draws with CI excluding 0: %d\n', r, f(median(dr[, 1])), f(quantile(dr[, 1], .025)), f(quantile(dr[, 1], .975)), sum(dr[, 2])))
  cat('   rule', r); cr1(m1, clv)
  rb <- robust(m1, cluster = clv, clubSandwich = TRUE); cat(sprintf('   CR2 rule %s: r=%s (%s to %s) df=%.1f\n', r, f(tanh(rb$b[1])), f(tanh(rb$ci.lb)), f(tanh(rb$ci.ub)), rb$dfs))
  prim$pp <- clv; mm <- rma.mv(zi, vi, random = ~ 1 | pp / study_id, data = prim, method = 'REML')
  rr <- robust(mm, cluster = prim$pp, clubSandwich = TRUE); cat(sprintf('   ML panel+estimate rule %s: r=%s (%s to %s) p=%.3f sigma2=%s\n', r, f(tanh(rr$b[1])), f(tanh(rr$ci.lb)), f(tanh(rr$ci.ub)), rr$pval, paste(round(mm$sigma2, 3), collapse = ', ')))
  allm$pp <- allm[[paste0('p', r)]]; m3 <- rma.mv(zi, vi, random = ~ 1 | pp / study_id / est_id, data = allm, method = 'REML')
  r3 <- robust(m3, cluster = allm$pp, clubSandwich = TRUE); cat(sprintf('   ML panel+study+estimate rule %s (k=%d): r=%s (%s to %s) p=%.3f\n', r, m3$k, f(tanh(r3$b[1])), f(tanh(r3$ci.lb)), f(tanh(r3$ci.ub)), r3$pval))
}
m2 <- rma.mv(zi, vi, random = ~ 1 | study_id / est_id, data = allm, method = 'REML'); r2 <- robust(m2, cluster = allm$study_id, clubSandwich = TRUE)
cat(sprintf('published multilevel CR2: r=%s (%s to %s)\n', f(tanh(r2$b[1])), f(tanh(r2$ci.lb)), f(tanh(r2$ci.ub))))
# Section 3.7 subgroups
ch <- prim$channels_tested != 'none tested'
cat('studies testing a channel:', sum(ch), '| of them Chinese:', sum(ch & prim$region == 'China'), '| Chinese not testing:', sum(!ch & prim$region == 'China'), '| non-Chinese testing:', sum(ch & prim$region != 'China'), '\n')
row('channel tested', rma(zi, vi, data = prim[ch, ], method = 'REML', test = 'knha'))
row('no channel tested', rma(zi, vi, data = prim[!ch, ], method = 'REML', test = 'knha'))
row('Chinese, no channel tested', rma(zi, vi, data = prim[!ch & prim$region == 'China', ], method = 'REML', test = 'knha'))
for (g in c('CN-province', 'CN-city', 'CN-firm')) { s <- prim[prim$pA == g, ]; m <- rma(zi, vi, data = s, method = 'REML', test = 'knha')
  row(g, m); cat(sprintf('   range r %s to %s, negative %d of %d, I2 %.2f%%, tau2 %.3f\n', f(min(tanh(s$zi))), f(max(tanh(s$zi))), sum(s$zi < 0), nrow(s), m$I2, m$tau2)) }
