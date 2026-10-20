#!/usr/bin/env bash
# Queue 21 (2026-10-20, cambc 2.2.5, 17 maps, 4-core Linux cloud machine): queue 20's zR lost contest again with
# sieges, so restrict them to clustered strong groups (SIEGE_COV 2.0: stampede only), with and without FAST_WALK /
# FAST_SCORE. Built from bots/mybot at commit b8cc0fc (DEBUG off); tools/lab.py head-to-head vs v12, seeds 1,2.
#   zS = MELEE_REACH WAIT_FIX FAST_WALK FAST_SCORE + sieges, SIEGE_SHARE 0.9, SIEGE_COV 2.0
#   zT = MELEE_REACH WAIT_FIX + sieges, SIEGE_SHARE 0.9, SIEGE_COV 2.0
# Reproduce: git checkout b8cc0fc, then run this.
cd "$(dirname "$0")/.."
PY=.venv/bin/python
V="$PY tools/variant.py"
L="$PY tools/lab.py"
on() { for f in "$@"; do printf -- '--set\nbot.py:%s = False=>%s = True\n' "$f" "$f"; done; }
G=(--set "bot.py:SIEGE_SHARE = 0.0=>SIEGE_SHARE = 0.9" --set "bot.py:SIEGE_COV = 0.0=>SIEGE_COV = 2.0")
mapfile -t S < <(on MELEE_REACH WAIT_FIX FAST_WALK FAST_SCORE MONOLITH_POKE AOE_POKE POKE_SMART)
mapfile -t T < <(on MELEE_REACH WAIT_FIX MONOLITH_POKE AOE_POKE POKE_SMART)
$V zS "${S[@]}" "${G[@]}" >/dev/null || exit 1
$V zT "${T[@]}" "${G[@]}" >/dev/null || exit 1
$L h2h zT v12 --seeds 1,2 --jobs 6
$L h2h zS v12 --seeds 1,2 --jobs 6
echo QUEUE21 DONE
