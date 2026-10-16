#!/usr/bin/env bash
# Queue 5 (2026-10-16, cambc 2.2.2, 17-map pool; 2 seeds = 68 games): one-change variants of mybot vs v6.
# po1 = MONOLITH_POKE (poke too-strong groups from range 4 with abilities); ts1 = the stand-off breaker
# (STANDOFF_TURNS 12) gated on our tributed gems being flat for 150 rounds (TEAM_STALL_ROUNDS).
# Reproduce: check out the commit in each gauntlet.csv line, then run this.
cd "$(dirname "$0")/.."
PY=.venv/Scripts/python.exe
[ -x "$PY" ] || PY=.venv/bin/python
V="$PY tools/variant.py"
G="$PY tools/gauntlet.py"
$V po1 --set "bot.py:MONOLITH_POKE = False=>MONOLITH_POKE = True" || exit 1
$V ts1 --set "bot.py:STANDOFF_TURNS = 0=>STANDOFF_TURNS = 12" --set "bot.py:TEAM_STALL_ROUNDS = 0=>TEAM_STALL_ROUNDS = 150" || exit 1
$G po1 --vs v6 --seeds 1,2 --note "queue5 po1 monolith poke vs v6" 2>&1 | grep -v "^created"
$G ts1 --vs v6 --seeds 1,2 --note "queue5 ts1 stall-gated stand-off breaker vs v6" 2>&1 | grep -v "^created"
echo QUEUE5 DONE
