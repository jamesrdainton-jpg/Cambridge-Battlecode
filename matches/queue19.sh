#!/usr/bin/env bash
# Queue 19 (2026-10-20, cambc 2.2.5, 4-core Linux cloud machine): queue 18's zL (fast unopposed) LOSES to v12 head to
# head. Which layer costs contested games? Each layer vs v12 on the five maps zL lost 0/2 (swirl, packs, pilgrimage,
# monolith, rows), seeds 1,2, both sides (20 games each). Built from bots/mybot at commit 381e8c6 (DEBUG off).
#   zP1 = MELEE_REACH WAIT_FIX                                   (pure bug fixes)
#   zP2 = zP1 + RESET_RETARGET LIVE_DPS STUN_CAMPS               (small mechanics; stuns damage-free only)
#   zP3 = zP2 + AWAKE_RECENT AWAKE_NEAR WAIT_STRICT              (awake rule and strict squad wait)
#   zP4 = zP2 + MONOLITH_POKE AOE_POKE POKE_SMART                (sieges)
#   zP5 = zL without PAIR_KILL (in a swirl trace zL lost 4 of 5 champions in the first ~40 rounds)
# Reproduce: git checkout 381e8c6, then run this.
cd "$(dirname "$0")/.."
PY=.venv/bin/python
V="$PY tools/variant.py"
L="$PY tools/lab.py"
on() { for f in "$@"; do printf -- '--set\nbot.py:%s = False=>%s = True\n' "$f" "$f"; done; }
mk() { local name=$1; shift; local args; mapfile -t args < <(on "$@"); $V "$name" "${args[@]}" >/dev/null || exit 1; }
P1="MELEE_REACH WAIT_FIX"
P2="$P1 RESET_RETARGET LIVE_DPS STUN_CAMPS"
mk zP1 $P1
mk zP2 $P2
mk zP3 $P2 AWAKE_RECENT AWAKE_NEAR WAIT_STRICT
mk zP4 $P2 MONOLITH_POKE AOE_POKE POKE_SMART
mk zP5 MELEE_REACH WAIT_FIX AWAKE_RECENT WAIT_STRICT RESET_RETARGET PACK_WALK_ALL LIVE_DPS STUN_CAMPS STUN_DAMAGING MONOLITH_POKE AOE_POKE POKE_SMART AWAKE_NEAR
M=swirl,packs,pilgrimage,monolith,rows
for b in zP5 zP1 zP2 zP3 zP4; do $L h2h $b v12 --seeds 1,2 --maps $M --jobs 6; done
echo QUEUE19 DONE
