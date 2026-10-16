"""Play bots with `cambc run --statistics` to get kills, deaths and damage per team.

Slower than tools/arena.py (every game rebuilds both bots) but reports combat detail.
Usage: python tools/stats.py BOT_A BOT_B [--maps a,b] [--jobs N]
"""
from __future__ import annotations

import argparse
import json
import subprocess
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from common import find_cambc

ROOT = Path(__file__).resolve().parent.parent
CAMBC = find_cambc()
NAMES = ["Ryth", "Vesper", "Vendetta", "Cassi", "Issac", "Stellar", "Prism", "Marcella", "Willow", "Ren", "Varg", "Tavi"]


def play(a: str, b: str, m: str, out: Path) -> dict:
    out.mkdir(parents=True, exist_ok=True)
    stats = out / "stats.json"
    for _ in range(3):
        if stats.exists():
            stats.unlink()
        subprocess.run([str(CAMBC), "run", a, b, "--map", m, "--out-dir", str(out), "--statistics", str(stats)],
                       cwd=ROOT, capture_output=True, text=True)
        if stats.exists():
            return {"a": a, "b": b, "map": m, "data": json.loads(stats.read_text())}
    return {"a": a, "b": b, "map": m, "error": True}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("bot_a")
    parser.add_argument("bot_b")
    parser.add_argument("--maps", default="")
    parser.add_argument("--jobs", type=int, default=6)
    args = parser.parse_args()
    maps = args.maps.split(",") if args.maps else sorted(p.stem for p in (ROOT / "maps").glob("*.map26a"))
    base = ROOT / "matches" / "stats"
    games = []
    for m in maps:
        games.append((args.bot_a, args.bot_b, m, base / f"{m}-1"))
        games.append((args.bot_b, args.bot_a, m, base / f"{m}-2"))
    with ThreadPoolExecutor(args.jobs) as pool:
        results = list(pool.map(lambda g: play(*g), games))
    for r in results:
        if r.get("error"):
            print(f"{r['map']:10} {r['a']} vs {r['b']}: ERROR")
            continue
        d = r["data"]
        teams = d["teams"]
        line = f"{r['map']:10} {r['a']:>8} v {r['b']:<8} {d['outcome']:6} r{d['round']:>4} gems {teams[0]['submittedGems']:>4}-{teams[1]['submittedGems']:<4}"
        for t in (0, 1):
            champs = [c for c in d["champions"] if c["team"] == t]
            k = sum(c["kills"] for c in champs)
            de = sum(c["deaths"] for c in champs)
            dmg = sum(c["championDamageDone"] for c in champs)
            lost = sum(c["collectedGems"] - c["submittedGems"] - c["gems"] for c in champs)
            line += f" | T{t} K{k} D{de} lost{lost}"
        print(line)
        for t in (0, 1):
            champs = [c for c in d["champions"] if c["team"] == t]
            print("      T%d " % t + "  ".join(
                f"{NAMES[c['type']]}:k{c['kills']}d{c['deaths']}g{c['submittedGems']}" for c in champs))


if __name__ == "__main__":
    main()
