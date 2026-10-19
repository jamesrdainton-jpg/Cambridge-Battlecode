"""Analyse instrumented runs (I T / I F / I D lines).

Usage: python analyze.py RUN [--bot NAME] [--fights] [--acts] [--deaths]
RUN is a folder under matches/research/runs (or $RS_WORK/runs). --bot picks which bot's lines to analyse (default: first in manifest).
"""
import os as _os
from pathlib import Path as _Path
_HERE = _Path(__file__).resolve().parent
_ROOT = _HERE.parents[2]
_WORK = _Path(_os.environ.get("RS_WORK", str(_ROOT / "matches" / "research")))
import argparse
import re
import zipfile
from collections import Counter, defaultdict
from pathlib import Path

SP = _WORK
RESULT = re.compile(r"\[\+\]\s+(.*?)\s{2,}(\S+) vs (\S+)\s+(\S+)\s+Round (\d+)/\d+")


def load(run):
    base = SP / "runs" / run
    man = [l.split() for l in (base / "manifest.txt").read_text().splitlines() if l.strip()]
    res = {}
    for line in (base / "batch.log").read_text().splitlines():
        m = RESULT.search(line)
        if m:
            st, a, b, mp, rnd = m.groups()
            res[(Path(a).name, Path(b).name, mp)] = (st, int(rnd))
    games = []
    for a, b, mp, rp in man:
        a, b, mp = Path(a).name, Path(b).name, Path(mp).stem
        st, rnd = res.get((a, b, mp), ("MISSING", 0))
        texts = {}
        try:
            with zipfile.ZipFile(rp) as z:
                for t in ("a", "b"):
                    texts[t] = z.read(f"team-{t}.stdout").decode(errors="replace").replace("\x00", "")
        except Exception:
            continue
        games.append({"a": a, "b": b, "map": mp, "status": st, "round": rnd, "text": texts, "replay": rp})
    return games


def lines_of(text, kind):
    out = []
    for line in text.splitlines():
        if line.startswith("I " + kind + " "):
            out.append(line.split())
    return out


def stat_curve(text):
    out = []
    for line in text.splitlines():
        if line.startswith("STAT "):
            p = line.split()
            out.append((int(p[1]), int(p[2]), int(p[3])))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("run")
    ap.add_argument("--bot", default="")
    ap.add_argument("--acts", action="store_true")
    ap.add_argument("--fights", action="store_true")
    ap.add_argument("--deaths", action="store_true")
    args = ap.parse_args()
    games = load(args.run)
    bot = args.bot or games[0]["a"]
    grand = Counter()
    grand_sub = Counter()
    per_map = {}
    for g in games:
        for side in ("a", "b"):
            if g[side] != bot:
                continue
            acts = Counter()
            sub = Counter()
            for p in lines_of(g["text"][side], "T"):
                act, s = p[4], p[5]
                acts[act] += 1
                if act in ("camp", "fight", "wait", "farm", "to_altar"):
                    sub[act + ":" + s] += 1
            grand.update(acts)
            grand_sub.update(sub)
            win = (side == "a" and "TEAM A WIN" in g["status"]) or (side == "b" and "TEAM B WIN" in g["status"])
            per_map.setdefault(g["map"], []).append((g["round"], win, acts, side))
    if args.acts:
        tot = sum(grand.values())
        print(f"{bot}: {tot} champion-turns")
        for k, v in grand.most_common():
            print(f"  {k:14} {v:7} {100 * v / tot:5.1f}%")
        print("  sub-labels (h=hit, c=cast, m=moved):")
        for k, v in sorted(grand_sub.items()):
            print(f"    {k:18} {v:7} {100 * v / tot:5.1f}%")
        print("\nper map (round, win, top acts %):")
        for mp in sorted(per_map):
            for rnd, win, acts, side in per_map[mp]:
                t = sum(acts.values())
                top = " ".join(f"{k}={100 * v / t:.0f}" for k, v in acts.most_common(8))
                print(f"  {mp:12} {side} r{rnd:<5} {'W' if win else 'L'}  {top}")
    if args.deaths:
        dc = Counter()
        lost = 0
        n = 0
        for g in games:
            for side in ("a", "b"):
                if g[side] != bot:
                    continue
                for p in lines_of(g["text"][side], "D"):
                    dc[p[3]] += 1
                    lost += int(p[4])
                    n += 1
        print(f"deaths {n} in {len(games)} games, gems lost {lost}; by champion {dict(dc)}")


if __name__ == "__main__":
    main()
