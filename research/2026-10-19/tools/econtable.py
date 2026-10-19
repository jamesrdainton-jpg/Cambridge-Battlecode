import os as _os
from pathlib import Path as _Path
_HERE = _Path(__file__).resolve().parent
_ROOT = _HERE.parents[2]
_WORK = _Path(_os.environ.get("RS_WORK", str(_ROOT / "matches" / "research")))
import re, os, sys
SP = str(_WORK / 'runs')
runs = sys.argv[1:]
data = {}
for r in runs:
    p = f'{SP}/{r}.txt'
    if not os.path.exists(p) or not os.path.getsize(p):
        continue
    d = {}
    for l in open(p):
        m = re.match(r'(\S+)\s+A=\S+\s+B=\S+\s+(.*?)\s+round=\s*(\d+) gems (\d+)-(\d+)', l)
        if m:
            d[m.group(1)] = (int(m.group(3)), int(m.group(4)))
    data[r] = d
maps = sorted(data[runs[0]])
names = [r.replace('_econ', '').replace('econ_', '').replace('rs_', '') for r in data]
print(f"{'map':12}" + "".join(f"{n[:9]:>10}" for n in names))
for m in maps:
    print(f"{m:12}" + "".join(f"{data[r].get(m, (0, 0))[0]:>10}" for r in data))
print(f"{'SUM':12}" + "".join(f"{sum(v[0] for v in data[r].values()):>10}" for r in data))
print(f"{'SUM-contest':12}" + "".join(f"{sum(v[0] for k, v in data[r].items() if k != 'contest'):>10}" for r in data))
base = data[runs[0]]
print(f"{'maps faster':12}" + "".join(f"{sum(1 for k, v in data[r].items() if k != 'contest' and v[0] < base[k][0]):>10}" for r in data))
