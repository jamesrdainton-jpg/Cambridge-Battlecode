#!/usr/bin/env bash
# Queue 43 (2026-10-27, cambc 4.0.0, 70 maps, C++): UNSTICK (go() bounced between two tiles at the edge of awake camps'
# reach: 8,505 champion-rounds in the 60 panel games, research/2026-10-27/tools/oscillation.py).
# u1 = v14 + UNSTICK vs c29b (v14); bu6 = BUILD_30 6 + UNSTICK vs b6 (BUILD_30 6). Seeds 1,2.
cd "$(dirname "$0")/.."
PY=.venv/Scripts/python.exe; [ -x "$PY" ] || PY=.venv/bin/python
$PY tools/variant.py u1 --src cpp13 --set "params.h:UNSTICK = false=>UNSTICK = true"
$PY tools/gauntlet.py u1 --vs c29b --seeds 1,2 --no-econ --note "u1 (UNSTICK) vs c29b (v14); queue 43; cambc 4.0.0, 70 maps, C++"
$PY tools/variant.py bu6 --src cpp13 --set "params.h:UNSTICK = false=>UNSTICK = true" --set "params.h:BUILD_30 = 4=>BUILD_30 = 6"
$PY tools/gauntlet.py bu6 --vs b6 --seeds 1,2 --no-econ --note "bu6 (BUILD_30 6 + UNSTICK) vs b6 (BUILD_30 6); queue 43; cambc 4.0.0, 70 maps, C++"
