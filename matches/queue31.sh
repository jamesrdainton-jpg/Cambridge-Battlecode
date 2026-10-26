#!/usr/bin/env bash
# Queue 31 (2026-10-26, cambc 4.0.0, 70 maps, C++): meta play, round 3. Queue 30's best: c30hb (v14 draft + Heart of Ruin,
# her focus build, braver fights) 73/140, +3,718 vs v14. Cassi & Issac still lose at 4-5 picks. Each vs c29b (v14), seed 1:
#   c31a = c30hb + META_STUN_COMMIT (pile onto stunned enemies)
#   c31b = c30hb, bravest fights (FIGHT_ENGAGE 0.8, FIGHT_RETREAT 0.6)
#   c31c = c30hb + LOW_HP_RETREAT 0.15 (Heart of Ruin hits harder when hurt; everyone stays a little longer)
#   c31d = META_PLAY + braver fights on the plain v14 draft (does bravery alone do it?)
#   c31m = c30m (top teams' core) + META_STUN_COMMIT
cd "$(dirname "$0")/.."
PY=.venv/Scripts/python.exe; [ -x "$PY" ] || PY=.venv/bin/python
V=tools/variant.py
P="params.h:META_PLAY = false=>META_PLAY = true"; B="params.h:META_BUILD = false=>META_BUILD = true"; R="params.h:META_PAIR = false=>META_PAIR = true"
E="params.h:FIGHT_ENGAGE = 1.3=>FIGHT_ENGAGE = 1.0"; T="params.h:FIGHT_RETREAT = 0.9=>FIGHT_RETREAT = 0.75"
S="params.h:META_STUN_COMMIT = false=>META_STUN_COMMIT = true"; D="params.h:META_DRAFT = 0=>META_DRAFT"
$PY $V c31a --src cpp13 --set "$P" --set "$D = 3" --set "$B" --set "$E" --set "$T" --set "$S"
$PY $V c31b --src cpp13 --set "$P" --set "$D = 3" --set "$B" --set "params.h:FIGHT_ENGAGE = 1.3=>FIGHT_ENGAGE = 0.8" --set "params.h:FIGHT_RETREAT = 0.9=>FIGHT_RETREAT = 0.6"
$PY $V c31c --src cpp13 --set "$P" --set "$D = 3" --set "$B" --set "$E" --set "$T" --set "params.h:LOW_HP_RETREAT = 0.25=>LOW_HP_RETREAT = 0.15"
$PY $V c31d --src cpp13 --set "$P" --set "$E" --set "$T"
$PY $V c31m --src cpp13 --set "$P" --set "$D = 1" --set "$B" --set "$R" --set "$E" --set "$T" --set "$S"
N="queue 31; cambc 4.0.0, 70 maps, C++"
for v in c31a c31b c31c c31d c31m; do
  $PY tools/gauntlet.py $v --vs c29b --seeds 1 --no-econ --note "$v (meta play round 3) vs c29b (v14); $N"
done
