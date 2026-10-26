#!/usr/bin/env bash
# Queue 29 (2026-10-26, cambc 4.0.0, 70 maps, C++): making the meta picks work (the user's request: be brazen).
# META_PLAY = Heart of Ruin's stun-dash in fights and on camps, stunned enemies valued, Cassi's stun on camps, shields
# whenever hurt. Each vs c29b (= cpp13 as uploaded, v14), seed 1:
#   c29s = META_PLAY, v14 draft          c29m = META_PLAY + META_DRAFT 1 (HoR, Vesper, Vendetta, C&I, Marcella)
#   c29t = META_PLAY + META_DRAFT 2 (HoR, Vesper, Vendetta, Tavi, C&I)   c29h = META_PLAY + META_DRAFT 3 (v14 + HoR)
#   c29a = c29m with braver fights (FIGHT_ENGAGE 1.3 -> 1.0, FIGHT_RETREAT 0.9 -> 0.75)
cd "$(dirname "$0")/.."
PY=.venv/Scripts/python.exe; [ -x "$PY" ] || PY=.venv/bin/python
V=tools/variant.py
P="params.h:META_PLAY = false=>META_PLAY = true"
$PY $V c29b --src cpp13
$PY $V c29s --src cpp13 --set "$P"
$PY $V c29m --src cpp13 --set "$P" --set "params.h:META_DRAFT = 0=>META_DRAFT = 1"
$PY $V c29t --src cpp13 --set "$P" --set "params.h:META_DRAFT = 0=>META_DRAFT = 2"
$PY $V c29h --src cpp13 --set "$P" --set "params.h:META_DRAFT = 0=>META_DRAFT = 3"
$PY $V c29a --src cpp13 --set "$P" --set "params.h:META_DRAFT = 0=>META_DRAFT = 1" \
    --set "params.h:FIGHT_ENGAGE = 1.3=>FIGHT_ENGAGE = 1.0" --set "params.h:FIGHT_RETREAT = 0.9=>FIGHT_RETREAT = 0.75"
N="queue 29; cambc 4.0.0, 70 maps, C++"
for v in c29m c29t c29h c29s c29a; do
  $PY tools/gauntlet.py $v --vs c29b --seeds 1 --no-econ --note "$v (meta play) vs c29b (v14); $N"
done
