#!/usr/bin/env bash
# Queue 14 (2026-10-19, cambc 2.2.5, 17 maps, 4-core Linux cloud machine): implementing the research report
# research/2026-10-19/REPORT.md. Every variant below is rebuilt from the frozen v12 (commit 826b5cc) with
# tools/variant.py; v12 itself = bots/mybot with DEBUG off. Head-to-heads use research/2026-10-19/tools/h2h.py
# (seeded copies of both bots, every map from both sides, 4 jobs; Linux paths: .venv/bin/python). Outputs go to
# matches/research/ (git-ignored). Results are DEVLOG rows 135-142.
#   x12c  boss poking on (MONOLITH_POKE with the live ring, capture step and shared poke health), our draft, no packs
#   x12d  x12c + POKE_AVOID_ENEMY 20 (stop poking a group after an enemy came within 8 tiles of it)
#   x12e  poking off, our draft, no packs  (= v12 without the pro draft)
#   xCchase  v12 + CHASE_SAFE (research/2026-10-19/patches/chase.py)
# Reproduce: git checkout 826b5cc, then run this.
cd "$(dirname "$0")/.."
PY=.venv/bin/python
V="$PY tools/variant.py"
H="$PY research/2026-10-19/tools/h2h.py"
POKE="bot.py:MONOLITH_POKE = False=>MONOLITH_POKE = True"
OURS="draft.py:PRO_DRAFT = (4, 5)=>PRO_DRAFT = ()"
NOPACK="bot.py:PACK_UNTIL = 150=>PACK_UNTIL = 0"
$V x12c --src v12 --set "$POKE" --set "$OURS" --set "$NOPACK" || exit 1
$V x12d --src v12 --set "$POKE" --set "$OURS" --set "$NOPACK" --set "bot.py:POKE_AVOID_ENEMY = 0=>POKE_AVOID_ENEMY = 20" || exit 1
$V x12e --src v12 --set "$OURS" --set "$NOPACK" || exit 1
$V xC --src v12 || exit 1
$PY research/2026-10-19/patches/chase.py v12 xCchase || exit 1
for b in x12c x12d x12e; do
  $H boss_$b $b v10 --seeds 1,2,3,4 --maps contest,stampede
done
$H h2h_xC_x12e xC x12e --seeds 1,2 --maps ambush,contest,corners,eight,elkring,interlock,lanes,monolith,pilgrimage,rows,rushbait-v2,stampede,swirl
$H h2h_xCchase_xC xCchase xC --seeds 1,2
$PY tools/gauntlet.py v12 --vs v10 --seeds 1,2 --note "v12 final: v10 + shop 150/any HP + pro draft 4-5 + pro packs 150 + claim on kill; poke off" 2>&1 | grep -v "^created"
echo QUEUE14 DONE
