#!/usr/bin/env bash
# Queue 41 (2026-10-27, cambc 4.0.0, C++): LOCKED_OPEN (on the three altar-locked maps, also value gems and tribute
# once an altar can be walked to) on top of BUILD_30 6. lo6 vs b6 (BUILD_30 6 alone) on 01boss-battle, 02guardians and
# 02the-pack, seeds 1-4 (24 games); lo6 vs c29b (v14) on the same maps.
cd "$(dirname "$0")/.."
PY=.venv/Scripts/python.exe; [ -x "$PY" ] || PY=.venv/bin/python
$PY tools/variant.py lo6 --src cpp13 --set "params.h:BUILD_30 = 4=>BUILD_30 = 6" --set "params.h:LOCKED_OPEN = false=>LOCKED_OPEN = true"
$PY tools/gauntlet.py lo6 --vs b6 --seeds 1,2,3,4 --maps 01boss-battle,02guardians,02the-pack --no-econ --note "lo6 (BUILD_30 6 + LOCKED_OPEN) vs b6 (BUILD_30 6) on the locked maps; queue 41; cambc 4.0.0, C++"
$PY tools/gauntlet.py lo6 --vs c29b --seeds 1,2,3,4 --maps 01boss-battle,02guardians,02the-pack --no-econ --note "lo6 (BUILD_30 6 + LOCKED_OPEN) vs c29b (v14) on the locked maps; queue 41; cambc 4.0.0, C++"
