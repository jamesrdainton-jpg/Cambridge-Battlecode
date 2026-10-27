"""Platform test panel: the same opponents, maps and sides for every version we test, so results can be compared.

Usage (from the project folder, logged in with `cambc login`):
  python tools/panel.py queue LABEL [--pin BASE] [--expect-live N]   # 6 unranked groups with the live version
  python tools/panel.py fetch LABEL                                  # results + replays into replays/platform/
  python tools/panel.py table                                        # wins per label and opponent

`--pin BASE` replays each opponent's bot version from the BASE label's groups (`--source-group`), so later versions
meet exactly the same opponents as the baseline. Rows go to matches/panel.csv (in git). Match groups play whatever
version is live: check `cambc submissions list` ("Live: N") first, or pass --expect-live N.
"""
from __future__ import annotations

import argparse
import csv
import json
import random
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CSV = ROOT / "matches" / "panel.csv"
CAMBC = str(ROOT / ".venv" / ("Scripts/cambc.exe" if sys.platform == "win32" else "bin/cambc"))
FIELDS = ["label", "live", "rank", "opponent", "team_id", "group", "source_group", "queued", "maps", "sides", "wins", "games", "results"]

# Ladder of 2026-10-27 (we were #239, 1,654): one team per band, chosen for many matches played (active, stable bots).
PANEL = [
    (42, "smurphy", "83798ea3-f051-43ed-933d-e0bced90992b"),
    (97, "Crimson Pathfinders", "271f8b15-7d97-4a0a-bd32-b634dd006dc0"),
    (144, "vc?", "910ccbab-531b-4efa-a223-0335a686ad83"),
    (177, "kata", "788c49a0-256d-4094-a57d-2487d0a16f32"),
    (217, "another name", "b095a9ef-91f3-4c4a-b4aa-3ec386286b82"),
    (253, "#grrrrmonday", "8a509652-43f5-4ee8-92bc-16fa59563d2e"),
]
PLATFORM_MAPS = sorted(
    "00ambush 00anvil 00breadcrumbs 00collision 00contest 00corners 00crater 00dunes 00eight 00elkring 00expanse "
    "00fragment 00galaxy 00gem_fields 00gemfight 00great_wall 00interlock 00lanes 00lost_world 00monolith 00oasis "
    "00packs 00pilgrimage 00quadrants 00quarry 00reverse_spiral 00ribs 00road_of_riches 00rows 00rushbait_v2 00split "
    "00stampede 00swirl 00the_line 00vault 01big_world 01boss_battle 01broken_curve 01concentrated_wealth 01corridors "
    "01elk_arena 01fracture 01gold_rush 01hooks 01islands 01shortcut 01starfish 01starvation 01the_farm "
    "01yellow_brick_road 02arena 02crossing 02cuts 02famine 02fields 02geodes 02gift_wrapping 02guardians 02harvest "
    "02stalactites 02tangle 02the_pack 02the_pond 02treasure_box 02uncharted_lands adgato_gemcombat1 adgato_gemcombat2 "
    "adgato_gemcombat3 adgato_gemcombat4 adgato_gemcombat5".split())


def assignment():
    maps = random.Random(2710).sample(PLATFORM_MAPS, 5 * len(PANEL))
    out = []
    for i, opp in enumerate(PANEL):
        ms = maps[5 * i:5 * i + 5]
        sides = ["a" if (i + j) % 2 == 0 else "b" for j in range(5)]
        out.append((opp, ms, sides))
    return out


def cambc(*args) -> str:
    for attempt in range(6):
        p = subprocess.run([CAMBC, *args], capture_output=True, text=True, encoding="utf-8", errors="replace")
        if p.returncode == 0:
            return p.stdout
        if "429" in p.stdout + p.stderr:
            time.sleep(5 * (attempt + 1))
            continue
        raise SystemExit(f"cambc {' '.join(args)} failed: {p.stdout} {p.stderr}")
    raise SystemExit(f"cambc {' '.join(args)}: rate limited")


def live_version() -> str:
    for line in cambc("submissions", "list").splitlines():
        if line.startswith("Live:"):
            return line.split()[1]
    return "?"


def rows() -> list[dict]:
    if not CSV.exists():
        return []
    with CSV.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def save(all_rows: list[dict]) -> None:
    with CSV.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        w.writerows(all_rows)


def queue(args) -> None:
    live = live_version()
    if args.expect_live and live != args.expect_live:
        raise SystemExit(f"live version is {live}, expected {args.expect_live}")
    old = rows()
    if any(r["label"] == args.label for r in old):
        raise SystemExit(f"label {args.label} exists")
    pins = {r["team_id"]: r["group"] for r in old if r["label"] == args.pin} if args.pin else {}
    if args.pin and not pins:
        raise SystemExit(f"no rows for --pin {args.pin}")
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    for (rank, name, tid), maps, sides in assignment():
        cmd = ["match-groups", "create", tid, "--maps", ",".join(maps), "--sides", ",".join(sides), "--json"]
        if tid in pins:
            cmd += ["--source-group", pins[tid]]
        out = json.loads(cambc(*cmd))
        gid = out.get("groupId") or out.get("id") or out.get("group", {}).get("id")
        if not gid:
            raise SystemExit(f"no group id in {out}")
        print(f"{name:22s} #{rank:<4d} group {gid}")
        old.append({"label": args.label, "live": live, "rank": rank, "opponent": name, "team_id": tid, "group": gid,
                    "source_group": pins.get(tid, ""), "queued": now, "maps": " ".join(maps), "sides": "".join(sides),
                    "wins": "", "games": "", "results": ""})
        save(old)


def fetch(args) -> None:
    all_rows = rows()
    dest = ROOT / "replays" / "platform"
    dest.mkdir(parents=True, exist_ok=True)
    for r in all_rows:
        if r["label"] != args.label or r["games"]:
            continue
        d = json.loads(cambc("match-groups", "show", r["group"], "--json"))
        ms = d.get("matches", [])
        if len(ms) < 5 or any(m.get("status") != "finished" for m in ms):
            print(f"{r['opponent']:22s} not finished ({sum(m.get('status') == 'finished' for m in ms)}/5)")
            continue
        res = []
        for m in sorted(ms, key=lambda m: m.get("position", 0)):
            us = next(t for t in m["teams"] if t["teamId"] == "cd168e4d-952a-47db-aa97-a9cae638dea1")
            res.append(f"{m['map']}:{'W' if us['result'] == 'win' else 'L'}:{m.get('endReason', '')}")
        r["wins"] = str(sum(x.split(":")[1] == "W" for x in res))
        r["games"] = str(len(res))
        r["results"] = " ".join(res)
        zp = dest / f"match-group-{r['group']}.zip"
        if not zp.exists():
            cambc("match-groups", "download", r["group"], "-o", str(zp))
        print(f"{r['opponent']:22s} #{r['rank']:<4s} {r['wins']}/{r['games']}  {r['results']}")
        save(all_rows)


def table(_args) -> None:
    all_rows = rows()
    labels = list(dict.fromkeys(r["label"] for r in all_rows))
    print(f"{'opponent':26s}" + "".join(f"{lb:>12s}" for lb in labels))
    for rank, name, tid in PANEL:
        cells = []
        for lb in labels:
            r = next((x for x in all_rows if x["label"] == lb and x["team_id"] == tid), None)
            cells.append(f"{r['wins']}/{r['games']}" if r and r["games"] else "-")
        print(f"#{rank:<4d}{name:21s}" + "".join(f"{c:>12s}" for c in cells))
    tot = []
    for lb in labels:
        rs = [x for x in all_rows if x["label"] == lb and x["games"]]
        tot.append(f"{sum(int(x['wins']) for x in rs)}/{sum(int(x['games']) for x in rs)}")
    print(f"{'total':26s}" + "".join(f"{c:>12s}" for c in tot))
    print(f"{'live version':26s}" + "".join(f"{next(x['live'] for x in all_rows if x['label'] == lb):>12s}" for lb in labels))


def main() -> None:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    q = sub.add_parser("queue")
    q.add_argument("label")
    q.add_argument("--pin")
    q.add_argument("--expect-live")
    q.set_defaults(fn=queue)
    f = sub.add_parser("fetch")
    f.add_argument("label")
    f.set_defaults(fn=fetch)
    t = sub.add_parser("table")
    t.set_defaults(fn=table)
    args = ap.parse_args()
    args.fn(args)


if __name__ == "__main__":
    main()
