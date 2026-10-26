#!/usr/bin/env bash
# Queue 30 (2026-10-26, cambc 4.0.0, 70 maps, C++): meta play, round 2. Queue 29 (vs v14, seed 1): v14 draft + Heart of
# Ruin 67/140 (even); HoR, Vesper, Vendetta, Tavi, C&I 54/140; the top teams' core 42/140 (46 with braver fights).
# Adds META_BUILD (Heart of Ruin's focus/health build) and META_PAIR (Cassi takes Issac's target). Each vs c29b (v14):
#   c30h  = META_DRAFT 3 (v14 + HoR) + META_BUILD
#   c30hb = c30h + braver fights (FIGHT_ENGAGE 1.0, FIGHT_RETREAT 0.75)
#   c30t  = META_DRAFT 2 (HoR, Vesper, Vendetta, Tavi, C&I) + META_BUILD + META_PAIR
#   c30tb = c30t + braver fights
#   c30m  = META_DRAFT 1 (top teams' core) + META_BUILD + META_PAIR + braver fights
cd "$(dirname "$0")/.."
PY=.venv/Scripts/python.exe; [ -x "$PY" ] || PY=.venv/bin/python
V=tools/variant.py
P="params.h:META_PLAY = false=>META_PLAY = true"; B="params.h:META_BUILD = false=>META_BUILD = true"; R="params.h:META_PAIR = false=>META_PAIR = true"
E="params.h:FIGHT_ENGAGE = 1.3=>FIGHT_ENGAGE = 1.0"; T="params.h:FIGHT_RETREAT = 0.9=>FIGHT_RETREAT = 0.75"
D="params.h:META_DRAFT = 0=>META_DRAFT"
$PY $V c30h --src cpp13 --set "$P" --set "$D = 3" --set "$B"
$PY $V c30hb --src cpp13 --set "$P" --set "$D = 3" --set "$B" --set "$E" --set "$T"
$PY $V c30t --src cpp13 --set "$P" --set "$D = 2" --set "$B" --set "$R"
$PY $V c30tb --src cpp13 --set "$P" --set "$D = 2" --set "$B" --set "$R" --set "$E" --set "$T"
$PY $V c30m --src cpp13 --set "$P" --set "$D = 1" --set "$B" --set "$R" --set "$E" --set "$T"
N="queue 30; cambc 4.0.0, 70 maps, C++"
for v in c30h c30hb c30t c30tb c30m; do
  $PY tools/gauntlet.py $v --vs c29b --seeds 1 --no-econ --note "$v (meta play round 2) vs c29b (v14); $N"
done
