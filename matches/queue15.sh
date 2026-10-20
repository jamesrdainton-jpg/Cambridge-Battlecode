#!/usr/bin/env bash
# Queue 15 (2026-10-20, cambc 2.2.5, 17 maps, 4-core Linux cloud machine): flag packages on top of v12, built from
# bots/mybot at commit 2f4399b (= v12 + new flags, all off) with tools/variant.py (DEBUG off). Economy and
# head-to-heads use tools/lab.py (seeded copies of both bots, every map from both sides; replays in matches/lab/).
#   zb2  all new flags off (should play as v12 apart from fuel-timing noise)
#   zA   bug fixes and small mechanics: MELEE_REACH, WAIT_FIX, AWAKE_RECENT, RESET_RETARGET, PACK_WALK_ALL, LIVE_DPS,
#        STUN_CAMPS, PAIR_KILL
#   zB   zA + boss/strong-group sieges: MONOLITH_POKE, AOE_POKE, POKE_SMART
# Reproduce: git checkout 2f4399b, then run this.
cd "$(dirname "$0")/.."
PY=.venv/bin/python
V="$PY tools/variant.py"
L="$PY tools/lab.py"
on() { for f in "$@"; do printf -- '--set\nbot.py:%s = False=>%s = True\n' "$f" "$f"; done; }
A="MELEE_REACH WAIT_FIX AWAKE_RECENT RESET_RETARGET PACK_WALK_ALL LIVE_DPS STUN_CAMPS PAIR_KILL"
mapfile -t AARGS < <(on $A)
mapfile -t BARGS < <(on $A MONOLITH_POKE AOE_POKE POKE_SMART)
$V zb2 >/dev/null || exit 1
$V zA "${AARGS[@]}" >/dev/null || exit 1
$V zB "${BARGS[@]}" >/dev/null || exit 1
$L econ zA zB --seeds 1,2 --jobs 6
$L h2h zA v12 --seeds 1,2 --jobs 6
$L h2h zB v12 --seeds 1,2 --jobs 6
$L econ v12 zb2 --seeds 1,2 --maps ambush,monolith,stampede --jobs 6
echo QUEUE15 DONE
