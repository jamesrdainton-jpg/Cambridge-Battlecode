#!/usr/bin/env bash
# Queue 13 (2026-10-18, cambc 2.2.5, 17 maps), mybot (= v8 flags) variants vs v8, DEBUG off, seeds 1,2 + economy:
#   fm2  FIGHT_MEMO 2: fight on the lowest strength ratio of the last 2 rounds (stops chase/flee flip-flops)
# Reproduce: check out the commit in each gauntlet.csv line, then run this.
cd "$(dirname "$0")/.."
PY=.venv/Scripts/python.exe
[ -x "$PY" ] || PY=.venv/bin/python
V="$PY tools/variant.py"
G="$PY tools/gauntlet.py"
OFF="bot.py:DEBUG = True=>DEBUG = False"
$V fm2 --set "$OFF" --set "bot.py:FIGHT_MEMO = 0=>FIGHT_MEMO = 2" || exit 1
for n in fm2; do
  $G $n --vs v8 --seeds 1,2 --note "queue13 $n vs v8" 2>&1 | grep -v "^created"
done
echo QUEUE13 DONE
