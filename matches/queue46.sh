#!/usr/bin/env bash
# Queue 46 (2026-10-27, cambc 4.0.0, 70 maps, C++): CAMP_AWAKE (a damaged camp counted as awake forever; ask the engine
# whether it is asleep). ca6 = BUILD_30 6 + CAMP_AWAKE vs b6 (BUILD_30 6) and vs c29b (v14), seeds 1,2.
cd "$(dirname "$0")/.."
PY=.venv/Scripts/python.exe; [ -x "$PY" ] || PY=.venv/bin/python
$PY tools/variant.py ca6 --src cpp13 --set "params.h:BUILD_30 = 4=>BUILD_30 = 6" --set "params.h:CAMP_AWAKE = false=>CAMP_AWAKE = true"
$PY tools/gauntlet.py ca6 --vs b6 --seeds 1,2 --no-econ --note "ca6 (BUILD_30 6 + CAMP_AWAKE) vs b6 (BUILD_30 6); queue 46; cambc 4.0.0, 70 maps, C++"
$PY tools/gauntlet.py ca6 --vs c29b --seeds 1,2 --no-econ --note "ca6 (BUILD_30 6 + CAMP_AWAKE) vs c29b (v14); queue 46; cambc 4.0.0, 70 maps, C++"
