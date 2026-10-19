"""Estimated camp damage per team from replays: basic hits use strength (base + strength shards x growth,
Power emblem = 6 shards, Monster +10% vs camps), casts use focus x the ability's modifier.
Splash/AoE extra targets are not counted (lower bound for Varg/Stellar/Ryth/Prism).
Usage: python -I damage.py [--team a] [--label X,Y] [--rounds 300] DIR..."""
import os as _os
from pathlib import Path as _Path
_HERE = _Path(__file__).resolve().parent
_ROOT = _HERE.parents[2]
_WORK = _Path(_os.environ.get("RS_WORK", str(_ROOT / "matches" / "research")))
import sys
from collections import Counter, defaultdict
from pathlib import Path
sys.path.insert(0, str(_ROOT / "tools"))
sys.path.insert(0, str(_HERE))
import replay_decode as RD
from replay_profile import per_turn, files
from targets import CAMPS

ROOT = _ROOT
# name: (str, str growth, focus, focus growth, slot0 modifier, slot1 modifier, health growth)
STATS = {
    "Ryth": (50, 5, 100, 10, 1.0, 0, 100), "Vesper": (45, 5, 100, 10, 0, 0, 100), "Vendetta": (70, 5, 100, 10, 0, 0, 100),
    "Cassi": (30, 3.5, 70, 15, 2.0, 0, 71.25), "Issac": (40, 4.75, 100, 10, 0, 0, 95), "Stellar": (35, 3.5, 100, 10, 2.0, 1.4, 75),
    "Prism": (35, 3.5, 80, 10, 1.5, 1.0, 75), "Marcella": (45, 5, 50, 10, 0, 2.0, 100), "Willow": (45, 3, 105, 5, 0, 0, 50),
    "Ren": (40, 5, 100, 10, 1.25, 0, 100), "Varg": (50, 5, 100, 10, 0, 0, 100), "Tavi": (35, 5, 100, 10, 0, 2.2, 75),
}
FAM = ["Monster", "Power", "Durability", "Treasure", "Jungle", "Home", "Bruiser"]


def main():
    args = sys.argv[1:]
    team_only = label = None
    R = 300
    for flag in ("--team", "--label", "--rounds"):
        if flag in args:
            i = args.index(flag)
            v = args[i + 1]
            del args[i:i + 2]
            if flag == "--team":
                team_only = v
            elif flag == "--label":
                label = v.split(",")
            else:
                R = int(v)
    maps = {p.stem: p.read_bytes() for p in (ROOT / "maps").glob("*.map26a")}
    agg = Counter()
    n = 0
    for f in files(args):
        for lab, data in RD.replays(f):
            g = per_turn(data, maps)
            if g is None:
                continue
            for team in "ab":
                if team_only and team != team_only:
                    continue
                if label and not all(x in g["champs"][team] for x in label):
                    continue
                n += 1
                for champ, tl in zip(g["champs"][team], g["turns"][team]):
                    s0, sg, f0, fg, m0, m1, hg = STATS[champ]
                    shards = Counter()  # (family, stat) -> count
                    for r, acts in tl:
                        if r > R:
                            break
                        for sub, a in acts:
                            if sub == 6 and a[0] < 42:
                                fam, rest = divmod(a[0], 6)
                                stat, kind = divmod(rest, 2)
                                shards[(fam, stat)] += a[1]
                        # current stats
                        sh = Counter()
                        monster = False
                        for (fam, stat), k in shards.items():
                            emblems = k // 5
                            sh[stat] += k + (emblems if fam == 1 else 0)
                            if fam == 6:
                                for o in (0, 1, 2):
                                    if o != stat:
                                        sh[o] += emblems
                            if fam == 0 and emblems:
                                monster = True
                        strength = s0 + sg * sh[0] + (0.01 * hg * sh[2] if champ == "Ryth" else 0)
                        focus = f0 + fg * sh[1]
                        mult = 1.1 if monster else 1.0
                        for sub, a in acts:
                            if sub == 2 and a[0] == 2:
                                agg["basic"] += strength * mult
                                agg["n_basic"] += 1
                            elif sub == 3 and a[1] == 2:
                                mod = m0 if a[0] == 0 else m1
                                agg["cast"] += focus * mod * mult
                                agg["n_cast"] += 1
                            elif sub == 3 and a[1] == 0 and a[3] >= 0:
                                # ground-targeted cast (AoE): count if the champion has an AoE in that slot
                                mod = m0 if a[0] == 0 else m1
                                if champ in ("Stellar", "Prism", "Ryth") and mod:
                                    agg["aoe_ground"] += focus * mod * mult
                    agg["turns"] += sum(1 for r, _ in tl if r <= R)
    if not n:
        print("no teams")
        return
    per100 = lambda k: agg[k] / n / (R / 100)
    print(f"{n} team-games, rounds 1-{R}: camp damage per team per 100 rounds: basic {per100('basic'):.0f} "
          f"({per100('n_basic'):.0f} hits, {agg['basic'] / max(1, agg['n_basic']):.0f}/hit), "
          f"targeted casts {per100('cast'):.0f} ({per100('n_cast'):.0f} casts), ground AoE casts {per100('aoe_ground'):.0f}; "
          f"total {per100('basic') + per100('cast') + per100('aoe_ground'):.0f}")


if __name__ == "__main__":
    main()
