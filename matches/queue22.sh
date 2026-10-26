#!/usr/bin/env bash
# Queue 22 (2026-10-25, cambc 3.0.5, 40 maps): C++ port parity again after the fuel fix (go() uses compute_to, which
# stops the search at our tile). Queue 20 (full-map searches): 72/160, -6,561 vs v13; C++ capped on 1.2% of turns.
cd "$(dirname "$0")/.."
PY=.venv/Scripts/python.exe; [ -x "$PY" ] || PY=.venv/bin/python
$PY tools/gauntlet.py cpp13 --vs v13 --seeds 1,2 --note "cpp13 (C++ port, go() with compute_to) vs v13 parity; cambc 3.0.5, 40 maps"
