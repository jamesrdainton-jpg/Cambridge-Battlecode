#!/usr/bin/env bash
# Queue 4 (2026-10-16, cambc 2.2.2, 17-map platform pool; 2 seeds = 68 games per opponent):
# sp1 = mybot + IGNORE_SPAWN_CAMPERS (fixes the rushbait-v2 spawn stand-off) vs v6, then the reference
# v6 vs meta (v6 logic with the platform's most common draft) to see whether that draft beats ours.
cd "$(dirname "$0")/.."
PY=.venv/Scripts/python.exe
[ -x "$PY" ] || PY=.venv/bin/python
V="$PY tools/variant.py"
G="$PY tools/gauntlet.py"
$V sp1 --set "bot.py:IGNORE_SPAWN_CAMPERS = False=>IGNORE_SPAWN_CAMPERS = True" || exit 1
$G sp1 --vs v6 --seeds 1,2 --note "queue4 sp1 ignore spawn campers vs v6" 2>&1 | grep -v "^created"
$G v6 --vs meta --seeds 1,2 --no-econ --note "queue4 v6 vs meta (platform draft)" 2>&1 | grep -v "^created"
echo QUEUE4 DONE
