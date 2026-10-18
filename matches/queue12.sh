#!/usr/bin/env bash
# Queue 12 (2026-10-18, cambc 2.2.5, 17 maps), mybot (= v8 flags) variants vs v8, DEBUG off, seeds 1,2 + economy:
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
for n in tb20 rs4; do
  $G $n --vs v8 --seeds 1,2 --note "queue12 $n vs v8" 2>&1 | grep -v "^created"
done
echo QUEUE12 DONE
