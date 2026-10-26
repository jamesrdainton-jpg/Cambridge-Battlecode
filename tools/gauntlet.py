"""Evaluate a bot against several baselines plus the economy benchmark, and log a summary line.

Usage: python tools/gauntlet.py BOT [--vs v3,v2,starter] [--note "what changed"]

Runs BOT vs each opponent on every map from both sides (run-batch), then BOT vs idle (one side).
Prints per-opponent wins and gem margins and appends one CSV line to matches/gauntlet.csv, ending with
the git commit the bots came from ("+dirty" if bots/ or maps/ had uncommitted changes).
"""
from __future__ import annotations

import argparse
import datetime
import re
import subprocess
import sys
from pathlib import Path

from common import git_commit

ROOT = Path(__file__).resolve().parent.parent
PY = sys.executable


MAPS = ""


def seed_file(bot: str) -> str:
    """The source file holding a bot's SEED constant: bot.py for Python bots, params.h for C++ bots (bots/cpp*)."""
    return "params.h" if (ROOT / "bots" / bot / "src" / "main.cpp").exists() else "bot.py"


def run_arena(bot: str, opp: str, one_side: bool = False) -> tuple[int, int, int, int]:
    cmd = [PY, str(ROOT / "tools" / "arena.py"), bot, opp]
    if one_side:
        cmd.append("--one-side")
    if MAPS:
        cmd += ["--maps", MAPS]
    out = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True).stdout
    wins = games = mine = theirs = rounds = 0
    for line in out.splitlines():
        m = re.match(rf"{re.escape(bot)}\s+wins\s+(\d+)/(\d+)\s+gems\(sum of STAT\)\s+(\d+)", line)
        if m:
            wins, games, mine = int(m.group(1)), int(m.group(2)), int(m.group(3))
        m = re.match(rf"{re.escape(opp)}\s+wins\s+\d+/\d+\s+gems\(sum of STAT\)\s+(\d+)", line)
        if m:
            theirs = int(m.group(1))
        m = re.search(r"round=\s*(\d+)", line)
        if m:
            rounds += int(m.group(1))
    return wins, games, mine - theirs, rounds


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("bot")
    parser.add_argument("--vs", default="v3,v2,starter")
    parser.add_argument("--note", default="")
    parser.add_argument("--no-econ", action="store_true")
    parser.add_argument("--seeds", default="", help="comma list of SEED values; plays a seeded copy per seed")
    parser.add_argument("--maps", default="", help="comma list of maps (default: all)")
    args = parser.parse_args()
    global MAPS
    MAPS = args.maps
    bots = [args.bot]
    if args.seeds:
        bots = []
        for seed in args.seeds.split(","):
            name = f"{args.bot}_s{seed}"
            subprocess.run([PY, str(ROOT / "tools" / "variant.py"), name, "--src", args.bot,
                            "--set", f"{seed_file(args.bot)}:SEED = 0=>SEED = {seed}"], cwd=ROOT, check=True)
            bots.append(name)
    seeds = args.seeds.split(",") if args.seeds else []
    parts = []
    total_w = total_g = 0
    for opp in args.vs.split(","):
        # Seed the opponent too when it supports SEED, so both sides are perturbed alike.
        opps = [opp] * len(bots)
        opp_src = ROOT / "bots" / opp / "src" / seed_file(opp)
        if seeds and opp_src.exists() and "SEED = 0" in opp_src.read_text():
            opps = []
            for seed in seeds:
                name = f"{opp}_s{seed}"
                subprocess.run([PY, str(ROOT / "tools" / "variant.py"), name, "--src", opp,
                                "--set", f"{seed_file(opp)}:SEED = 0=>SEED = {seed}"], cwd=ROOT, check=True,
                               stdout=subprocess.DEVNULL)
                opps.append(name)
        w_sum = g_sum = m_sum = 0
        for bot, opp_bot in zip(bots, opps):
            w, g, margin, _ = run_arena(bot, opp_bot)
            if len(bots) > 1:
                print(f"    {bot} vs {opp_bot}: {w}/{g} ({margin:+d})", flush=True)
            w_sum += w
            g_sum += g
            m_sum += margin
        total_w += w_sum
        total_g += g_sum
        parts.append(f"{opp}:{w_sum}/{g_sum}({m_sum:+d})")
        print(f"vs {opp:10} wins {w_sum}/{g_sum}  gem margin {m_sum:+d}", flush=True)
    econ = ""
    if not args.no_econ:
        rounds = 0
        for bot in bots:
            rounds += run_arena(bot, "idle", one_side=True)[3]
        rounds //= len(bots)
        econ = str(rounds)
        print(f"economy (rounds to 1000 vs idle, summed over {len(list((ROOT / "maps").glob("*.map26a")))} maps): {rounds}")
    stamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    maps_note = f" maps={args.maps}" if args.maps else ""
    line = (f"{stamp},{args.bot}{'[' + args.seeds + ']' if args.seeds else ''},{total_w}/{total_g},"
            f"{' '.join(parts)},{econ},{args.note}{maps_note},{git_commit('bots', 'maps')}\n")
    log = ROOT / "matches" / "gauntlet.csv"
    if not log.exists():
        log.write_text("time,bot,wins,per_opponent,economy_rounds,note,commit\n")
    with log.open("a") as f:
        f.write(line)
    print(line.strip())


if __name__ == "__main__":
    main()
