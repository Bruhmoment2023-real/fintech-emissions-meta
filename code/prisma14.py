"""PRISMA 2020 flow counts and diagram for pack 14, computed from the logs (never typed by hand).
Inputs: data/raw/records_*.jsonl, data/clean/candidates.csv, screening/stage1_decisions.csv, screening/fulltext_queue_all.csv, data/fulltext_log.csv,
screening/stage2_decisions.txt, extraction/estimates.csv. Outputs: results/prisma_counts.json, results/figures/F0_prisma_flow.png, screening/stage0_rule_exclusions.csv"""
import os, json, glob, re
import pandas as pd
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
HERE = os.path.dirname(os.path.abspath(__file__)); os.chdir(HERE)
os.makedirs('../results/figures', exist_ok=True)
src = {}
for f in glob.glob('../data/raw/records_*.jsonl'):
    src[os.path.basename(f)[8:-6]] = sum(1 for _ in open(f, encoding='utf-8'))
cand = pd.read_csv('../data/clean/candidates.csv', dtype=str)
total_rows = sum(src.values()); unique = len(cand)
def nt(t): return re.sub(r'[^a-z0-9]+', ' ', str(t).lower()).strip()
cand['key'] = cand.apply(lambda r: r['doi'] if isinstance(r['doi'], str) and r['doi'] else 't:' + nt(r['title'])[:100], axis=1)
dec = pd.read_csv('../screening/stage1_decisions.csv', dtype=str)
rule = cand[cand.rule_exclude.notna() & ~cand.key.isin(dec.key)][['key', 'title', 'year', 'venue', 'sources', 'rule_exclude']]
rule.to_csv('../screening/stage0_rule_exclusions.csv', index=False)
rule_counts = rule.rule_exclude.value_counts().to_dict()
s1 = dec.reason_code.value_counts().to_dict()
inc = dec[dec.decision == 'include']
q = pd.read_csv('../screening/fulltext_queue_all.csv', dtype=str)
log = pd.read_csv('../data/fulltext_log.csv', dtype=str) if os.path.exists('../data/fulltext_log.csv') else pd.DataFrame(columns=['doi', 'status'])
s2 = {}
for l in open('../screening/stage2_decisions.txt', encoding='utf-8'):
    if l.strip() and not l.startswith('#'):
        p = l.strip().split('|'); s2[p[0].lower()] = (p[1], p[2] if len(p) > 2 else '')
est = pd.read_csv('../extraction/estimates.csv', dtype=str) if os.path.exists('../extraction/estimates.csv') else pd.DataFrame(columns=['study_id', 'primary'])
n_closed = int((q.is_oa.astype(str) != 'True').sum()); n_oa = int((q.is_oa.astype(str) == 'True').sum())
got = [x for x in log[log.status == 'ok'].doi.str.lower().tolist() if x in set(q.doi.str.lower())]; n_text = len(got)  # only records still included at stage 1
n_extracted = est.study_id.nunique()
ex2 = collections = {}
import collections as C
ex2 = C.Counter(v[1] for v in s2.values() if v[0] == 'excluded')
counts = dict(records_by_source=src, records_total=total_rows, unique_after_dedup=unique, duplicates_removed=total_rows - unique, rule_excluded=rule_counts, rule_excluded_total=int(len(rule)),
              hand_screened=len(dec), stage1_by_code=s1, stage1_included=len(inc), included_with_doi=len(q), included_without_doi=int(len(inc) - len(q)),
              fulltext_open_access_listed=n_oa, closed_or_unknown=n_closed, fulltext_retrieved=n_text, fulltext_not_retrieved_open=int(n_oa - n_text),
              stage2_excluded_by_code=dict(ex2), stage2_excluded_total=sum(ex2.values()), studies_extracted=int(n_extracted), estimates_extracted=int(len(est)))
json.dump(counts, open('../results/prisma_counts.json', 'w'), indent=1); print(json.dumps(counts, indent=1))
fig, ax = plt.subplots(figsize=(9, 11), dpi=200); ax.axis('off')
def box(x, y, w, h, t): ax.add_patch(plt.Rectangle((x, y), w, h, fill=False, lw=1.2)); ax.text(x + w / 2, y + h / 2, t, ha='center', va='center', fontsize=8)
box(0.1, 0.88, 0.45, 0.1, f"Records identified (rows returned)\nn = {total_rows:,}\n" + '; '.join(f'{k} {v:,}' for k, v in src.items()))
box(0.62, 0.88, 0.36, 0.1, f"Duplicates and versions merged\nn = {total_rows - unique:,}")
box(0.1, 0.72, 0.45, 0.1, f"Unique records screened\nn = {unique:,}")
box(0.62, 0.69, 0.36, 0.16, f"Rule-excluded (no text to read or no\nfintech / emissions term)\nn = {len(rule):,}")
box(0.1, 0.55, 0.45, 0.1, f"Records read by hand (title + abstract)\nn = {len(dec):,}")
box(0.62, 0.50, 0.36, 0.2 - 0.02, "Excluded after reading: " + str(len(dec) - len(inc)) + "\n" + '\n'.join(f"{k}: {v}" for k, v in s1.items() if k != 'I'))
box(0.1, 0.38, 0.45, 0.1, f"Included for full-text assessment\nn = {len(inc):,}\nopen full text listed {n_oa}; closed or unknown {n_closed + (len(inc) - len(q))}")
box(0.62, 0.30, 0.36, 0.14, f"No open full text retrieved\nn = {len(inc) - n_text:,}")
box(0.1, 0.22, 0.45, 0.1, f"Full texts read\nn = {n_text:,}")
box(0.62, 0.12, 0.36, 0.14, "Excluded at full text: " + str(sum(ex2.values())) + "\n" + '\n'.join(f"{k}: {v}" for k, v in sorted(ex2.items(), key=lambda x: -x[1])[:5]))
box(0.1, 0.05, 0.45, 0.1, f"Studies in the meta-analysis\nn = {n_extracted:,} studies, {len(est):,} estimates")
for (x1, y1, x2, y2) in [(0.325, 0.88, 0.325, 0.82), (0.55, 0.93, 0.62, 0.93), (0.325, 0.72, 0.325, 0.65), (0.55, 0.77, 0.62, 0.77), (0.325, 0.55, 0.325, 0.48), (0.55, 0.60, 0.62, 0.60), (0.325, 0.38, 0.325, 0.32), (0.55, 0.43, 0.62, 0.37), (0.325, 0.22, 0.325, 0.15), (0.55, 0.27, 0.62, 0.20)]:
    ax.annotate('', xy=(x2, y2), xytext=(x1, y1), arrowprops=dict(arrowstyle='->'))
ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.set_title('PRISMA 2020 flow: fintech and carbon emissions meta-analysis (counts computed from the logs)', fontsize=9)
plt.savefig('../results/figures/F0_prisma_flow.png', bbox_inches='tight'); print('figure ok')
