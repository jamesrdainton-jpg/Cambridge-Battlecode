#!/usr/bin/env bash
# Queue 38 (2026-10-27, cambc 4.0.0, 70 maps, C++): FIGHT2 (fight rewrite from platform deaths vs mid-ladder teams:
# only allies who can fight count, enemy burst/stuns/passive, enemies remembered 3 rounds, step out of a stronger
# enemy's reach, flee by the safest step, focus fire via shared memory, leave camps at 3 turns of their damage).
# f2a = cpp13 (v14 defaults) + FIGHT2 vs c29b (v14), seed 1.
cd "$(dirname "$0")/.."
PY=.venv/Scripts/python.exe; [ -x "$PY" ] || PY=.venv/bin/python
$PY tools/variant.py f2a --src cpp13 --set "params.h:FIGHT2 = false=>FIGHT2 = true"
$PY tools/gauntlet.py f2a --vs c29b --seeds 1 --no-econ --note "f2a (FIGHT2) vs c29b (v14); queue 38; cambc 4.0.0, 70 maps, C++"
