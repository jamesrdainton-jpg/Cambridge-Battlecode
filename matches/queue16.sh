#!/usr/bin/env bash
# Queue 16 (2026-10-20, cambc 2.2.5, 17 maps, 4-core Linux cloud machine): corrected packages after queue 15
# (AWAKE_RECENT dropped: a probe showed camps keep attacking a champion that stays in range after one hit). Built from
# bots/mybot at commit b0ad8ab with tools/variant.py (DEBUG off); tools/lab.py runs (replays in matches/lab/).
# BASE = MELEE_REACH WAIT_FIX RESET_RETARGET LIVE_DPS STUN_CAMPS PAIR_KILL FAST_WALK FAST_SCORE HP_AWARE, plus:
#   zG  PACK_NEED (packs sized by need)
#   zH  PACK_NEED + sieges (MONOLITH_POKE AOE_POKE POKE_SMART)
#   zI  PACK_WALK_ALL + sieges
#   zJ  sieges (packs as in v12)
# Then zH vs v12 head-to-head, seeds 1,2.
# Reproduce: git checkout b0ad8ab, then run this.
cd "$(dirname "$0")/.."
PY=.venv/bin/python
V="$PY tools/variant.py"
L="$PY tools/lab.py"
on() { for f in "$@"; do printf -- '--set\nbot.py:%s = False=>%s = True\n' "$f" "$f"; done; }
BASE="MELEE_REACH WAIT_FIX RESET_RETARGET LIVE_DPS STUN_CAMPS PAIR_KILL FAST_WALK FAST_SCORE HP_AWARE"
SIEGE="MONOLITH_POKE AOE_POKE POKE_SMART"
mk() { local name=$1; shift; local args; mapfile -t args < <(on "$@"); $V "$name" "${args[@]}" >/dev/null || exit 1; }
mk zG $BASE PACK_NEED
mk zH $BASE PACK_NEED $SIEGE
mk zI $BASE PACK_WALK_ALL $SIEGE
mk zJ $BASE $SIEGE
$L econ zG zH zI zJ --seeds 1,2 --jobs 6
$L h2h zH v12 --seeds 1,2 --jobs 6
echo QUEUE16 DONE
