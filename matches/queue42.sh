#!/usr/bin/env bash
# Queue 42 (2026-10-27, cambc 4.0.0, 70 maps, C++): item-order variants around BUILD_30 6 (the stronger teams' order,
# 158/280 vs v14 in queue 40), and the cpp15 meta flags on top of it. All vs c29b (v14), seeds 1,2.
# b7 = Prospector first; b8 = Durability H first; b9 = no Monster stage; m6 = BUILD_30 6 + cpp15's flags (Heart of Ruin
# for Marcella at 4 picks / Ryth at 5, META_PLAY, META_BUILD, engage 0.8 / retreat 0.6).
cd "$(dirname "$0")/.."
PY=.venv/Scripts/python.exe; [ -x "$PY" ] || PY=.venv/bin/python
for b in 7 8 9; do
  $PY tools/variant.py b$b --src cpp13 --set "params.h:BUILD_30 = 4=>BUILD_30 = $b"
  $PY tools/gauntlet.py b$b --vs c29b --seeds 1,2 --no-econ --note "b$b (BUILD_30 $b) vs c29b (v14); queue 42; cambc 4.0.0, 70 maps, C++"
done
$PY tools/variant.py m6 --src cpp13 --set "params.h:BUILD_30 = 4=>BUILD_30 = 6" --set "params.h:META_PLAY = false=>META_PLAY = true" \
  --set "params.h:META_DRAFT = 0=>META_DRAFT = 3" --set "params.h:META_BUILD = false=>META_BUILD = true" \
  --set "params.h:FIGHT_ENGAGE = 1.3=>FIGHT_ENGAGE = 0.8" --set "params.h:FIGHT_RETREAT = 0.9=>FIGHT_RETREAT = 0.6"
$PY tools/gauntlet.py m6 --vs c29b --seeds 1,2 --no-econ --note "m6 (BUILD_30 6 + cpp15 meta flags) vs c29b (v14); queue 42; cambc 4.0.0, 70 maps, C++"
