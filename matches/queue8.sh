#!/usr/bin/env bash
# Queue 8 (2026-10-16): gt1 (GOLD_WEIGHT 0.4, GOLD_TAPER 500) with seeds 5-8 (136 games, no economy). Rule fixed
# before running: adopt if seeds 1-8 together reach 159/272 vs v6 (the 42/72 rate) with positive gems.
cd "$(dirname "$0")/.."
PY=.venv/Scripts/python.exe
[ -x "$PY" ] || PY=.venv/bin/python
$PY tools/variant.py gt1 --set "bot.py:GOLD_WEIGHT = 0.15=>GOLD_WEIGHT = 0.4" --set "bot.py:GOLD_TAPER = 1200=>GOLD_TAPER = 500" || exit 1
$PY tools/gauntlet.py gt1 --vs v6 --seeds 5,6,7,8 --no-econ --note "queue8 gt1 confirm (seeds 5-8)" 2>&1 | grep -v "^created"
echo QUEUE8 DONE
