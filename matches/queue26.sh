#!/usr/bin/env bash
# Queue 26 (2026-10-26, cambc 4.0.0, 70 maps): v14 decisions on queue 25's best build (BUILD_30 4, Monster first:
# 97/140, +19,696 vs v13).
#   z26b = mybot + BUILD_30 4 + FIGHT_PRIO                 c26b = cpp13 + the same (C++)
#   z26g = z26b + LOCKED_GOLD (gold mode on altar-locked maps) c26g = c26b + LOCKED_GOLD
# 1. Gold mode on the three altar-locked maps (01boss-battle, 02guardians, 02the-pack), seeds 1-4, both languages.
# 2. z26g vs v13 on seed 2 (confirms queue 25 on a second seed, with gold mode).
# 3. Language: c26g vs z26g, seeds 1,2 (the user prefers C++ if it plays at least as well).
cd "$(dirname "$0")/.."
PY=.venv/Scripts/python.exe; [ -x "$PY" ] || PY=.venv/bin/python
V=tools/variant.py
B="bot.py:BUILD_30 = 0=>BUILD_30 = 4"; F="bot.py:FIGHT_PRIO = False=>FIGHT_PRIO = True"; G="bot.py:LOCKED_GOLD = False=>LOCKED_GOLD = True"
CB="params.h:BUILD_30 = 0=>BUILD_30 = 4"; CF="params.h:FIGHT_PRIO = false=>FIGHT_PRIO = true"; CG="params.h:LOCKED_GOLD = false=>LOCKED_GOLD = true"
$PY $V z26b --set "$B" --set "$F"
$PY $V z26g --set "$B" --set "$F" --set "$G"
$PY $V c26b --src cpp13 --set "$CB" --set "$CF"
$PY $V c26g --src cpp13 --set "$CB" --set "$CF" --set "$CG"
N="queue 26; cambc 4.0.0"
L=01boss-battle,02guardians,02the-pack
$PY tools/gauntlet.py z26g --vs z26b --seeds 1,2,3,4 --no-econ --maps $L --note "z26g (LOCKED_GOLD) vs z26b, altar-locked maps only; $N"
$PY tools/gauntlet.py c26g --vs c26b --seeds 1,2,3,4 --no-econ --maps $L --note "c26g (LOCKED_GOLD, C++) vs c26b, altar-locked maps only; $N"
$PY tools/gauntlet.py z26g --vs v13 --seeds 2 --no-econ --note "z26g = BUILD_30 4 + FIGHT_PRIO + LOCKED_GOLD vs v13 seed 2; $N, 70 maps"
$PY tools/gauntlet.py c26g --vs z26g --seeds 1,2 --no-econ --note "c26g vs z26g: same flags, C++ vs Python; $N, 70 maps"
