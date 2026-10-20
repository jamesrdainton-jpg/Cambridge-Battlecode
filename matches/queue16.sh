#!/usr/bin/env bash
# Queue 16 (2026-10-20, cambc 2.2.5, 17 maps, 4-core Linux cloud machine): second round of packages, built from
# bots/mybot at commit 0cf623d with tools/variant.py (DEBUG off); tools/lab.py runs (replays in matches/lab/).
# Common to all: MELEE_REACH WAIT_FIX AWAKE_RECENT (non-strict wait: WAIT_STRICT off) RESET_RETARGET LIVE_DPS
# STUN_CAMPS PAIR_KILL FAST_WALK FAST_SCORE, plus:
#   zC    PACK_WALK_ALL
#   zCnp  (no pack change)
#   zD    PACK_WALK_ALL + sieges (MONOLITH_POKE AOE_POKE POKE_SMART)
#   zE    PACK_NEED
#   zF    PACK_NEED + sieges
# Reproduce: git checkout 0cf623d, then run this.
cd "$(dirname "$0")/.."
PY=.venv/bin/python
V="$PY tools/variant.py"
L="$PY tools/lab.py"
on() { for f in "$@"; do printf -- '--set\nbot.py:%s = False=>%s = True\n' "$f" "$f"; done; }
BASE="MELEE_REACH WAIT_FIX AWAKE_RECENT RESET_RETARGET LIVE_DPS STUN_CAMPS PAIR_KILL FAST_WALK FAST_SCORE"
SIEGE="MONOLITH_POKE AOE_POKE POKE_SMART"
mk() { local name=$1; shift; local args; mapfile -t args < <(on "$@"); $V "$name" "${args[@]}" >/dev/null || exit 1; }
mk zC $BASE PACK_WALK_ALL
mk zCnp $BASE
mk zD $BASE PACK_WALK_ALL $SIEGE
mk zE $BASE PACK_NEED
mk zF $BASE PACK_NEED $SIEGE
$L econ zC zCnp zD zE zF --seeds 1,2 --jobs 6
echo QUEUE16 DONE
