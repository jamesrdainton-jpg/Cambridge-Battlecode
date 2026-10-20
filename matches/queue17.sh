#!/usr/bin/env bash
# Queue 17 (2026-10-20, cambc 2.2.5, 4-core Linux cloud machine): which shared fix costs time on the small 3-pick maps
# (queue 16: zG packs 474 and fragment 612 vs v12 427 and 589)? Each zK_<FLAG> = queue 16's zG without that one flag;
# STUN_CAMPS now covers only damage-free stuns (none in the 3-pick draft), and zKdmg adds STUN_DAMAGING (the old
# STUN_CAMPS behaviour for Tavi's damaging stun).
# Built from bots/mybot at commit 585a26e with tools/variant.py (DEBUG off); tools/lab.py econ, seeds 1-3, packs+fragment.
# Reproduce: git checkout 585a26e, then run this.
cd "$(dirname "$0")/.."
PY=.venv/bin/python
V="$PY tools/variant.py"
L="$PY tools/lab.py"
on() { for f in "$@"; do printf -- '--set\nbot.py:%s = False=>%s = True\n' "$f" "$f"; done; }
G="MELEE_REACH WAIT_FIX RESET_RETARGET LIVE_DPS STUN_CAMPS PAIR_KILL FAST_WALK FAST_SCORE HP_AWARE PACK_NEED"
mk() { local name=$1; shift; local args; mapfile -t args < <(on "$@"); $V "$name" "${args[@]}" >/dev/null || exit 1; }
mk zKall $G
mk zKdmg $G STUN_DAMAGING
BOTS="v12 zKall zKdmg"
for drop in MELEE_REACH WAIT_FIX RESET_RETARGET LIVE_DPS FAST_WALK FAST_SCORE HP_AWARE; do
  keep=""
  for f in $G; do [ "$f" != "$drop" ] && keep="$keep $f"; done
  mk "zK_$drop" $keep
  BOTS="$BOTS zK_$drop"
done
$L econ $BOTS --seeds 1,2,3 --maps packs,fragment --jobs 6
echo QUEUE17 DONE
