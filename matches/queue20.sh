#!/usr/bin/env bash
# Queue 20 (2026-10-25, cambc 3.0.5, 40 maps): parity of the C++ port (bots/cpp13, commit 2ce2aae) with the Python v13.
# A faithful port should score ~50% head to head and farm about as fast unopposed.
cd "$(dirname "$0")/.."
PY=.venv/Scripts/python.exe; [ -x "$PY" ] || PY=.venv/bin/python
$PY tools/gauntlet.py cpp13 --vs v13 --seeds 1,2 --note "cpp13 (C++ port of v13) vs v13 parity; cambc 3.0.5, 40 maps"
