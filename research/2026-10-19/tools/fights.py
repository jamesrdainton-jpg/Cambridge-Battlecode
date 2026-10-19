"""Fight calibration from instrumented runs where both sides print I F / I D lines.

Usage: python fights.py RUN BOT
An engagement = one champion's consecutive fight snapshots (gap <= 2 rounds). Its decision ratio is the
first snapshot's ratio (after home/away modifiers). Outcome window: start .. end + 6 rounds.
  died   = this champion died in the window
  kill   = an enemy champion that was in its near list died in the window (opponent's I D lines)
Also: what preceded each of our deaths (fight or not, ratio, enemies near, allies near, health).
"""
import os as _os
from pathlib import Path as _Path
_HERE = _Path(__file__).resolve().parent
_ROOT = _HERE.parents[2]
_WORK = _Path(_os.environ.get("RS_WORK", str(_ROOT / "matches" / "research")))
import sys
from collections import Counter, defaultdict

sys.path.insert(0, str(_HERE))
from analyze import load, lines_of  # noqa: E402

BUCKETS = [(0, 0.5), (0.5, 0.9), (0.9, 1.3), (1.3, 2.0), (2.0, 4.0), (4.0, 1e9)]


def bucket(r):
    for lo, hi in BUCKETS:
        if lo <= r < hi:
            return f"{lo}-{hi if hi < 1e8 else 'inf'}"
    return "?"


def main():
    run, bot = sys.argv[1], sys.argv[2]
    games = load(run)
    tab = defaultdict(Counter)
    by_enemy = defaultdict(Counter)
    death_ctx = Counter()
    death_rows = []
    n_eng = 0
    for g in games:
        for side, other in (("a", "b"), ("b", "a")):
            if g[side] != bot:
                continue
            fl = lines_of(g["text"][side], "F")
            ours = [(int(p[2]), p[3]) for p in lines_of(g["text"][side], "D")]
            theirs = [(int(p[2]), p[3]) for p in lines_of(g["text"][other], "D")]
            # Per champion engagements.
            eng = defaultdict(list)
            for p in fl:
                r, name = int(p[2]), p[3]
                ratio = float(p[4])
                hp, mh = float(p[5]), float(p[6])
                act = p[11]
                allies = int(p[12].split("=")[1])
                near = []
                for tok in p[13:]:
                    k, d, ehp, emh, eg = tok.split(":")
                    near.append((k, int(d), float(ehp), float(emh), int(eg)))
                lst = eng[name]
                if lst and r - lst[-1][-1]["r"] <= 2:
                    lst[-1].append({"r": r, "ratio": ratio, "hp": hp, "mh": mh, "near": near, "act": act, "allies": allies})
                else:
                    lst.append([{"r": r, "ratio": ratio, "hp": hp, "mh": mh, "near": near, "act": act, "allies": allies}])
            for name, episodes in eng.items():
                for ep in episodes:
                    n_eng += 1
                    s, e = ep[0]["r"], ep[-1]["r"]
                    died = any(n == name and s <= r <= e + 6 for r, n in ours)
                    kinds = {x[0] for snap in ep for x in snap["near"]}
                    kill = any(n in kinds and s <= r <= e + 6 for r, n in theirs)
                    b = bucket(ep[0]["ratio"])
                    t = tab[b]
                    t["n"] += 1
                    t["died"] += died
                    t["kill"] += kill
                    t["long"] += (e - s) >= 5
                    for k in kinds:
                        by_enemy[k]["n"] += 1
                        by_enemy[k]["died"] += died
            # Death context.
            for r, name in ours:
                ctx = None
                for ep in eng.get(name, []):
                    if ep[0]["r"] <= r <= ep[-1]["r"] + 6:
                        ctx = ep
                if ctx is None:
                    death_ctx["no fight snapshot within 6 rounds (camp or unseen attacker)"] += 1
                    continue
                first, last = ctx[0], ctx[-1]
                death_ctx[f"fight: first ratio {bucket(first['ratio'])}"] += 1
                death_rows.append((g["map"], r, name, first["ratio"], last["ratio"], len(ctx), first["hp"] / first["mh"],
                                   last["hp"] / last["mh"], first["allies"], [x[0][:4] + str(x[1]) for x in first["near"]],
                                   [s["act"] for s in ctx][-6:]))
    print(f"{bot}: {n_eng} engagements")
    print(f"{'first ratio':>12} {'n':>6} {'died%':>6} {'kill%':>6} {'5+rounds%':>9}")
    for lo, hi in BUCKETS:
        b = f"{lo}-{hi if hi < 1e8 else 'inf'}"
        t = tab.get(b)
        if not t:
            continue
        print(f"{b:>12} {t['n']:6} {100 * t['died'] / t['n']:6.1f} {100 * t['kill'] / t['n']:6.1f} {100 * t['long'] / t['n']:9.1f}")
    print("\ndeath context:")
    for k, v in death_ctx.most_common():
        print(f"  {v:5} {k}")
    print("\nengagements by enemy champion present (died%):")
    for k, c in sorted(by_enemy.items(), key=lambda kv: -kv[1]["n"]):
        print(f"  {k:10} n={c['n']:5} died={100 * c['died'] / c['n']:5.1f}%")
    print("\nsample deaths (map, round, champ, first/last ratio, snaps, hp% first/last, allies, enemies, last acts):")
    for row in death_rows[:40]:
        print("  ", row[0], row[1], row[2], f"{row[3]:.2f}/{row[4]:.2f}", row[5], f"{row[6]:.2f}/{row[7]:.2f}", row[8], row[9], row[10])


if __name__ == "__main__":
    main()
