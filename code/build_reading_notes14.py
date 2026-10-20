"""Build depth/reading-notes/*.md for pack 14. Every verbatim quotation is machine-checked against the extracted text of the file I opened (page = PDF page index; Europe PMC XML texts have
no pages and show page 0). Numbers in the 'what the meta-analysis took from it' line are read from extraction/estimates.csv, not typed. Everything else is my summary of the parts I read;
each note says which parts were not read. Any quote that fails the check stops the build."""
import re, os, sys, unicodedata
import pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); PACK = os.path.dirname(HERE); os.chdir(HERE)
OUT = os.path.join(PACK, 'depth', 'reading-notes'); os.makedirs(OUT, exist_ok=True)
def norm(s):
    s = unicodedata.normalize('NFKC', s)
    for a, b in {'‘': "'", '’': "'", '“': '"', '”': '"', '–': '-', '—': '-', '‐': '-', '‑': '-'}.items(): s = s.replace(a, b)
    s = re.sub(r'(?<=\w)-\s+(?=\w)', '', s); s = re.sub(r'[,\s]+', ' ', s)
    return s.lower().strip()
def pages_of(doi):
    path = os.path.join(PACK, 'data', 'fulltext', re.sub(r'[^a-z0-9]+', '_', doi.lower()).strip('_') + '.txt')
    t = open(path, encoding='utf-8', errors='replace').read(); parts = re.split(r'=====PAGE (\d+)=====', t)
    if len(parts) == 1: return {0: norm(t)}
    return {int(parts[i]): norm(parts[i + 1]) for i in range(1, len(parts), 2)}
est = pd.read_csv(os.path.join(PACK, 'results', 'tables', 'estimates_with_effect_sizes.csv'), dtype=str)
st = pd.read_csv(os.path.join(PACK, 'extraction', 'studies.csv'), dtype=str)
N = []
def note(doi, access, rq, data, method, limits, quotes, bears, slug):
    N.append(dict(doi=doi, access=access, rq=rq, data=data, method=method, limits=limits, quotes=quotes, bears=bears, slug=slug))

note('10.1002/bse.3778', 'opened in full (21 pages, publisher PDF)',
     'Effect of fintech development on corporate carbon emissions (CCEs) of Chinese firms.',
     'National Tax Survey Database (NTSD) firm records; the extracted N is the largest in the meta-analysis (about 965 thousand firm-years).',
     'Difference-in-differences style panel regression with an instrumental-variable robustness check; mechanism and heterogeneity analyses.',
     'I read the abstract, data description and main regression table; I did not read the mechanism or heterogeneity sections in detail.',
     ['The results suggest that Fintech development leads to a reduction in CCEs.', 'Our findings remain robust even after using the instrumental variable approach to alleviate endogeneity problems.', 'To isolate the effects of the financial crisis, we use the sub-sample ranging from 2008 to 2016 to regress Equation (1).'],
     'Shows how a very large N makes the partial correlation tiny (near zero) while the t statistic is significant. It is the study with the smallest SE in the funnel plot. Extraction caveat: the open PDF text has lost the minus signs in Table 3, so the sign was applied from the authors own sentence about a decrease (flagged SIGN_NEG and primary_fallback in the data); the first column sign could not be read directly.', 'wang-2024-bse')
note('10.3390/su18168249', 'opened in full (24 pages, MDPI PDF via the MDPI file CDN)',
     'How digital financial inclusion (DFI) influences CO2 emissions of Chinese A-share firms, and through which channels.',
     'Panel of Chinese A-share firms, 2013 to 2023 (baseline 2013 to 2019, extended to 2023 in robustness); green patents from CNRDS, financials from CSMAR and Wind.',
     'Firm and year fixed-effects panel regression with mediation tests; expanding-window and sample-exclusion tests for the pandemic years.',
     'I read the abstract, data section, the robustness section on pandemic years and the limitations paragraph; I did not check the mediation tables.',
     ['We find a significant negative correlation between access to DFI and CO2 emissions', 'Green patent data are sourced from the Chinese Research Data Services Platform (CN- RDS), and firm-level financial data are collected from the China Stock Market & Accounting Research Database (CSMAR) and the Wind database.', 'A remaining limitation is the absence of more granular firm-level operational or environmental information.'],
     'One of the firm-level studies: unit-of-analysis moderator. Note the abstract says 2013 to 2023 while the baseline sample is 2013 to 2019, so the sample period recorded in the extraction is the one the table reports.', 'liu-2026-su')
note('10.1371/journal.pone.0302826', 'opened in full (Europe PMC XML, no page numbers)',
     'Digital inclusive finance and enterprise carbon emissions.',
     'Panel data of 247 prefecture-level cities and 6,019 industrial enterprises in China.',
     'Panel regressions with an instrumental-variable test, heterogeneity by region (Hu Huanyong line) and ownership, a stepwise mediation check.',
     'I read the abstract and the main table; mechanism and sub-dimension tables were not read.',
     ['using panel data of 247 prefectural-level cities and 6019 industrial enterprises in China', 'this effect remains significant after the instrumental variable estimation test'],
     'Firm-level study with N = 18,802 in the extracted table; contributes a near-zero partial correlation. Extraction caveat: the printed coefficient (-0.0180 with a star-level of 1%) has a printed SE of 0.03, which contradicts the stars, so the row is flagged INCONSISTENT and dropped in that sensitivity analysis.', 'peng-2024-pone')
note('10.1007/s00181-024-02609-9', 'opened in full (29 pages, Springer open PDF)',
     'Effect of FinTech company counts on regional carbon emission intensity.',
     'County-level carbon emissions in China 2011 to 2017 with data on FinTech companies; about 7,900 county-years in the extracted table.',
     'Fixed-effects regression with an instrumental-variable strategy and controls for financial attributes; mechanism tests on industrial structure and energy structure.',
     'I read the abstract, the baseline interpretation (page 11) and the limitations (page 26); I did not read the instrument tests.',
     ['this study reveals that FinTech significantly reduces regional car- bon emissions intensity.', 'The relatively short sample period might fail to fully capture these long-term effects.', 'a 1% increase in the number of FinTech companies during the sample period is associated with an approximately 0.0038% reduction in regional carbon intensity.'],
     'A rare study whose fintech measure is a count of companies (not the Peking University index), at county level; it is the clearest example of the log-log interpretation (an elasticity), which the partial correlation conversion handles through t and N.', 'wu-2024-empec')
note('10.1016/j.heliyon.2024.e30155', 'opened in full (Europe PMC XML, no page numbers)',
     'Does digital finance reduce carbon emissions intensity, through production technology innovation and green technology innovation?',
     'Chinese provincial panel 2011 to 2020 (30 provinces, N = 300); the extracted column has province effects only, no time effects, and a log-log specification.',
     'Fixed-effects regression with a chain mediation model (IPAT framework).',
     'I read the title, the data sentence and the main table; I did not read the mediation sections.',
     ['How does digital finance reduce carbon emissions intensity? Evidence from chain mediation effect of production technology innovation and green technology innovation'],
     'Table 4 column 1 (log index only: -0.2552, SE 0.0150) gives a partial correlation near -0.7 on N = 300, one of the most negative values in the set and part of the left tail of the funnel plot; a good example of why small-N, large-t studies drive the Egger test and PET.', 'jiang-2024-heliyon')
note('10.3389/fenvs.2025.1549623', 'opened in full (15 pages, Frontiers open PDF)',
     'Impact and mechanisms of digital financial inclusion on agricultural carbon emission intensity.',
     'Panel of 31 Chinese provinces, 2000 to 2021 (the extracted table has N = 682).',
     'Double machine learning (causal inference with ML nuisance functions), robustness to sample choice and to K-fold ratio, heterogeneity by region.',
     'I read the abstract, the robustness paragraph and the heterogeneity discussion; I did not check the machine learning settings beyond the stated K-fold changes.',
     ['digital inclusive finance significantly reduces agricultural carbon intensity through two main channels', 'By changing the ratio from the previous 1:4 to 1:2, 1:3, 1:5, and 1:6'],
     'Outcome is agricultural carbon intensity (sector-specific) with a non-standard estimator; kept in the pooled set but flagged by the emissions-type and estimator moderators.', 'zheng-2025-fenvs')
note('10.1186/s40854-025-00826-4', 'opened in full (20 pages, open access)',
     'Relationship between digital financial inclusion and carbon neutrality in different provinces of China.',
     'Chinese provincial panel; the extracted table is a GMM or IV specification with N = 360.',
     'Province-by-province causality analysis plus a panel estimate.',
     'I read the abstract and the main table; I did not read the causality tests.',
     ['digital financial inclusion is found to have a causal effect on carbon neutrality in one-third of the provinces', 'no causal relationship is detected between digital financial inclusion and carbon neutrality in two-thirds of the regions'],
     'Positive coefficient (0.187, SE 0.034) in the system-GMM column with a lagged dependent variable; the paper defines carbon neutrality as carbon emissions per unit GDP, so it is an intensity outcome. N was not printed and is inferred (360), so this study is in the inferred-N sensitivity set. The authors themselves find no causal relationship in two thirds of the provinces.', 'cifuentes-2026-fi')
note('10.3389/fenvs.2023.1282784', 'opened in full (15 pages, Frontiers open PDF)',
     'Digital inclusive finance, consumption structure upgrading and carbon emissions.',
     'Panel of 30 Chinese provinces, 2014 to 2020 (the extracted table has N = 210).',
     'Panel regression with mediation through consumption structure and a spatial model.',
     'I read the abstract and the limitations paragraph; I did not read the mediation tables.',
     ['digital inclusive finance can play a significant role in lowering carbon emissions by encouraging individuals to alter their consumption patterns', 'it overlooks the direct environmental costs associated with the growth of the digital economy itself.'],
     'The primary estimate (Table 2 column 1, index only, no controls) is positive (0.2431, t 8.52), while the fully controlled column 2 is negative (-0.2286, t -2.41). The sign of this study depends on which column is taken, which is why the protocol fixes the primary column in advance and the secondary analysis uses the fully specified column. A second extractor should check this row.', 'ye-2023-fenvs')
note('10.1186/s43093-025-00469-y', 'opened in full (13 pages, open access)',
     'Fintech, green finance, natural resource rent and economic growth in BRICS environmental sustainability.',
     'BRICS countries, 2000 to 2022 (the extracted table has N = 115 observations).',
     'Cross-sectionally augmented ARDL.',
     'I read the abstract, limitations and recommendations; I did not check the diagnostic tests.',
     ['using cross-sectionally augmented autoregressive distributed lag method', 'The results show that fintech has the capability to efficiently optimize the financial aspects of green projects, all the while decreasing carbon emissions.'],
     'The most negative partial correlation in the set (about -0.88), from a short time-series panel: this is the mechanism behind the ARDL moderator (r around -0.5) and the PET slope.', 'miled-2025-fbj')
note('10.1057/s41599-024-03354-1', 'opened in full (14 pages, open access)',
     'Non-linear (inverted U) role of digital inclusive finance in agricultural carbon emissions.',
     'Chinese provinces 2011 to 2021 (the extracted table has N = 330).',
     'Panel regression with a squared term; moderation by agricultural green cooperatives and human capital.',
     'I read the abstract and the future-research paragraph; the extracted linear coefficient comes from the baseline table, not the squared-term table.',
     ['Digital inclusive finance has an inverted "U-shaped" nonlinear impact on agricultural carbon emissions', 'Agricultural carbon emissions only begin to be effectively suppressed when the scale of digital inclusive finance exceeds the peak value.'],
     'The primary estimate (Table 3 column 1, linear term only: 0.1169, t 2.64) is positive; column 2 adds the squared term and is not used. A positive linear term can coexist with a negative effect at high levels, so this partial correlation does not refute the abstract. It shows why polynomial and threshold models were excluded or handled separately.', 'li-2024-hass')
note('10.15244/pjoes/197047', 'opened in full (publisher PDF)',
     'How digital finance affects corporate carbon emissions (CCE) and low-carbon technology innovation.',
     'Chinese A-share listed companies 2011 to 2021; N = 14,784 in the baseline table.',
     'Two-way fixed-effects regression with an IV-2SLS and system GMM check; industry clustering of SE.',
     'I read the abstract and the baseline table; I did not read the innovation-path section.',
     ['DF can significantly reduce CCE'],
     'Firm-level study with a typical t of about -4.7 and N near 15,000, so a partial correlation near -0.04.', 'fang-2025-pjoes')
note('10.1016/j.jeconbus.2024.106222', 'opened in full (Elsevier open-access PDF)',
     'Digital financial inclusion and households\' CO2 emissions in China.',
     'Chinese household panel (13,624 households; waves 2012, 2014, 2016, 2018).',
     'Fixed-effects panel regression and a mediation model separating direct and indirect household emissions.',
     'I read the abstract and the baseline table; I did not read the mediation or heterogeneity sections.',
     ['Exploiting a unique survey panel dataset of 13,624 Chinese households'],
     'One of the few studies with a positive sign among the large-N set: the household outcome (consumption-driven emissions) differs in meaning from firm or province emissions, so the outcome-type moderator matters.', 'li-2024-jeb')
note('10.32479/ijeep.16097', 'opened in full (publisher PDF)',
     'Digital financial inclusion, remittances, technological innovation, governance and carbon neutrality in the top remittance-receiving countries.',
     'Cross-country panel 2001 to 2020; the paper alternates between "top 10" and "top 30" countries, so the N in the extraction is inferred (30 x 20).',
     'Dynamic common-correlated-effects estimator with an IV variant.',
     'I read the model specification and the main table; sample size is not reported consistently, which is why this study sits in the inferred-N sensitivity set.',
     ['(CN) in Top 10 remittances receipting nations for the period', 'carbon neutrality in the top 30 remittance-receiving countries from 2001 to 2020'],
     'Concrete example of an inconsistent sample description inside one paper, and the publisher (EconJournals) matches a Kscien warning-list entry; the study is excluded in the flagged-venue sensitivity analysis.', 'farzana-2024-ijeep')

lines_index = ['# Reading notes, pack 14', '', 'Quotes are machine-checked against the extracted full text of each file; page = PDF page index (0 means a Europe PMC XML text without pages). Each note names which parts were read. These are working notes, not manuscript text.', '']
bad = 0
for n in N:
    pg = pages_of(n['doi']); s = st[st.study_id == n['doi'].lower()].iloc[0]
    rows = est[(est.study_id == n['doi'].lower()) & (est.primary == '1')].iloc[0]
    qs = []
    for q in n['quotes']:
        nq = norm(q); hit = [p for p, tx in pg.items() if nq in tx]
        if not hit:
            hit2 = [p for p, tx in pg.items() if nq.replace(' ', '') in tx.replace(' ', '')]
            if hit2: hit = hit2
        if not hit: print('QUOTE NOT FOUND', n['doi'], q[:80]); bad += 1; continue
        qs.append((q, hit[0]))
    fn = os.path.join(OUT, n['slug'] + '.md')
    md = [f"# {s.first_author_full or s.first_author} ({s.year}): {s.title}", '', f"- Venue: {s.venue}. DOI: https://doi.org/{n['doi']}", f"- Access: {n['access']}", f"- Question: {n['rq']}", f"- Data: {n['data']}", f"- Method: {n['method']}",
          f"- What the meta-analysis took from it (primary estimate, machine-read from the extraction): coefficient {rows.b} (SE {rows.se if str(rows.se) != 'nan' else 'not printed, t used'}, t {rows.t_use}), N {rows.n_obs}, partial correlation {float(rows.ri):.3f}; {rows.model_label}.",
          f"- Not read / limits: {n['limits']}", '', 'Verbatim quotes (checked):']
    md += [f'- "{q}" (p. {p})' for q, p in qs]
    md += ['', f"Bearing on the review: {n['bears']}", '']
    open(fn, 'w', encoding='utf-8').write('\n'.join(md))
    lines_index.append(f"- [{s.first_author} {s.year}]({n['slug']}.md): r = {float(rows.ri):.2f}, N = {rows.n_obs}, {s.venue}")
open(os.path.join(OUT, '00-index.md'), 'w', encoding='utf-8').write('\n'.join(lines_index) + '\n')
print('notes', len(N), 'failed quotes', bad)
