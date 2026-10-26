#!/usr/bin/env bash
# Queue 34 (2026-10-26, cambc 4.0.0, 70 maps, C++): looser deathballs (queue 33's whole-team ball lost 47-50/140 vs v14 in
# self-play). Each vs c29b (v14), seed 1:
#   c34p = pairs (BALL_SIZE 2)        c34l = whole team, loose (BALL_RADIUS 7)
#   c34e = whole team until round 300 (BALL_UNTIL 300)        c34q = pairs + cpp15's flags (Heart of Ruin, braver)
cd "$(dirname "$0")/.."
PY=.venv/Scripts/python.exe; [ -x "$PY" ] || PY=.venv/bin/python
V=tools/variant.py
DB="params.h:DEATHBALL = false=>DEATHBALL = true"
$PY $V c34p --src cpp13 --set "$DB" --set "params.h:BALL_SIZE = 99=>BALL_SIZE = 2"
$PY $V c34l --src cpp13 --set "$DB" --set "params.h:BALL_RADIUS = 4=>BALL_RADIUS = 7"
$PY $V c34e --src cpp13 --set "$DB" --set "params.h:BALL_UNTIL = 2000=>BALL_UNTIL = 300"
$PY $V c34q --src cpp13 --set "$DB" --set "params.h:BALL_SIZE = 99=>BALL_SIZE = 2" --set "params.h:META_PLAY = false=>META_PLAY = true" \
    --set "params.h:META_DRAFT = 0=>META_DRAFT = 3" --set "params.h:META_BUILD = false=>META_BUILD = true" \
    --set "params.h:FIGHT_ENGAGE = 1.3=>FIGHT_ENGAGE = 0.8" --set "params.h:FIGHT_RETREAT = 0.9=>FIGHT_RETREAT = 0.6"
N="queue 34; cambc 4.0.0, 70 maps, C++"
for v in c34p c34l c34e c34q; do
  $PY tools/gauntlet.py $v --vs c29b --seeds 1 --no-econ --note "$v (looser ball) vs c29b (v14); $N"
done
