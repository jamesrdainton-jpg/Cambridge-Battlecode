#!/usr/bin/env bash
# Queue 12 (2026-10-18, cambc 2.2.5, 17 maps), mybot (= v9 flags) variants vs v9 (= v8 + FIGHT_SHIELD), DEBUG off, seeds 1,2 + economy:
#   tb20 TRIBUTE_BIG 20 / TRIBUTE_MID 10 (v8: 30/15): bank gems sooner; 79% of platform deaths are to champions,
#        who take the carried gems, and pros tribute every ~24 rounds vs our ~65
#   rs4  RECALL_SAFE 4: no recall within 4 rounds of an enemy champion within 10 tiles, none from retreats or when
#        stuck with an enemy that can reach us within 4 moves (debug logs: interrupted recalls ended in deaths)
# Reproduce: check out the commit in each gauntlet.csv line, then run this.
cd "$(dirname "$0")/.."
PY=.venv/Scripts/python.exe
[ -x "$PY" ] || PY=.venv/bin/python
V="$PY tools/variant.py"
G="$PY tools/gauntlet.py"
OFF="bot.py:DEBUG = True=>DEBUG = False"
$V tb20 --set "$OFF" --set "bot.py:TRIBUTE_BIG = 30=>TRIBUTE_BIG = 20" --set "bot.py:TRIBUTE_MID = 15=>TRIBUTE_MID = 10" || exit 1
$V rs4 --set "$OFF" --set "bot.py:RECALL_SAFE = 0=>RECALL_SAFE = 4" || exit 1
$G tb20 --vs v9 --seeds 1,2 --note "queue12 tb20 vs v9" 2>&1 | grep -v "^created"
# rs4 changes nothing against idle opponents: skip the economy run
$G rs4 --vs v9 --seeds 1,2 --no-econ --note "queue12 rs4 vs v9" 2>&1 | grep -v "^created"
echo QUEUE12 DONE
