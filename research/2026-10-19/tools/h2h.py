"""Seeded head-to-head, gauntlet-style: seeded copies of A and B (tools/variant.py --set SEED), every map from
both sides, all seeds in one run-batch. Prints per-seed and total wins and STAT gem margins, per-map wins.
Usage: python h2h.py OUT A B --seeds 1,2 [--maps m1,m2] [--jobs 4]"""
import os as _os
from pathlib import Path as _Path
_HERE = _Path(__file__).resolve().parent
_ROOT = _HERE.parents[2]
_WORK = _Path(_os.environ.get("RS_WORK", str(_ROOT / "matches" / "research")))
import argparse
import re
import subprocess
import sys
import zipfile
from collections import Counter
from pathlib import Path

ROOT = _ROOT
SP = _WORK
RESULT = re.compile(r"\[\+\]\s+(.*?)\s{2,}(\S+) vs (\S+)\s+(\S+)\s+Round (\d+)/\d+")
PY = str(ROOT / ".venv/bin/python")


def stat(bundle, team):
    try:
        with zipfile.ZipFile(bundle) as z:
            t = z.read(f"team-{team}.stdout").decode(errors="replace").replace("\x00", "")
    except Exception:
        return None
    found = None
    for line in t.splitlines():
        if line.startswith("STAT "):
            p = line.split()
            found = (int(p[1]), int(p[2]), int(p[3]))
    return found


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("a")
    ap.add_argument("b")
    ap.add_argument("--seeds", default="1,2")
    ap.add_argument("--maps", default="")
    ap.add_argument("--jobs", type=int, default=4)
    args = ap.parse_args()
    maps = args.maps.split(",") if args.maps else sorted(p.stem for p in (ROOT / "maps").glob("*.map26a"))
    seeds = args.seeds.split(",")
    pairs = []
    for s in seeds:
        na, nb = f"{args.a}_s{s}", f"{args.b}_s{s}"
        for src, dst in ((args.a, na), (args.b, nb)):
            subprocess.run([PY, str(ROOT / "tools/variant.py"), dst, "--src", src, "--set", f"bot.py:SEED = 0=>SEED = {s}"],
                           cwd=ROOT, check=True, stdout=subprocess.DEVNULL)
        pairs.append((s, na, nb))
    base = SP / "runs" / args.out
    base.mkdir(parents=True, exist_ok=True)
    for old in base.glob("*.repl26a"):
        old.unlink()
    games = []
    for s, na, nb in pairs:
        for m in maps:
            games.append((s, na, nb, m, f"{m}-s{s}-1.repl26a"))
            games.append((s, nb, na, m, f"{m}-s{s}-2.repl26a"))
    man = base / "manifest.txt"
    man.write_text("".join(f"{ROOT}/bots/{a} {ROOT}/bots/{b} {ROOT}/maps/{m}.map26a {base}/{r}\n" for s, a, b, m, r in games))
    proc = subprocess.run([str(ROOT / ".venv/bin/cambc"), "run-batch", str(man), "--jobs", str(args.jobs), "--color", "never",
                           "--log-limit", "40000000"], cwd=ROOT, capture_output=True, text=True)
    out = proc.stdout + proc.stderr
    (base / "batch.log").write_text(out)
    res = {}
    for line in out.splitlines():
        mm = RESULT.search(line)
        if mm:
            st, a, b, mp, rnd = mm.groups()
            res[(Path(a).name, Path(b).name, mp)] = (st, int(rnd))
    per_seed = Counter()
    margin = Counter()
    per_map = Counter()
    missing = 0
    for s, a, b, m, r in games:
        st, rnd = res.get((a, b, m), ("MISSING", 0))
        if st == "MISSING":
            missing += 1
            continue
        a_is_A = a.startswith(args.a + "_s")
        winner_is_A = ("TEAM A WIN" in st) == a_is_A
        if "WIN" in st and winner_is_A:
            per_seed[s] += 1
            per_map[m] += 1
        sa = stat(base / r, "a") or (lambda x: (x[0], x[2], x[1]) if x else None)(stat(base / r, "b"))
        if sa:
            ga, gb = sa[1], sa[2]
            margin[s] += (ga - gb) if a_is_A else (gb - ga)
    n_per_seed = 2 * len(maps)
    tot_w = sum(per_seed.values())
    tot_m = sum(margin.values())
    print(f"{args.a} vs {args.b}: " + "  ".join(f"seed {s}: {per_seed[s]}/{n_per_seed} ({margin[s]:+d})" for s in seeds)
          + f"  TOTAL {tot_w}/{n_per_seed * len(seeds)} ({tot_m:+d})" + (f"  MISSING {missing}" if missing else ""))
    print("  wins by map:", " ".join(f"{m}:{per_map[m]}/{2 * len(seeds)}" for m in maps))


if __name__ == "__main__":
    main()
