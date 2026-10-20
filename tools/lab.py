"""Seeded economy and head-to-head runs in one cambc run-batch, with per-map tables.

Usage:
  python tools/lab.py econ BOT [BOT...] [--seeds 1,2] [--maps m1,m2] [--jobs 8]
      Each BOT (seeded copies, made with tools/variant.py) vs idle, BOT as team A, every map. Prints mean rounds
      to 1,000 per map and the sum (a game that misses 1,000 counts as 2,000).
  python tools/lab.py h2h A B [--seeds 1,2] [--maps m1,m2] [--jobs 8]
      Seeded copies of A vs seeded copies of B (same seed on both sides), every map from both sides. Prints A's
      wins and STAT gem margin per map, per seed and in total.

Replays go to matches/lab/<name>/ (not in git). Both modes need the bots' SEED hook ("SEED = 0" in bot.py).
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
import zipfile
from collections import defaultdict
from pathlib import Path

from common import find_cambc

ROOT = Path(__file__).resolve().parent.parent
CAMBC = find_cambc()
RESULT = re.compile(r"\[\+\]\s+(.*?)\s{2,}(\S+) vs (\S+)\s+(\S+)\s+Round (\d+)/\d+")


def seeded(bot: str, seed: str) -> str:
    if seed == "0":
        return bot
    name = f"{bot}_s{seed}"
    src = ROOT / "bots" / bot / "src" / "bot.py"
    if "SEED = 0" not in src.read_text():
        raise SystemExit(f"{bot} has no SEED hook")
    subprocess.run([sys.executable, str(ROOT / "tools" / "variant.py"), name, "--src", bot,
                    "--set", f"bot.py:SEED = 0=>SEED = {seed}"], cwd=ROOT, check=True, stdout=subprocess.DEVNULL)
    return name


def last_stat(bundle: Path, team: str):
    try:
        with zipfile.ZipFile(bundle) as z:
            text = z.read(f"team-{team}.stdout").decode(errors="replace").replace("\x00", "")
    except (OSError, KeyError, zipfile.BadZipFile):
        return None
    found = None
    for line in text.splitlines():
        line = line.strip()
        if line.startswith("STAT "):
            p = line.split()
            if len(p) >= 4:
                found = (int(p[1]), int(p[2]), int(p[3]))
    return found


def run(name: str, games: list[tuple[str, str, str]], jobs: int) -> dict:
    """games: (team A bot, team B bot, map). Returns {(a, b, map): (status, round, gems_a, gems_b)}."""
    base = ROOT / "matches" / "lab" / name
    base.mkdir(parents=True, exist_ok=True)
    for old in base.glob("*.repl26a"):
        old.unlink()
    lines = []
    files = {}
    for i, (a, b, m) in enumerate(games):
        rep = f"{i:03d}-{m}.repl26a"
        files[(a, b, m)] = base / rep
        lines.append(f"../../../bots/{a} ../../../bots/{b} ../../../maps/{m}.map26a {rep}\n")
    manifest = base / "manifest.txt"
    manifest.write_text("".join(lines))
    proc = subprocess.run([CAMBC, "run-batch", str(manifest), "--jobs", str(jobs), "--color", "never"],
                          cwd=ROOT, capture_output=True, text=True)
    out = proc.stdout + proc.stderr
    (base / "batch.log").write_text(out)
    status = {}
    for line in out.splitlines():
        mt = RESULT.search(line)
        if mt:
            st, a, b, mp, rnd = mt.groups()
            status.setdefault((a, b, mp), (st, int(rnd)))
    if "FAILED" in out or "failed" in out.split("Finished:")[-1].split("\n")[0].replace(" 0 failed", ""):
        print("WARNING: some games failed, see", base / "batch.log")
    res = {}
    for key, bundle in files.items():
        st, rnd = status.get(key, ("MISSING", 0))
        sa = last_stat(bundle, "a")
        sb = last_stat(bundle, "b")
        if sa:
            ga, gb = sa[1], sa[2]
        elif sb:
            ga, gb = sb[2], sb[1]
        else:
            ga = gb = 0
        res[key] = (st, rnd, ga, gb)
    return res


def all_maps() -> list[str]:
    return sorted(p.stem for p in (ROOT / "maps").glob("*.map26a"))


def econ(args) -> None:
    maps = args.maps.split(",") if args.maps else all_maps()
    seeds = args.seeds.split(",")
    games = []
    names = {}
    for bot in args.bots:
        for s in seeds:
            sb = seeded(bot, s)
            names[sb] = bot
            for m in maps:
                games.append((sb, "idle", m))
    res = run("econ-" + "-".join(args.bots), games, args.jobs)
    table = defaultdict(list)
    for (a, _, m), (st, rnd, ga, _) in res.items():
        table[(names[a], m)].append(rnd if "TEAM A WIN" in st else 2000)
    print(f"{'map':12}" + "".join(f"{b[:10]:>11}" for b in args.bots))
    totals = defaultdict(float)
    for m in maps:
        row = f"{m:12}"
        for b in args.bots:
            v = table[(b, m)]
            mean = sum(v) / len(v)
            totals[b] += mean
            row += f"{mean:>11.0f}"
        print(row)
    print(f"{'SUM':12}" + "".join(f"{totals[b]:>11.0f}" for b in args.bots))


def h2h(args) -> None:
    maps = args.maps.split(",") if args.maps else all_maps()
    seeds = args.seeds.split(",")
    games = []
    pairs = []
    for s in seeds:
        a, b = seeded(args.bots[0], s), seeded(args.bots[1], s)
        pairs.append((s, a, b))
        for m in maps:
            games.append((a, b, m))
            games.append((b, a, m))
    res = run(f"h2h-{args.bots[0]}-{args.bots[1]}", games, args.jobs)
    per_map = defaultdict(lambda: [0, 0, 0])
    per_seed = defaultdict(lambda: [0, 0, 0])
    for s, a, b in pairs:
        for m in maps:
            for ta, tb in ((a, b), (b, a)):
                st, rnd, ga, gb = res[(ta, tb, m)]
                mine, theirs = (ga, gb) if ta == a else (gb, ga)
                win = ("TEAM A WIN" in st and ta == a) or ("TEAM B WIN" in st and tb == a)
                for acc in (per_map[m], per_seed[s]):
                    acc[0] += win
                    acc[1] += 1
                    acc[2] += mine - theirs
    wins = sum(v[0] for v in per_seed.values())
    games_n = sum(v[1] for v in per_seed.values())
    margin = sum(v[2] for v in per_seed.values())
    for m in maps:
        w, n, g = per_map[m]
        print(f"{m:12} {w:>2}/{n:<2} {g:+7d}")
    print("per seed: " + "  ".join(f"s{s} {v[0]}/{v[1]} ({v[2]:+d})" for s, v in per_seed.items()))
    print(f"{args.bots[0]} vs {args.bots[1]}: {wins}/{games_n}, gems {margin:+d}")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=("econ", "h2h"))
    ap.add_argument("bots", nargs="+")
    ap.add_argument("--seeds", default="1,2")
    ap.add_argument("--maps", default="")
    ap.add_argument("--jobs", type=int, default=8)
    args = ap.parse_args()
    if args.mode == "h2h" and len(args.bots) != 2:
        raise SystemExit("h2h takes exactly two bots")
    (econ if args.mode == "econ" else h2h)(args)


if __name__ == "__main__":
    main()
