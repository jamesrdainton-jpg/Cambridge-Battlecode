#!/usr/bin/env bash
# Queue 13 (2026-10-18, cambc 2.2.5, 17 maps), mybot (= v11 flags) variant vs v11, DEBUG off, seeds 1,2, no economy:
#   ge50 FIGHT_GEM_EXTRA 0.25 -> 0.5: champions carrying 20+ gems retreat sooner and chase later (a kill hands the
#        killer every carried gem)
# Reproduce: check out the commit in each gauntlet.csv line, then run this.
cd "$(dirname "$0")/.."
PY=.venv/Scripts/python.exe
[ -x "$PY" ] || PY=.venv/bin/python
V="$PY tools/variant.py"
G="$PY tools/gauntlet.py"
OFF="bot.py:DEBUG = True=>DEBUG = False"
$V ge50 --set "$OFF" --set "bot.py:FIGHT_GEM_EXTRA = 0.25=>FIGHT_GEM_EXTRA = 0.5" || exit 1
$G ge50 --vs v11 --seeds 1,2 --no-econ --note "queue13 ge50 vs v11" 2>&1 | grep -v "^created"
echo QUEUE13 DONE
