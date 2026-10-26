#!/usr/bin/env bash
# Queue 21 (2026-10-25, cambc 3.0.5, 40 maps): early economy on top of BUILD_30 1 (the replays: our dying champions had
# spent 0 gold in the first 300 rounds vs their killers' 210; the top teams shop 11.4 times by r300, we 5.1).
#   y21a = mybot (commit b3c5a38 flags) + BUILD_30 1 (base)
#   y21g = + SHOP_GOLD 90 (shop with 3 shards' worth instead of 5)
#   y21w = + GOLD_WEIGHT 0.8 (gold counts twice as much in early target choice)
# plus y19p (FIGHT_PRIO) vs y19a on seed 2 to confirm queue 19's +3,414.
cd "$(dirname "$0")/.."
PY=.venv/Scripts/python.exe; [ -x "$PY" ] || PY=.venv/bin/python
V=tools/variant.py
B="bot.py:BUILD_30 = 0=>BUILD_30 = 1"
$PY $V y21a --set "$B"
$PY $V y21g --set "$B" --set "bot.py:SHOP_GOLD = 150=>SHOP_GOLD = 90"
$PY $V y21w --set "$B" --set "bot.py:GOLD_WEIGHT = 0.4=>GOLD_WEIGHT = 0.8"
$PY tools/gauntlet.py y21g --vs y21a --seeds 1 --no-econ --note "y21g = BUILD_30 1 + SHOP_GOLD 90 vs y21a; queue 21; cambc 3.0.5, 40 maps"
$PY tools/gauntlet.py y21w --vs y21a --seeds 1 --no-econ --note "y21w = BUILD_30 1 + GOLD_WEIGHT 0.8 vs y21a; queue 21; cambc 3.0.5, 40 maps"
$PY tools/gauntlet.py y19p --vs y19a --seeds 2 --no-econ --note "y19p (FIGHT_PRIO) vs y19a seed 2 confirmation; queue 21; cambc 3.0.5, 40 maps"
