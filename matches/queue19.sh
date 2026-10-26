#!/usr/bin/env bash
# Queue 19 (2026-10-25, cambc 3.0.5, 40 maps): each fight flag alone, on top of BUILD_30 1 (queue 18: 99/160 vs v13).
# Base y19a = mybot (commit b3c5a38) + BUILD_30 1. Seed 1 screening, 80 games each vs the base.
cd "$(dirname "$0")/.."
PY=.venv/Scripts/python.exe; [ -x "$PY" ] || PY=.venv/bin/python
V=tools/variant.py
B="bot.py:BUILD_30 = 0=>BUILD_30 = 1"
$PY $V y19a --set "$B"
$PY $V y19p --set "$B" --set "bot.py:FIGHT_PRIO = False=>FIGHT_PRIO = True"
$PY $V y19h --set "$B" --set "bot.py:HELP_CALLS = False=>HELP_CALLS = True"
$PY $V y19s --set "$B" --set "bot.py:STAND_REACH = 0=>STAND_REACH = 2"
$PY $V y19c --set "$B" --set "bot.py:FIGHT_COMMIT = 0=>FIGHT_COMMIT = 3"
for X in y19p y19h y19s y19c; do
  $PY tools/gauntlet.py $X --vs y19a --seeds 1 --no-econ --note "$X vs y19a (BUILD_30 1 base); queue 19 fight-flag screening; cambc 3.0.5, 40 maps"
done
