#!/usr/bin/env bash
# Queue 35 (2026-10-26, cambc 4.0.0, 70 maps, C++): "survivor" candidates for the next platform test against the top 3
# (DEVLOG 169: 74% of our deaths came after 11+ rounds in contact; 52% while fighting, mostly 1-on-1).
#   c35s = META_PLAY + META_DRAFT 3 + META_BUILD + ALLY_RANGE 4 + ENEMY_DPS_MUL 1.4 + FIGHT_RETREAT 1.1 + FIGHT_ENGAGE 1.5
#          + whole-team ball until round 300
#   c35p = c35s with pairs all game (BALL_SIZE 2, BALL_UNTIL 2000) instead of the early ball
# Self-play vs c29b (v14), seed 1: only a sanity check of the cost; the platform decides.
cd "$(dirname "$0")/.."
PY=.venv/Scripts/python.exe; [ -x "$PY" ] || PY=.venv/bin/python
V=tools/variant.py
S=(--set "params.h:META_PLAY = false=>META_PLAY = true" --set "params.h:META_DRAFT = 0=>META_DRAFT = 3" --set "params.h:META_BUILD = false=>META_BUILD = true"
   --set "params.h:ALLY_RANGE = 7=>ALLY_RANGE = 4" --set "params.h:ENEMY_DPS_MUL = 1.0=>ENEMY_DPS_MUL = 1.4"
   --set "params.h:FIGHT_RETREAT = 0.9=>FIGHT_RETREAT = 1.1" --set "params.h:FIGHT_ENGAGE = 1.3=>FIGHT_ENGAGE = 1.5"
   --set "params.h:DEATHBALL = false=>DEATHBALL = true")
$PY $V c35s --src cpp13 "${S[@]}" --set "params.h:BALL_UNTIL = 2000=>BALL_UNTIL = 300"
$PY $V c35p --src cpp13 "${S[@]}" --set "params.h:BALL_SIZE = 99=>BALL_SIZE = 2"
N="queue 35; cambc 4.0.0, 70 maps, C++"
for v in c35s c35p; do
  $PY tools/gauntlet.py $v --vs c29b --seeds 1 --no-econ --note "$v (survivor candidate) vs c29b (v14); $N"
done
