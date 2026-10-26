#!/usr/bin/env bash
# Queue 15 (2026-10-25, cambc 3.0.5, 40 maps): squad waiting on top of the 3.0 camp-stats fix (commit 74afa8d).
# x13a = mybot DEBUG off (82/160 vs v12: wins all 24 golem-map games, 58/136 elsewhere; waits 11-12% of turns vs v12's 1%).
cd "$(dirname "$0")/.."
PY=.venv/Scripts/python.exe; [ -x "$PY" ] || PY=.venv/bin/python
$PY tools/variant.py x13b --set "bot.py:WAIT_LIMIT = 40=>WAIT_LIMIT = 0"
$PY tools/variant.py x13c --set "bot.py:WAIT_LIMIT = 40=>WAIT_LIMIT = 10"
$PY tools/gauntlet.py x13b --vs v12 --seeds 1,2 --no-econ --note "x13b = x13a + WAIT_LIMIT 0 (never wait for a squad); cambc 3.0.5, 40 maps"
$PY tools/gauntlet.py x13c --vs v12 --seeds 1,2 --no-econ --note "x13c = x13a + WAIT_LIMIT 10; cambc 3.0.5, 40 maps"
