"""Create bots/rs_mapdump from bots/probe: during the draft it prints the map, altars, spawns, groups and every camp's
engine handle (CAMPH lines), which targets.py uses to map replay camp ids to camp kinds and tiles.
Then run:  python runner.py dumps rs_mapdump idle --one-side --rounds 1   and   python mk_mapdump.py --extract"""
import os as _os
import shutil
import sys
import zipfile
from pathlib import Path as _Path
_HERE = _Path(__file__).resolve().parent
_ROOT = _HERE.parents[2]
_WORK = _Path(_os.environ.get("RS_WORK", str(_ROOT / "matches" / "research")))
if "--extract" in sys.argv:
    d = _WORK / "runs" / "dumps"
    for f in sorted(d.glob("*.repl26a")):
        m = f.name.rsplit("-", 1)[0]
        (d / f"{m}.txt").write_text(zipfile.ZipFile(f).read("team-a.stdout").decode(errors="replace").replace("\x00", ""))
    print("extracted", len(list(d.glob("*.txt"))), "dumps")
    sys.exit()
dst = _ROOT / "bots" / "rs_mapdump"
if dst.exists():
    shutil.rmtree(dst)
shutil.copytree(_ROOT / "bots" / "probe", dst, ignore=shutil.ignore_patterns(".cambc"))
p = dst / "src" / "main.py"
s = p.read_text()
s = s.replace("                    dump()\n                    pass\n", "                    dump()\n")
s = s.replace('    print("fuel after dump", cambc.fuel_remaining(), flush=True)\n',
              '''    for g in game_map.camp_groups():
        for c in g.camps():
            sp = c.spawn_position()
            print(f"CAMPH {int(c)} {'wegGM'[c.kind()]} {sp.x} {sp.y} {int(g)}")
    print("fuel after dump", cambc.fuel_remaining(), flush=True)
''')
assert "CAMPH" in s and "                    dump()\n" in s
p.write_text(s)
print("created", dst)
