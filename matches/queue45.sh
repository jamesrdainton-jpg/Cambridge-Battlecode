#!/usr/bin/env bash
# Queue 45 (2026-10-27, cambc 4.0.0, 70 maps, C++): the full package for the next platform candidate.
# cf = BUILD_30 6 + FIGHT2 (allies within 6) + FEAR + UNSTICK + LOCKED_OPEN, vs b6 (BUILD_30 6) and vs c29b (v14).
cd "$(dirname "$0")/.."
PY=.venv/Scripts/python.exe; [ -x "$PY" ] || PY=.venv/bin/python
$PY tools/variant.py cf --src cpp13 --set "params.h:BUILD_30 = 4=>BUILD_30 = 6" --set "params.h:FIGHT2 = false=>FIGHT2 = true" \
  --set "params.h:FIGHT2_ALLY = 4=>FIGHT2_ALLY = 6" --set "params.h:FEAR = false=>FEAR = true" --set "params.h:UNSTICK = false=>UNSTICK = true" \
  --set "params.h:LOCKED_OPEN = false=>LOCKED_OPEN = true"
$PY tools/gauntlet.py cf --vs b6 --seeds 1,2 --no-econ --note "cf (BUILD_30 6 + FIGHT2 allies 6 + FEAR + UNSTICK + LOCKED_OPEN) vs b6; queue 45; cambc 4.0.0, 70 maps, C++"
$PY tools/gauntlet.py cf --vs c29b --seeds 1,2 --no-econ --note "cf (BUILD_30 6 + FIGHT2 allies 6 + FEAR + UNSTICK + LOCKED_OPEN) vs c29b (v14); queue 45; cambc 4.0.0, 70 maps, C++"
