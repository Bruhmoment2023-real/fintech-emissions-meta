"""Write bibliometrics/data/clean/evidence_notes.csv for the evidence table: for each of the top-ranked papers, how it relates to the meta-analysis, read from the screening and extraction logs
(never invented). Run after `python evidence.py` has written the draft evidence-table.csv; then run `python evidence.py` again."""
import os, re, csv
import pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); PACK = os.path.dirname(HERE); BIB = os.path.join(PACK, 'bibliometrics')
ev = pd.read_csv(os.path.join(BIB, 'evidence-table.csv'), encoding='utf-8-sig', dtype=str).fillna('')
est = pd.read_csv(os.path.join(PACK, 'results', 'tables', 'estimates_with_effect_sizes.csv'), dtype=str); est = est[est.primary == '1'].set_index('study_id')
dec1 = pd.read_csv(os.path.join(PACK, 'screening', 'stage1_decisions.csv'), dtype=str).set_index('key')
s2 = {}
for l in open(os.path.join(PACK, 'screening', 'stage2_decisions.txt'), encoding='utf-8'):
    if l.strip() and not l.startswith('#'):
        p = l.strip().split('|'); s2[p[0].lower()] = (p[1], p[2] if len(p) > 2 else '', p[3] if len(p) > 3 else '')
log = {r['doi'].lower(): r['status'] for r in csv.DictReader(open(os.path.join(PACK, 'data', 'fulltext_log.csv'), encoding='utf-8'))}
rows = []
for _, r in ev.iterrows():
    doi = re.sub(r'^https?://doi.org/', '', r['doi_or_arxiv']).lower()
    n = dict(id=r['id'], study_type='', data='', models='', method='', read_status='', relation='')
    if doi in est.index:
        e = est.loc[doi]
        n.update(study_type='empirical panel regression (in the meta-analysis)', method=f"{e.estimator}; unit {e.unit}; {e.period}", read_status='abstract read; main results table opened in full text',
                 relation=f"Included in the meta-analysis: primary estimate r = {float(e.ri):.3f}, N = {e.n_obs}, outcome {e.emissions_type}, fintech measure {e.fintech_measure}.")
    elif doi in s2 and s2[doi][0] == 'excluded':
        n.update(read_status='full text opened', relation=f"Excluded at full text, code {s2[doi][1]}: {s2[doi][2]}")
    elif doi in dec1.index:
        d = dec1.loc[doi]
        if d.decision == 'include':
            n.update(read_status=('abstract read' if r['read_status'] == 'abstract read' else 'title only (no abstract available)'), relation='Passed the title and abstract screen; no open full text was retrieved, so it is not in the meta-analysis' + ('' if log.get(doi) != 'ok' else ' (text retrieved)'))
        else:
            n.update(relation=f"Excluded at title and abstract, code {d.reason_code}: {d.reason}")
    else:
        n.update(relation='Not hand-screened: an OpenAlex hit that passed the lexical fintech and emissions test; read only by title and abstract here.')
    rows.append(n)
out = os.path.join(BIB, 'data', 'clean', 'evidence_notes.csv')
pd.DataFrame(rows).to_csv(out, index=False, encoding='utf-8-sig'); print('wrote', out, len(rows))
print(pd.Series([x['relation'][:20] for x in rows]).value_counts().to_string())
