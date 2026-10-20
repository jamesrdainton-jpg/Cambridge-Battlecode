#!/usr/bin/env bash
# Queue 20 (2026-10-20, cambc 2.2.5, 17 maps, 4-core Linux cloud machine): the v13 candidate after queue 19's layer
# ablation. Built from bots/mybot at commit 0c41bef (DEBUG off); tools/lab.py head-to-head vs v12, seeds 1,2, every map
# from both sides (68 games).
#   zR = MELEE_REACH WAIT_FIX FAST_WALK FAST_SCORE + sieges (MONOLITH_POKE AOE_POKE POKE_SMART) only on maps where 90%+
#        of the gems are in 200+ damage groups (SIEGE_SHARE 0.9: stampede and contest)
# Reproduce: git checkout 0c41bef, then run this.
cd "$(dirname "$0")/.."
PY=.venv/bin/python
V="$PY tools/variant.py"
L="$PY tools/lab.py"
on() { for f in "$@"; do printf -- '--set\nbot.py:%s = False=>%s = True\n' "$f" "$f"; done; }
mapfile -t ARGS < <(on MELEE_REACH WAIT_FIX FAST_WALK FAST_SCORE MONOLITH_POKE AOE_POKE POKE_SMART)
$V zR "${ARGS[@]}" --set "bot.py:SIEGE_SHARE = 0.0=>SIEGE_SHARE = 0.9" >/dev/null || exit 1
$L h2h zR v12 --seeds 1,2 --jobs 6
echo QUEUE20 DONE
