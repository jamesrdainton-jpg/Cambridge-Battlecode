#!/usr/bin/env bash
# Queue 33 (2026-10-26, cambc 4.0.0, 70 maps, C++): DEATHBALL (the whole team farms and fights together behind a
# leader). Platform games vs the top 3 (DEVLOG 168): v14 0/15, cpp15 1/15; we die ~6x as often as they do. Each vs c29b
# (v14), seed 1:
#   c33a = v14 + DEATHBALL (radius 4)            c33b = v14 + DEATHBALL radius 3
#   c33c = cpp15's flags + DEATHBALL             c33d = v14 + DEATHBALL + braver fights (0.8 / 0.6)
cd "$(dirname "$0")/.."
PY=.venv/Scripts/python.exe; [ -x "$PY" ] || PY=.venv/bin/python
V=tools/variant.py
DB="params.h:DEATHBALL = false=>DEATHBALL = true"
E8="params.h:FIGHT_ENGAGE = 1.3=>FIGHT_ENGAGE = 0.8"; T6="params.h:FIGHT_RETREAT = 0.9=>FIGHT_RETREAT = 0.6"
$PY $V c33a --src cpp13 --set "$DB"
$PY $V c33b --src cpp13 --set "$DB" --set "params.h:BALL_RADIUS = 4=>BALL_RADIUS = 3"
$PY $V c33c --src cpp13 --set "$DB" --set "params.h:META_PLAY = false=>META_PLAY = true" --set "params.h:META_DRAFT = 0=>META_DRAFT = 3" \
    --set "params.h:META_BUILD = false=>META_BUILD = true" --set "$E8" --set "$T6"
$PY $V c33d --src cpp13 --set "$DB" --set "$E8" --set "$T6"
N="queue 33; cambc 4.0.0, 70 maps, C++"
for v in c33a c33b c33c c33d; do
  $PY tools/gauntlet.py $v --vs c29b --seeds 1 --no-econ --note "$v (deathball) vs c29b (v14); $N"
done
