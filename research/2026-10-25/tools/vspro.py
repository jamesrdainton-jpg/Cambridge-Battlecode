"""Why we lose to strong teams: per-game and aggregate analysis of platform match groups that contain our stdout.

Usage: python -I research/2026-10-25/tools/vspro.py ZIP [ZIP ...] [--json OUT]
Uses replay30.py (turn-accurate, priority-aware) and the map dumps in research/2026-10-25/data/mapdumps.
Reports per game: score timeline (our STAT lines), deaths with killer and place, engagements (initiative, numbers,
outcome), spending, camp hits, tributes, items, time in the enemy half, camps taken on the enemy side, grouping.
"""
from __future__ import annotations

import io
import json
import re
import sys
import zipfile
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
import replay30 as R  # noqa: E402

MAPS = {p.stem: p.read_bytes() for p in (ROOT / "maps").glob("*.map26a")}
GEO = {}
for f in (ROOT / "research" / "2026-10-25" / "data" / "mapdumps").glob("*.txt"):
    t = f.read_text(errors="replace")
    m = re.search(r"spawn=(\d+),(\d+) espawn=(\d+),(\d+)", t)
    camps = {}
    for line in t.splitlines():
        if line.startswith("CAMPH"):
            _, h, k, x, y, gi = line.split()
            camps[int(h)] = (k, int(x), int(y), int(gi))
    GEO[f.stem] = {"a": (int(m.group(1)), int(m.group(2))), "b": (int(m.group(3)), int(m.group(4))), "camps": camps}

FAM = ["Monster", "Power", "Durability", "Treasure", "Jungle", "Home", "Bruiser"]
STATS = ["S", "F", "H"]


def item_name(i):
    fam, rest = divmod(i, 6)
    stat, emblem = divmod(rest, 2)
    return f"{FAM[fam] if fam < len(FAM) else fam} {STATS[stat]}"


def cheb(a, b):
    return max(abs(a[0] - b[0]), abs(a[1] - b[1]))


def games(paths):
    for zp in paths:
        z = zipfile.ZipFile(zp)
        for n in sorted(z.namelist()):
            if not n.endswith(".zip"):
                continue
            inner = zipfile.ZipFile(io.BytesIO(z.read(n)))
            names = inner.namelist()
            side = "a" if "team-a.stdout" in names else "b" if "team-b.stdout" in names else None
            stats = []
            if side:
                out = inner.read(f"team-{side}.stdout").decode(errors="replace").replace("\x00", "")
                stats = [tuple(map(int, line.split()[1:4])) for line in out.splitlines() if line.startswith("STAT ")]
            yield f"{Path(zp).name[12:20]}/{n[:2]}", side, stats, inner.read("replay.repl26a")


def analyse(label, side, stats, data):
    g = R.parse(data, MAPS)
    if g is None:
        return None
    geo = GEO.get(g["map"])
    rounds = g["rounds"]
    teams = ("a", "b")
    me, opp = (side, "b" if side == "a" else "a") if side else ("a", "b")
    champs = g["champs"]
    handle = g["handle"]
    owner = {h: (t, i) for (t, i), h in handle.items()}
    # Per champion: positions by round, activity rounds, actions.
    pos = {t: [] for t in teams}
    for t in teams:
        for tl in g["turns"][t]:
            p = {}
            cur = geo[t] if geo else None
            for r, acts in tl:
                for sub, args in acts:
                    if sub == 1:
                        cur = (args[0], args[1])
                p[r] = cur
            pos[t].append(p)

    def where(t, i, r):
        p = pos[t][i]
        while r > 0 and r not in p:
            r -= 1
        return p.get(r)

    # Hits on champions: (round, attacker team, attacker index, target team, target index, kind)
    hits = []
    camp_hits = Counter()
    enemy_side_camp_hits = Counter()
    tributes = defaultdict(list)
    spend = {t: Counter() for t in teams}
    items = {t: Counter() for t in teams}
    first_buy = {}
    for t in teams:
        for i, tl in enumerate(g["turns"][t]):
            for r, acts in tl:
                for sub, args in acts:
                    tgt = None
                    if sub == 2 and args[0] == 1:
                        tgt = args[1]
                    elif sub == 3 and args[1] == 1:
                        tgt = args[2]
                    if tgt is not None and tgt in owner and owner[tgt][0] != t:
                        hits.append((r, t, i, owner[tgt][0], owner[tgt][1], "atk" if sub == 2 else f"cast{args[0]}"))
                    if (sub == 2 and args[0] == 2) or (sub == 3 and args[1] == 2):
                        camp_hits[t] += 1
                        c = geo["camps"].get(args[1] if sub == 2 else args[2]) if geo else None
                        if c and cheb((c[1], c[2]), geo[t]) > cheb((c[1], c[2]), geo["b" if t == "a" else "a"]):
                            enemy_side_camp_hits[t] += 1
                    if sub == 5:
                        tributes[t].append(r)
                    if sub == 6:
                        for lim in (100, 200, 300, 500, 800, 99999):
                            if r <= lim:
                                spend[t][lim] += 30 * args[1]
                        items[t][item_name(args[0])] += args[1]
                        first_buy.setdefault(t, r)
                    if sub == 8:
                        for lim in (100, 200, 300, 500, 800, 99999):
                            if r <= lim:
                                spend[t][lim] += 10 * args[1]
    hits.sort()
    # Deaths (strict): a gap of 55+ rounds without move/attack/cast/recall/tribute.
    deaths = []
    for t in teams:
        seen = set()
        for i, tl in enumerate(g["turns"][t]):
            last = None
            for r, acts in tl:
                if any(s in (1, 2, 3, 4, 5) for s, _ in acts):
                    if last is not None and r - last >= 55:
                        key = (last // 5, "CI") if champs[t][i] in ("Cassi", "Issac") else (last, i)
                        if key not in seen:
                            seen.add(key)
                            deaths.append((last, t, i))
                    last = r
    deaths.sort()
    death_rows = []
    for r, t, i in deaths:
        killers = Counter((ht, hi) for hr, ht, hi, tt, ti, k in hits if tt == t and ti == i and r - 4 <= hr <= r + 1)
        p = where(t, i, r)
        half = None
        if p and geo:
            half = "own half" if cheb(p, geo[t]) <= cheb(p, geo["b" if t == "a" else "a"]) else "enemy half"
        near_camp = None
        if p and geo and geo["camps"]:
            near_camp = min(cheb(p, (c[1], c[2])) for c in geo["camps"].values())
        death_rows.append({"round": r, "team": t, "champ": champs[t][i], "killers": {champs[k[0]][k[1]]: v for k, v in killers.items()},
                           "by_champions": bool(killers), "half": half, "near_camp": near_camp, "pos": p,
                           "attackers": len(killers)})
    # Engagements: champion-vs-champion hits grouped by 8-round gaps.
    engagements = []
    cur = None
    for h in hits:
        if cur is None or h[0] - cur["end"] > 8:
            if cur:
                engagements.append(cur)
            cur = {"start": h[0], "end": h[0], "first": h[1], "who": {t: set() for t in teams}, "hits": Counter()}
        cur["end"] = h[0]
        cur["who"][h[1]].add(h[2])
        cur["hits"][h[1]] += 1
    if cur:
        engagements.append(cur)
    for e in engagements:
        e["deaths"] = Counter(d["team"] for d in death_rows if e["start"] - 2 <= d["round"] <= e["end"] + 5)
        e["n"] = {t: len(e["who"][t]) for t in teams}
    # Territory and grouping (sampled every 5 rounds for living champions).
    in_enemy_half = Counter()
    samples = Counter()
    near_allies = Counter()
    for t in teams:
        if not geo:
            break
        o = "b" if t == "a" else "a"
        for r in range(20, rounds, 5):
            ps = [where(t, i, r) for i in range(len(champs[t]))]
            for i, p in enumerate(ps):
                if p is None:
                    continue
                samples[t] += 1
                if cheb(p, geo[o]) < cheb(p, geo[t]):
                    in_enemy_half[t] += 1
                near_allies[t] += sum(1 for j, q in enumerate(ps) if j != i and q and cheb(p, q) <= 4)
    final = stats[-1] if stats else None
    timeline = {}
    for r in (100, 200, 300, 400, 500, 600, 800, 1000):
        s = next((x for x in stats if x[0] >= r), None)
        if s:
            timeline[r] = (s[1], s[2])
    return {"label": label, "map": g["map"], "rounds": rounds, "side": side, "final": final, "timeline": timeline,
            "champs": champs, "deaths": death_rows, "engagements": engagements, "camp_hits": camp_hits,
            "enemy_side_camp_hits": enemy_side_camp_hits, "tributes": {t: len(v) for t, v in tributes.items()},
            "first_tribute": {t: (v[0] if v else None) for t, v in tributes.items()}, "spend": spend, "items": items,
            "first_buy": first_buy, "in_enemy_half": in_enemy_half, "samples": samples, "near_allies": near_allies,
            "me": me, "opp": opp, "hits": hits}


def main():
    args = sys.argv[1:]
    out_json = None
    if "--json" in args:
        i = args.index("--json")
        out_json = args[i + 1]
        del args[i:i + 2]
    res = [a for a in (analyse(*x) for x in games(args)) if a]
    agg = defaultdict(Counter)
    for a in res:
        me, opp = a["me"], a["opp"]
        f = a["final"]
        dm = [d for d in a["deaths"] if d["team"] == me]
        do = [d for d in a["deaths"] if d["team"] == opp]
        print(f"\n== {a['label']} {a['map']} r{a['rounds']} final {f[1] if f else '?'}-{f[2] if f else '?'}  "
              f"us {','.join(a['champs'][me])} vs {','.join(a['champs'][opp])}")
        print("   gems us-them: " + "  ".join(f"r{r} {u}-{t}" for r, (u, t) in a["timeline"].items()))
        print(f"   deaths us {len(dm)} them {len(do)}; our deaths by champions {sum(d['by_champions'] for d in dm)}, "
              f"in enemy half {sum(d['half'] == 'enemy half' for d in dm)}; first 300 rounds us {sum(d['round'] <= 300 for d in dm)} them {sum(d['round'] <= 300 for d in do)}")
        kill_by = Counter()
        for d in dm:
            for k in d["killers"]:
                kill_by[k] += 1
        print(f"   who hits our dying champions: {dict(kill_by.most_common())}")
        eng = a["engagements"]
        init = Counter(e["first"] for e in eng)
        won = Counter()
        for e in eng:
            if e["deaths"][me] != e["deaths"][opp]:
                won[me if e["deaths"][me] < e["deaths"][opp] else opp] += 1
        print(f"   engagements {len(eng)}: started by us {init[me]} them {init[opp]}; won (fewer deaths) us {won[me]} them {won[opp]}; "
              f"mean champions per engagement us {sum(e['n'][me] for e in eng) / max(1, len(eng)):.1f} them {sum(e['n'][opp] for e in eng) / max(1, len(eng)):.1f}")
        print(f"   gold spent r100/200/300/500: us {[a['spend'][me][k] for k in (100, 200, 300, 500)]} them {[a['spend'][opp][k] for k in (100, 200, 300, 500)]}")
        print(f"   camp hits us {a['camp_hits'][me]} them {a['camp_hits'][opp]}; on the enemy side us {a['enemy_side_camp_hits'][me]} them {a['enemy_side_camp_hits'][opp]}; "
              f"tributes us {a['tributes'].get(me, 0)} them {a['tributes'].get(opp, 0)}")
        print(f"   time in enemy half us {100 * a['in_enemy_half'][me] / max(1, a['samples'][me]):.0f}% them {100 * a['in_enemy_half'][opp] / max(1, a['samples'][opp]):.0f}%; "
              f"allies within 4 us {a['near_allies'][me] / max(1, a['samples'][me]):.2f} them {a['near_allies'][opp] / max(1, a['samples'][opp]):.2f}")
        g = agg
        g["games"]["n"] += 1
        g["deaths"]["us"] += len(dm)
        g["deaths"]["them"] += len(do)
        g["deaths"]["us_by_champ"] += sum(d["by_champions"] for d in dm)
        g["deaths"]["us_enemy_half"] += sum(d["half"] == "enemy half" for d in dm)
        g["deaths"]["us_first300"] += sum(d["round"] <= 300 for d in dm)
        g["deaths"]["them_first300"] += sum(d["round"] <= 300 for d in do)
        g["rounds"]["sum"] += a["rounds"]
        for k, v in kill_by.items():
            g["killers"][k] += v
        g["eng"]["n"] += len(eng)
        g["eng"]["started_us"] += init[me]
        g["eng"]["started_them"] += init[opp]
        g["eng"]["won_us"] += won[me]
        g["eng"]["won_them"] += won[opp]
        g["eng"]["n_us"] += sum(e["n"][me] for e in eng)
        g["eng"]["n_them"] += sum(e["n"][opp] for e in eng)
        for k in (100, 200, 300, 500):
            g["spend_us"][k] += a["spend"][me][k]
            g["spend_them"][k] += a["spend"][opp][k]
        g["camps"]["us"] += a["camp_hits"][me]
        g["camps"]["them"] += a["camp_hits"][opp]
        g["camps"]["us_enemy_side"] += a["enemy_side_camp_hits"][me]
        g["camps"]["them_enemy_side"] += a["enemy_side_camp_hits"][opp]
        g["terr"]["us_enemy"] += a["in_enemy_half"][me]
        g["terr"]["them_enemy"] += a["in_enemy_half"][opp]
        g["terr"]["us_n"] += a["samples"][me]
        g["terr"]["them_n"] += a["samples"][opp]
        g["terr"]["us_allies"] += a["near_allies"][me]
        g["terr"]["them_allies"] += a["near_allies"][opp]
        for k, v in a["items"][me].items():
            g["items_us"][k] += v
        for k, v in a["items"][opp].items():
            g["items_them"][k] += v
        for r, (u, t) in a["timeline"].items():
            g["tl_us"][r] += u
            g["tl_them"][r] += t
            g["tl_n"][r] += 1
    g = agg
    n = g["games"]["n"]
    rr = g["rounds"]["sum"] / 100
    print(f"\n#### AGGREGATE over {n} games ({g['rounds']['sum']} rounds)")
    print(f"deaths per team per 100 rounds: us {g['deaths']['us'] / rr:.2f}  them {g['deaths']['them'] / rr:.2f}  "
          f"(ours by champions {g['deaths']['us_by_champ']}/{g['deaths']['us']}, in their half {g['deaths']['us_enemy_half']}, "
          f"in the first 300 rounds us {g['deaths']['us_first300']} them {g['deaths']['them_first300']})")
    print(f"enemy champions hitting our dying champions: {dict(g['killers'].most_common())}")
    e = g["eng"]
    print(f"engagements {e['n']}: started by us {e['started_us']} them {e['started_them']}; won us {e['won_us']} them {e['won_them']}; "
          f"champions per engagement us {e['n_us'] / max(1, e['n']):.2f} them {e['n_them'] / max(1, e['n']):.2f}")
    print("mean gold spent by r100/200/300/500: us " + str([round(g['spend_us'][k] / n) for k in (100, 200, 300, 500)])
          + " them " + str([round(g['spend_them'][k] / n) for k in (100, 200, 300, 500)]))
    print(f"camp hits per game us {g['camps']['us'] / n:.0f} them {g['camps']['them'] / n:.0f}; share on the enemy side us "
          f"{100 * g['camps']['us_enemy_side'] / max(1, g['camps']['us']):.0f}% them {100 * g['camps']['them_enemy_side'] / max(1, g['camps']['them']):.0f}%")
    t = g["terr"]
    print(f"time in enemy half us {100 * t['us_enemy'] / max(1, t['us_n']):.0f}% them {100 * t['them_enemy'] / max(1, t['them_n']):.0f}%; "
          f"allies within 4 tiles us {t['us_allies'] / max(1, t['us_n']):.2f} them {t['them_allies'] / max(1, t['them_n']):.2f}")
    print("mean gems (us-them) at round: " + "  ".join(f"r{r} {g['tl_us'][r] / g['tl_n'][r]:.0f}-{g['tl_them'][r] / g['tl_n'][r]:.0f} (n={g['tl_n'][r]})" for r in sorted(g['tl_n'])))
    print("items bought (shards) us:", dict(g["items_us"].most_common(8)))
    print("items bought (shards) them:", dict(g["items_them"].most_common(8)))
    if out_json:
        slim = [{k: v for k, v in a.items() if k not in ("hits", "engagements")} for a in res]
        Path(out_json).write_text(json.dumps(slim, default=lambda o: sorted(o) if isinstance(o, set) else str(o), indent=1))


if __name__ == "__main__":
    main()
