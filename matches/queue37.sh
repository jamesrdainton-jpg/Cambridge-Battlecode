#!/usr/bin/env bash
# Queue 37 (2026-10-26, cambc 4.0.0, 70 maps, C++): RECALL_TRICK (Mite and Trzy Kwaterki end 90% / 76% of their turns
# with a recall that they cancel at the start of the next turn). c37r = v14 + RECALL_TRICK vs c29b (v14), seed 1.
cd "$(dirname "$0")/.."
PY=.venv/Scripts/python.exe; [ -x "$PY" ] || PY=.venv/bin/python
$PY tools/variant.py c37r --src cpp13 --set "params.h:RECALL_TRICK = false=>RECALL_TRICK = true"
$PY tools/gauntlet.py c37r --vs c29b --seeds 1 --no-econ --note "c37r (RECALL_TRICK) vs c29b (v14); queue 37; cambc 4.0.0, 70 maps, C++"
