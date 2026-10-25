"""Summarise survey probe output: per map, total gems, share of gems in groups with a monolith/golem, golem presence.

Usage: python research/2026-10-25/tools/survey_table.py [DIR]
DIR holds one text dump per map (the survey probe's team-a stdout); default: research/2026-10-25/data/mapdumps.
To regenerate the dumps, run survey_probe.py as a bot on every map for one round (see the report's appendix).
"""
import sys, re, collections
from pathlib import Path
out = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parents[1] / "data" / "mapdumps"
rows = []
kind_rewards = collections.defaultdict(set)
for f in sorted(out.glob("*.txt")):
    t = f.read_text(errors="replace")
    head = next(l for l in t.splitlines() if l.startswith("SURVEY"))
    groups = [l for l in t.splitlines() if l.startswith("GROUP")]
    tot = boss = golem_gems = 0
    kinds_all = collections.Counter()
    hasO = hasM = 0
    for g in groups:
        m = re.match(r"GROUP (\S+) gold=(\d+) gems=(\d+) respawn=(\d+)", g)
        k, gold, gems, resp = m.group(1), int(m.group(2)), int(m.group(3)), int(m.group(4))
        tot += gems
        kinds_all.update(k)
        if len(k) == 1:
            kind_rewards[k].add((gold, gems, resp))
        if "M" in k or "O" in k:
            boss += gems
        if "O" in k:
            golem_gems += gems; hasO += 1
        if "M" in k:
            hasM += 1
    picks = re.search(r"picks=(\d+)", head).group(1)
    size = re.search(r"map (\d+x\d+)", head).group(1)
    alt = re.search(r"altars=(\d+)", head).group(1)
    bush = re.search(r"bushes=(\d+)", head).group(1)
    rows.append((f.stem, size, picks, alt, bush, len(groups), tot, boss, hasM, hasO, golem_gems, dict(kinds_all)))
print("| map | size | picks | altars | bushes | groups | gems | boss-group gems (share) | monolith groups | golem groups | camps by kind |")
print("|---|---|---|---|---|---|---|---|---|---|---|")
for r in rows:
    share = f"{r[7]} ({100*r[7]//max(1,r[6])}%)"
    print(f"| {r[0]} | {r[1]} | {r[2]} | {r[3]} | {r[4]} | {r[5]} | {r[6]} | {share} | {r[8]} | {r[9]} | {r[11]} |")
print("\nsingle-camp group rewards by kind (gold, gems, respawn):", {k: sorted(v) for k, v in kind_rewards.items()})
print("maps with golems:", [r[0] for r in rows if r[9]])
