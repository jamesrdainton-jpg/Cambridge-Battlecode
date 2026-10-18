#!/usr/bin/env bash
# Queue 13 (2026-10-18, cambc 2.2.5, 17 maps), mybot (= v9 flags) variants vs v9 (= v8 + FIGHT_SHIELD), DEBUG off, seeds 1,2 + economy:
#   fm2  FIGHT_MEMO 2: fight on the lowest strength ratio of the last 2 rounds (stops chase/flee flip-flops)
# Reproduce: check out the commit in each gauntlet.csv line, then run this.
cd "$(dirname "$0")/.."
PY=.venv/Scripts/python.exe
[ -x "$PY" ] || PY=.venv/bin/python
V="$PY tools/variant.py"
G="$PY tools/gauntlet.py"
OFF="bot.py:DEBUG = True=>DEBUG = False"
$V fm2 --set "$OFF" --set "bot.py:FIGHT_MEMO = 0=>FIGHT_MEMO = 2" || exit 1
# fm2 changes nothing against idle opponents: skip the economy run
$G fm2 --vs v9 --seeds 1,2 --no-econ --note "queue13 fm2 vs v9" 2>&1 | grep -v "^created"
echo QUEUE13 DONE
