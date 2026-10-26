#!/usr/bin/env bash
# Queue 31 (2026-10-26, cambc 4.0.0, 70 maps, 4-core Linux cloud machine): cpp15 (the C++ release) vs v14 (the Python
# bot currently uploaded), seed 1, 140 games.
cd "$(dirname "$0")/.."
PY=.venv/Scripts/python.exe; [ -x "$PY" ] || PY=.venv/bin/python
$PY tools/gauntlet.py cpp15 --vs v14 --seeds 1 --no-econ --jobs ${JOBS:-6} --note "cpp15 (C++ release) vs v14 (Python, uploaded); queue 31; cambc 4.0.0, 70 maps"
echo QUEUE31 DONE
