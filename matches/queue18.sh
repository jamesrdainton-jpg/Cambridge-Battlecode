#!/usr/bin/env bash
# Queue 18 (2026-10-25, cambc 3.0.5, 40 maps): the top teams' item builds vs v13.
#   x16a = mybot + BUILD_30 1: Treasure first, Jungle H, Bruiser S, Durability H, then Bruiser S/H stacks
#   x16b = mybot + BUILD_30 2: Treasure first, then Bruiser S/H only
cd "$(dirname "$0")/.."
PY=.venv/Scripts/python.exe; [ -x "$PY" ] || PY=.venv/bin/python
$PY tools/variant.py x16a --set "bot.py:BUILD_30 = 0=>BUILD_30 = 1"
$PY tools/variant.py x16b --set "bot.py:BUILD_30 = 0=>BUILD_30 = 2"
$PY tools/gauntlet.py x16a --vs v13 --seeds 1,2 --note "x16a = v13 + BUILD_30 1 (Treasure, Jungle, Bruiser stacks); cambc 3.0.5, 40 maps"
$PY tools/gauntlet.py x16b --vs v13 --seeds 1,2 --note "x16b = v13 + BUILD_30 2 (Treasure, then Bruiser only); cambc 3.0.5, 40 maps"
