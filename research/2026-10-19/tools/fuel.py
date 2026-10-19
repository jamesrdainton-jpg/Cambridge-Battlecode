import os as _os
from pathlib import Path as _Path
_HERE = _Path(__file__).resolve().parent
_ROOT = _HERE.parents[2]
_WORK = _Path(_os.environ.get("RS_WORK", str(_ROOT / "matches" / "research")))
import sys, struct
from pathlib import Path
sys.path.insert(0, str(_HERE))
from ourgames import games
sys.path.insert(0, str(_ROOT / "tools"))
import replay_decode as RD
ROOT = _ROOT
maps = {p.stem: p.read_bytes() for p in (ROOT / "maps").glob("*.map26a")}
for label, side, f in games(sys.argv[1:]):
    if side is None: continue
    fuel = f.get(f"team-{side}.fuel", b"")
    vals = [struct.unpack_from("<q", fuel, o)[0] for o in range(13, len(fuel) - 7, 8)][8:]
    big = [i for i, v in enumerate(vals[:12]) if v > 1_500_000]
    normal = vals[(big[-1] + 1) if big else 0:]
    m = RD.decode(f["replay.repl26a"], maps)["map"]
    over2 = sum(v > 2_000_000 for v in normal); over24 = sum(v > 2_400_000 for v in normal); cap = sum(v >= 2_499_000 for v in normal)
    if over2:
        print(f"{m:12} {label:7} turns {len(normal)} >2.0M {over2} >2.4M {over24} at cap {cap} max {max(normal)/1e6:.3f}M first turns {[round(v/1e6,2) for v in vals[:8]]}")
