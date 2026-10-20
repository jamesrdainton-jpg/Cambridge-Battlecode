#!/usr/bin/env bash
# Queue 22 (2026-10-20, cambc 2.2.5, 4-core Linux cloud machine): more seeds for zT (queue 21: MELEE_REACH WAIT_FIX +
# stampede-only sieges) on the maps where it can play differently from v12: stampede (sieges), pilgrimage and
# monolith (the fixes); seeds 3-6, both sides (24 games). zT is rebuilt from bots/mybot at commit 495138b as in queue 21.
# Reproduce: git checkout 495138b, then run this.
cd "$(dirname "$0")/.."
PY=.venv/bin/python
V="$PY tools/variant.py"
L="$PY tools/lab.py"
on() { for f in "$@"; do printf -- '--set\nbot.py:%s = False=>%s = True\n' "$f" "$f"; done; }
G=(--set "bot.py:SIEGE_SHARE = 0.0=>SIEGE_SHARE = 0.9" --set "bot.py:SIEGE_COV = 0.0=>SIEGE_COV = 2.0")
mapfile -t T < <(on MELEE_REACH WAIT_FIX MONOLITH_POKE AOE_POKE POKE_SMART)
$V zT "${T[@]}" "${G[@]}" >/dev/null || exit 1
$L h2h zT v12 --seeds 3,4,5,6 --maps stampede,pilgrimage,monolith --jobs 6
echo QUEUE22 DONE
