"""Per-team activity profile from replays (any source): what each champion-turn was spent on.

Usage: python -I replay_profile.py FILE_OR_DIR [...] [--by-map] [--rounds 0-400]
Categories per champion-turn (first match wins):
  hit_camp   basic attack or cast on a camp           hit_champ  attack or cast on a champion
  cast_none  untargeted/ground cast (AoE, shield, dash...) with no attack
  move       moved only                               buy        bought something, nothing else
  none       no action (channelling recall/tribute, capturing, waiting, dead)
Also: recalls, tributes, wards, deaths per 100 rounds.
"""
import os as _os
from pathlib import Path as _Path
_HERE = _Path(__file__).resolve().parent
_ROOT = _HERE.parents[2]
_WORK = _Path(_os.environ.get("RS_WORK", str(_ROOT / "matches" / "research")))
import argparse
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(_ROOT / "tools"))
import replay_decode as RD  # noqa: E402

ROOT = _ROOT


def turn_lists(data, maps):
    """Like RD.decode but keeps each turn's record list (one entry per champion-turn)."""
    g = RD.decode(data, maps)
    return g


def per_turn(data, maps):
    """Return map, rounds, champs, and per team per champion a list of (round, [actions]) per turn."""
    import struct
    name, mb = next(((n, b) for n, b in maps.items() if b in data), ("?", b""))
    if not mb or RD.version(data) not in RD.SUPPORTED:
        return None
    o = data.find(mb) + len(mb)
    count = struct.unpack_from("<I", data, o)[0]
    o += 4
    picks, turns, cur = [], [], []
    n = 0
    draft_end = False
    while n < count and o < len(data):
        tag = data[o]
        if tag == 4:
            picks.append(struct.unpack_from("<I", data, o + 2)[0])
            o += 7
            draft_end = RD.draft_end_records(data)
        elif tag == 3:
            if not draft_end:
                turns.append(cur)
                cur = []
            draft_end = False
            o += 2
        elif tag == 0 and data[o + 1] in RD.PAYLOAD:
            sub = data[o + 1]
            p = data[o + 2:o + 2 + RD.PAYLOAD[sub]]
            if sub in (1, 5, 10):
                args = struct.unpack("<ii", p)
            elif sub in (6, 8):
                args = struct.unpack("<II", p)
            elif sub == 2:
                args = (p[0], struct.unpack_from("<I", p, 1)[0])
            elif sub == 3:
                args = (p[0], p[4], struct.unpack_from("<I", p, 5)[0]) + struct.unpack_from("<ii", p, 9)
            elif sub == 9:
                args = (p[0],) + struct.unpack_from("<ii", p, 1)
            else:
                args = ()
            cur.append((sub, args))
            o += 2 + RD.PAYLOAD[sub]
        else:
            break
        n += 1
    teams = {"a": picks[0::2], "b": picks[1::2]}
    champs = {t: [c for p in teams[t] for c in (("Cassi", "Issac") if p == 3 else (RD.PICKS[p],))] for t in teams}
    out = {t: [[] for _ in champs[t]] for t in teams}
    t, r = 0, 1
    while t < len(turns):
        first, second = ("a", "b") if r % 2 == 1 else ("b", "a")
        for k in range(max(len(champs["a"]), len(champs["b"]))):
            for team in (first, second):
                if k < len(champs[team]) and t < len(turns):
                    out[team][k].append((r, turns[t]))
                    t += 1
        r += 1
    return {"map": name, "rounds": r - 1, "champs": champs, "turns": out, "draft": teams}


def classify(acts):
    kinds = [s for s, _ in acts]
    hit_camp = any((s == 2 and a[0] == 2) or (s == 3 and a[1] == 2) for s, a in acts)
    hit_champ = any((s == 2 and a[0] == 1) or (s == 3 and a[1] == 1) for s, a in acts)
    if hit_champ:
        return "hit_champ"
    if hit_camp:
        return "hit_camp"
    if 3 in kinds:
        return "cast_none"
    if 1 in kinds:
        return "move"
    if 2 in kinds:
        return "hit_other"  # altar lock etc.
    if 4 in kinds:
        return "recall_start"
    if 5 in kinds:
        return "tribute_start"
    if 6 in kinds or 8 in kinds:
        return "buy"
    return "none"


def files(paths):
    for p in paths:
        p = Path(p)
        if p.is_dir():
            for f in sorted(p.rglob("*")):
                if f.suffix in (".repl26a", ".zip"):
                    yield f
        else:
            yield p


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("paths", nargs="+")
    ap.add_argument("--by-map", action="store_true")
    ap.add_argument("--rounds", default="")
    ap.add_argument("--label", default="", help="only teams whose champions include all of these (comma)")
    ap.add_argument("--team", default="", help="a or b only")
    args = ap.parse_args()
    lo, hi = (0, 10 ** 9)
    if args.rounds:
        lo, hi = map(int, args.rounds.split("-"))
    maps = {p.stem: p.read_bytes() for p in (ROOT / "maps").glob("*.map26a")}
    total = Counter()
    by_map = defaultdict(Counter)
    n_games = 0
    for f in files(args.paths):
        for label, data in RD.replays(f):
            g = per_turn(data, maps)
            if g is None:
                continue
            n_games += 1
            for team in ("a", "b"):
                if args.team and team != args.team:
                    continue
                if args.label and not all(x in g["champs"][team] for x in args.label.split(",")):
                    continue
                for champ, tl in zip(g["champs"][team], g["turns"][team]):
                    for r, acts in tl:
                        if lo <= r <= hi:
                            c = classify(acts)
                            total[c] += 1
                            by_map[g["map"]][c] += 1
    t = sum(total.values())
    print(f"{n_games} games, {t} champion-turns")
    for k, v in total.most_common():
        print(f"  {k:14} {100 * v / t:5.1f}%")
    if args.by_map:
        for m in sorted(by_map):
            c = by_map[m]
            tt = sum(c.values())
            print(f"  {m:12} " + " ".join(f"{k}={100 * c[k] / tt:.0f}" for k in ("hit_camp", "hit_champ", "move", "none", "cast_none")))


if __name__ == "__main__":
    main()
