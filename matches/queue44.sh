#!/usr/bin/env bash
# Queue 44 (2026-10-27, cambc 4.0.0, 70 maps, C++): FEAR (after a retreat, avoid the enemies' reach for 8 turns and drop
# a target inside it: the other cause of bouncing) with UNSTICK, on BUILD_30 6. bf6 vs b6, seeds 1,2; bf6 vs c29b (v14).
cd "$(dirname "$0")/.."
PY=.venv/Scripts/python.exe; [ -x "$PY" ] || PY=.venv/bin/python
$PY tools/variant.py bf6 --src cpp13 --set "params.h:UNSTICK = false=>UNSTICK = true" --set "params.h:FEAR = false=>FEAR = true" --set "params.h:BUILD_30 = 4=>BUILD_30 = 6"
$PY tools/gauntlet.py bf6 --vs b6 --seeds 1,2 --no-econ --note "bf6 (BUILD_30 6 + UNSTICK + FEAR) vs b6 (BUILD_30 6); queue 44; cambc 4.0.0, 70 maps, C++"
$PY tools/gauntlet.py bf6 --vs c29b --seeds 1,2 --no-econ --note "bf6 (BUILD_30 6 + UNSTICK + FEAR) vs c29b (v14); queue 44; cambc 4.0.0, 70 maps, C++"
