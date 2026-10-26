#!/usr/bin/env bash
# Queue 36 (2026-10-26, cambc 4.0.0, 70 maps, C++): moderate caution (queue 35's survivors lost 26-34/140 vs v14).
#   c36r  = v14 + ENEMY_DPS_MUL 1.5 + ALLY_RANGE 4          c36re = c36r + whole-team ball until round 300
#   c36rm = c36r + META_PLAY + META_DRAFT 3 + META_BUILD (Heart of Ruin)
cd "$(dirname "$0")/.."
PY=.venv/Scripts/python.exe; [ -x "$PY" ] || PY=.venv/bin/python
V=tools/variant.py
R=(--set "params.h:ENEMY_DPS_MUL = 1.0=>ENEMY_DPS_MUL = 1.5" --set "params.h:ALLY_RANGE = 7=>ALLY_RANGE = 4")
$PY $V c36r --src cpp13 "${R[@]}"
$PY $V c36re --src cpp13 "${R[@]}" --set "params.h:DEATHBALL = false=>DEATHBALL = true" --set "params.h:BALL_UNTIL = 2000=>BALL_UNTIL = 300"
$PY $V c36rm --src cpp13 "${R[@]}" --set "params.h:META_PLAY = false=>META_PLAY = true" --set "params.h:META_DRAFT = 0=>META_DRAFT = 3" \
    --set "params.h:META_BUILD = false=>META_BUILD = true"
N="queue 36; cambc 4.0.0, 70 maps, C++"
for v in c36r c36re c36rm; do
  $PY tools/gauntlet.py $v --vs c29b --seeds 1 --no-econ --note "$v (moderate caution) vs c29b (v14); $N"
done
