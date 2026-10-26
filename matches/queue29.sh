#!/usr/bin/env bash
# Queue 29 (2026-10-26, cambc 4.0.0, 70 maps, 4-core Linux cloud machine), C++ vs the frozen cpp14 (= v14).
# Queue 28 (seed 1): zh1 consensus draft + HOR_DASH 62/140; zd1 the same draft without HOR_DASH 36/140; zh2 Marcella
# core + HOR_DASH 67/140 (3-pick maps 18/24 +4,738, 4-pick 16/32, 5-pick 33/84); zg EARLY_GOLD 1.5 73/140 +218;
# zr FIGHT_RESPECT 1.5 58/140.
#   zm4 = HOR_DASH + DRAFT_SET 4 (Marcella core on 3-pick maps only), seeds 1,2
#   zho = HOLD_FIX alone, seeds 1,2
#   zg  = EARLY_GOLD 1.5, seed 2 (seed 1 in queue 28)
#   zc  = HOR_DASH + DRAFT_SET 4 + EARLY_GOLD 1.5 + HOLD_FIX + TELEMETRY (the candidate), seeds 1,2
cd "$(dirname "$0")/.."
PY=.venv/Scripts/python.exe; [ -x "$PY" ] || PY=.venv/bin/python
V=tools/variant.py
H="params.h:HOR_DASH = false=>HOR_DASH = true"; D4="params.h:DRAFT_SET = 0=>DRAFT_SET = 4"
G="params.h:EARLY_GOLD = 0.0=>EARLY_GOLD = 1.5"; O="params.h:HOLD_FIX = false=>HOLD_FIX = true"
T="params.h:TELEMETRY = false=>TELEMETRY = true"
$PY $V zm4 --src cpp13 --set "$H" --set "$D4" >/dev/null
$PY $V zho --src cpp13 --set "$O" >/dev/null
$PY $V zg --src cpp13 --set "$G" >/dev/null
$PY $V zc --src cpp13 --set "$H" --set "$D4" --set "$G" --set "$O" --set "$T" >/dev/null
N="queue 29; cambc 4.0.0, 70 maps"
J="--jobs ${JOBS:-6}"
$PY tools/gauntlet.py zm4 --vs cpp14 --seeds 1,2 --no-econ $J --note "zm4 = HOR_DASH + DRAFT_SET 4 vs cpp14; $N"
$PY tools/gauntlet.py zho --vs cpp14 --seeds 1,2 --no-econ $J --note "zho = HOLD_FIX vs cpp14; $N"
$PY tools/gauntlet.py zg --vs cpp14 --seeds 2 --no-econ $J --note "zg = EARLY_GOLD 1.5 to r150 vs cpp14, seed 2; $N"
$PY tools/gauntlet.py zc --vs cpp14 --seeds 1,2 --no-econ $J --note "zc = HOR_DASH + DRAFT_SET 4 + EARLY_GOLD 1.5 + HOLD_FIX + TELEMETRY vs cpp14; $N"
echo QUEUE29 DONE
