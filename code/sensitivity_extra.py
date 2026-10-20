"""Extra sensitivity rows for Table 3 of the fintech-emissions meta-analysis, in pure Python (no packages).
Random effects, REML tau^2, Knapp-Hartung CI; checked against the pack's metafor output.
Usage: python -I sensitivity_extra.py <estimates_with_effect_sizes.csv>
Prints: k, r, 95% CI low, high for each row. Cluster rows print the number of clusters first."""
import csv, sys, math, re

def betacf(a, b, x):
    qab, qap, qam = a + b, a + 1, a - 1
    c, d = 1.0, 1 - qab * x / qap
    d = 1 / (d if abs(d) > 1e-30 else 1e-30); h = d
    for m in range(1, 300):
        m2 = 2 * m
        aa = m * (b - m) * x / ((qam + m2) * (a + m2))
        d = 1 + aa * d; d = 1 / (d if abs(d) > 1e-30 else 1e-30)
        c = 1 + aa / c; c = c if abs(c) > 1e-30 else 1e-30; h *= d * c
        aa = -(a + m) * (qab + m) * x / ((a + m2) * (qap + m2))
        d = 1 + aa * d; d = 1 / (d if abs(d) > 1e-30 else 1e-30)
        c = 1 + aa / c; c = c if abs(c) > 1e-30 else 1e-30; de = d * c; h *= de
        if abs(de - 1) < 1e-12: break
    return h

def ibeta(a, b, x):
    if x <= 0: return 0.0
    if x >= 1: return 1.0
    lb = math.lgamma(a + b) - math.lgamma(a) - math.lgamma(b) + a * math.log(x) + b * math.log(1 - x)
    if x < (a + 1) / (a + b + 2): return math.exp(lb) * betacf(a, b, x) / a
    return 1 - math.exp(lb) * betacf(b, a, 1 - x) / b

def tcdf(t, df): return 1 - 0.5 * ibeta(df / 2, 0.5, df / (df + t * t)) if t > 0 else 0.5 * ibeta(df / 2, 0.5, df / (df + t * t))
def tq(p, df):
    lo, hi = 0.0, 100.0
    for _ in range(200):
        mid = (lo + hi) / 2
        if tcdf(mid, df) < p: lo = mid
        else: hi = mid
    return (lo + hi) / 2

def reml(y, v):
    tau = 0.0
    for _ in range(5000):
        w = [1 / (vi + tau) for vi in v]; sw = sum(w)
        mu = sum(wi * yi for wi, yi in zip(w, y)) / sw
        new = max(0.0, sum(wi * wi * ((yi - mu) ** 2 - vi) for wi, yi, vi in zip(w, y, v)) / sum(wi * wi for wi in w) + 1 / sw)
        if abs(new - tau) < 1e-12: return new
        tau = new
    return tau

def re_kh(y, v):
    k = len(y); tau = reml(y, v)
    w = [1 / (vi + tau) for vi in v]; sw = sum(w)
    mu = sum(wi * yi for wi, yi in zip(w, y)) / sw
    q = sum(wi * (yi - mu) ** 2 for wi, yi in zip(w, y)) / (k - 1)
    se = math.sqrt(q / sw); c = tq(0.975, k - 1) * se
    return k, math.tanh(mu), math.tanh(mu - c), math.tanh(mu + c), tau, w, mu

def cluster_robust(y, v, cl):
    k, r, lo, hi, tau, w, mu = re_kh(y, v)
    sw = sum(w); C = len(set(cl))
    s = {}
    for wi, yi, ci in zip(w, y, cl): s[ci] = s.get(ci, 0) + wi * (yi - mu)
    var = (C / (C - 1)) * sum(x * x for x in s.values()) / sw ** 2
    c = tq(0.975, C - 1) * math.sqrt(var)
    return C, math.tanh(mu), math.tanh(mu - c), math.tanh(mu + c)

rows = [x for x in csv.DictReader(open(sys.argv[1], encoding='utf-8')) if x['primary'] == '1']
F = lambda x, k: float(x[k])
y = [F(x, 'zi') for x in rows]; v = [F(x, 'vi') for x in rows]
print('primary', [round(z, 3) for z in re_kh(y, v)[:4]])
# same 34 studies (n_units > 8), standard df and units df
pu = [x for x in rows if x['n_units'] not in ('', 'NA') and float(x['n_units']) > 8]
print('34 with N df', [round(z, 3) for z in re_kh([F(x, 'zi') for x in pu], [F(x, 'vi') for x in pu])[:4]])
def zu(x):
    t = F(x, 't_use'); df = float(x['n_units']) - F(x, 'k_used') - 1
    r = t / math.sqrt(t * t + df); return math.atanh(r), 1 / (float(x['n_units']) - F(x, 'k_used') - 3)
pu2 = [x for x in pu if float(x['n_units']) - F(x, 'k_used') - 3 > 0]
print('units-df usable', len(pu2))
zz = [zu(x) for x in pu2]
print('34 with units df', [round(z, 3) for z in re_kh([a for a, b in zz], [b for a, b in zz])[:4]])
ch = [x for x in rows if x['region'] == 'China']
print('China only', [round(z, 3) for z in re_kh([F(x, 'zi') for x in ch], [F(x, 'vi') for x in ch])[:4]])
nch = [x for x in rows if x['region'] != 'China']
print('outside China', [round(z, 3) for z in re_kh([F(x, 'zi') for x in nch], [F(x, 'vi') for x in nch])[:4]])
pat = re.compile(r'PKU|Peking|inclusive finance|financial inclusion|DFI|DIF', re.I)
def clus(x):
    if x['region'] == 'China' and x['unit'] in ('province', 'city') and pat.search(x['fintech_measure']):
        return 'CN-index-' + x['unit']
    return x['study_id']
cl = [clus(x) for x in rows]
print('clusters', len(set(cl)), sum(c.startswith('CN-index') for c in cl), {c: cl.count(c) for c in set(cl) if c.startswith('CN')})
print('cluster CR1 (index x unit)', [round(z, 3) for z in cluster_robust(y, v, cl)])
cl2 = ['CN-index' if c.startswith('CN-index') else c for c in cl]
print('cluster CR1 (one index cluster)', [round(z, 3) for z in cluster_robust(y, v, cl2)])
