#!/usr/bin/env bash
# Queue 18 (2026-10-20, cambc 2.2.5, 17 maps, 4-core Linux cloud machine): from the best economy so far (queue 15's zB,
# 9,610) with the danger-zone hole fixed (AWAKE_NEAR), vary one thing at a time. Built from bots/mybot at commit d30816a
# with tools/variant.py (DEBUG off); tools/lab.py econ, seeds 1,2.
#   zL  = zB (MELEE_REACH WAIT_FIX AWAKE_RECENT WAIT_STRICT RESET_RETARGET PACK_WALK_ALL LIVE_DPS STUN_CAMPS
#         STUN_DAMAGING PAIR_KILL + MONOLITH_POKE AOE_POKE POKE_SMART) + AWAKE_NEAR
#   zM  = zL without WAIT_STRICT (v12's squad wait)
#   zN  = zL + FAST_WALK FAST_SCORE
#   zO  = zN + HP_AWARE
# Reproduce: git checkout d30816a, then run this.
cd "$(dirname "$0")/.."
PY=.venv/bin/python
V="$PY tools/variant.py"
L="$PY tools/lab.py"
on() { for f in "$@"; do printf -- '--set\nbot.py:%s = False=>%s = True\n' "$f" "$f"; done; }
mk() { local name=$1; shift; local args; mapfile -t args < <(on "$@"); $V "$name" "${args[@]}" >/dev/null || exit 1; }
L0="MELEE_REACH WAIT_FIX AWAKE_RECENT RESET_RETARGET PACK_WALK_ALL LIVE_DPS STUN_CAMPS STUN_DAMAGING PAIR_KILL MONOLITH_POKE AOE_POKE POKE_SMART AWAKE_NEAR"
mk zL $L0 WAIT_STRICT
mk zM $L0
mk zN $L0 WAIT_STRICT FAST_WALK FAST_SCORE
mk zO $L0 WAIT_STRICT FAST_WALK FAST_SCORE HP_AWARE
$L econ zL zM zN zO --seeds 1,2 --jobs 6
echo QUEUE18 DONE
