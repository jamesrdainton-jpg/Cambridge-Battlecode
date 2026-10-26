#!/usr/bin/env bash
# Queue 32 (2026-10-26, cambc 4.0.0, 70 maps, C++): meta play, round 4. Queue 31's best: c31b (v14 draft + Heart of Ruin,
# her focus build, FIGHT_ENGAGE 0.8 / FIGHT_RETREAT 0.6) 81/140, +5,067 vs v14. Each vs c29b (v14), seed 1, plus c31b seed 2:
#   c32a = c31b + META_STUN_COMMIT          c32b = c31b with FIGHT_ENGAGE 0.6 / FIGHT_RETREAT 0.45
#   c32v = plain v14 draft + META_PLAY + 0.8 / 0.6 (bravery without Heart of Ruin)
#   c32m = top teams' core + build + pair + stun commit + META_CASSI + 0.8 / 0.6
#   c32t = HoR, Vesper, Vendetta, Tavi, C&I + build + pair + META_CASSI + 0.8 / 0.6
cd "$(dirname "$0")/.."
PY=.venv/Scripts/python.exe; [ -x "$PY" ] || PY=.venv/bin/python
V=tools/variant.py
P="params.h:META_PLAY = false=>META_PLAY = true"; B="params.h:META_BUILD = false=>META_BUILD = true"; R="params.h:META_PAIR = false=>META_PAIR = true"
E8="params.h:FIGHT_ENGAGE = 1.3=>FIGHT_ENGAGE = 0.8"; T6="params.h:FIGHT_RETREAT = 0.9=>FIGHT_RETREAT = 0.6"
S="params.h:META_STUN_COMMIT = false=>META_STUN_COMMIT = true"; C="params.h:META_CASSI = false=>META_CASSI = true"
D="params.h:META_DRAFT = 0=>META_DRAFT"
$PY $V c32a --src cpp13 --set "$P" --set "$D = 3" --set "$B" --set "$E8" --set "$T6" --set "$S"
$PY $V c32b --src cpp13 --set "$P" --set "$D = 3" --set "$B" --set "params.h:FIGHT_ENGAGE = 1.3=>FIGHT_ENGAGE = 0.6" --set "params.h:FIGHT_RETREAT = 0.9=>FIGHT_RETREAT = 0.45"
$PY $V c32v --src cpp13 --set "$P" --set "$E8" --set "$T6"
$PY $V c32m --src cpp13 --set "$P" --set "$D = 1" --set "$B" --set "$R" --set "$S" --set "$C" --set "$E8" --set "$T6"
$PY $V c32t --src cpp13 --set "$P" --set "$D = 2" --set "$B" --set "$R" --set "$C" --set "$E8" --set "$T6"
N="queue 32; cambc 4.0.0, 70 maps, C++"
for v in c32a c32b c32v c32m c32t; do
  $PY tools/gauntlet.py $v --vs c29b --seeds 1 --no-econ --note "$v (meta play round 4) vs c29b (v14); $N"
done
$PY tools/gauntlet.py c31b --vs c29b --seeds 2 --no-econ --note "c31b vs c29b (v14) seed 2 confirmation; $N"
