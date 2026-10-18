#!/usr/bin/env bash
# Queue 9 (2026-10-18, cambc 2.2.5, 17 maps): fight caution and 3-pick drafts, each one change of mybot vs v7.
# From the v7 platform games: 80% of our deaths follow enemy attacks, 72% with an ally within 6 tiles, 49% with a
# single attacker; 3-pick maps 2/7 (opponents field 4 champions via Cassi & Issac).
#   ar4: only allies within 4 tiles count in the fight ratio (was 7)
#   lh1: retreat below 40% health if an enemy can hit us within 4 moves (was 25% / 2); lh2: 35% / 3
#   d3a / d3b: 3-pick drafts with Cassi & Issac, on the four 3-pick maps with seeds 1-8 (64 games)
# Reproduce: check out the commit in each gauntlet.csv line, then run this.
cd "$(dirname "$0")/.."
PY=.venv/Scripts/python.exe
[ -x "$PY" ] || PY=.venv/bin/python
V="$PY tools/variant.py"
G="$PY tools/gauntlet.py"
D3="draft.py:BY_SIZE = {3: (CD.VENDETTA, CD.RYTH, CD.TAVI)}"
$V ar4 --set "bot.py:ALLY_RANGE = 7=>ALLY_RANGE = 4" || exit 1
$V lh1 --set "bot.py:LOW_HP_RETREAT = 0.25=>LOW_HP_RETREAT = 0.4" --set "bot.py:LOW_HP_REACH = 2=>LOW_HP_REACH = 4" || exit 1
$V lh2 --set "bot.py:LOW_HP_RETREAT = 0.25=>LOW_HP_RETREAT = 0.35" --set "bot.py:LOW_HP_REACH = 2=>LOW_HP_REACH = 3" || exit 1
$V d3a --set "$D3=>BY_SIZE = {3: (CD.VENDETTA, CD.RYTH, CD.CASSI_AND_ISSAC)}" || exit 1
$V d3b --set "$D3=>BY_SIZE = {3: (CD.VENDETTA, CD.CASSI_AND_ISSAC, CD.TAVI)}" || exit 1
for n in ar4 lh1 lh2; do
  $G $n --vs v7 --seeds 1,2 --note "queue9 $n vs v7" 2>&1 | grep -v "^created"
done
for n in d3a d3b; do
  $G $n --vs v7 --seeds 1,2,3,4,5,6,7,8 --maps collision,expanse,fragment,packs --no-econ --note "queue9 $n 3-pick draft vs v7" 2>&1 | grep -v "^created"
done
echo QUEUE9 DONE
