"""One-off: config.json held regular expressions with single backslashes (invalid JSON). Double every backslash and check it parses."""
import json
p = r'D:\Research-Publishing\14-fintech-emissions-meta\bibliometrics\config.json'
t = open(p, encoding='utf-8').read()
BS = chr(92)
assert BS * 2 not in t, 'already escaped'
t2 = t.replace(BS, BS * 2)
d = json.loads(t2)
print(len(d['heatmap']['rows']), d['heatmap']['rows']['China (provinces)'])
open(p, 'w', encoding='utf-8').write(t2)
