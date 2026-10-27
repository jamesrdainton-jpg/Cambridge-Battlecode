#!/usr/bin/env bash
# Queue 39 (2026-10-27, cambc 4.0.0, 70 maps, C++): the stronger platform teams' item order (BUILD_30 6: Jungle,
# Durability H, Monster, then Bruiser H / Bruiser S-F in turn; focus for Marcella, Heart of Ruin, Ren) on top of FIGHT2.
# f2b = cpp13 + FIGHT2 + BUILD_30 6 vs c29b (v14), seed 1; f2a (FIGHT2 alone) vs c29b seed 2 for a second read.
cd "$(dirname "$0")/.."
PY=.venv/Scripts/python.exe; [ -x "$PY" ] || PY=.venv/bin/python
$PY tools/variant.py f2b --src cpp13 --set "params.h:FIGHT2 = false=>FIGHT2 = true" --set "params.h:BUILD_30 = 4=>BUILD_30 = 6"
$PY tools/gauntlet.py f2b --vs c29b --seeds 1 --no-econ --note "f2b (FIGHT2 + BUILD_30 6) vs c29b (v14); queue 39; cambc 4.0.0, 70 maps, C++"
$PY tools/gauntlet.py f2a --vs c29b --seeds 2 --no-econ --note "f2a (FIGHT2) vs c29b (v14) seed 2; queue 39; cambc 4.0.0, 70 maps, C++"
