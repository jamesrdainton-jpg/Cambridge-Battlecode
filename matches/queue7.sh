#!/usr/bin/env bash
# Queue 7 (2026-10-16, cambc 2.2.2, 17 maps): confirm the two borderline results of queue 6 with fresh seeds
# 3,4 (68 games each; adoption bar over both seed sets: 80/136 with positive gems), and test them together.
# Reproduce: check out the commit in each gauntlet.csv line, then run this.
cd "$(dirname "$0")/.."
PY=.venv/Scripts/python.exe
[ -x "$PY" ] || PY=.venv/bin/python
V="$PY tools/variant.py"
G="$PY tools/gauntlet.py"
$V wd1 --set "bot.py:WARDS = False=>WARDS = True" || exit 1
$V gt1 --set "bot.py:GOLD_WEIGHT = 0.15=>GOLD_WEIGHT = 0.4" --set "bot.py:GOLD_TAPER = 1200=>GOLD_TAPER = 500" || exit 1
$V wg1 --set "bot.py:WARDS = False=>WARDS = True" --set "bot.py:GOLD_WEIGHT = 0.15=>GOLD_WEIGHT = 0.4" --set "bot.py:GOLD_TAPER = 1200=>GOLD_TAPER = 500" || exit 1
$G wd1 --vs v6 --seeds 3,4 --note "queue7 wd1 confirm (seeds 3,4)" 2>&1 | grep -v "^created"
$G gt1 --vs v6 --seeds 3,4 --note "queue7 gt1 confirm (seeds 3,4)" 2>&1 | grep -v "^created"
$G wg1 --vs v6 --seeds 1,2 --note "queue7 wg1 wards + early gold vs v6" 2>&1 | grep -v "^created"
echo QUEUE7 DONE
