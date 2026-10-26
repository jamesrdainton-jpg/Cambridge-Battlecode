#!/usr/bin/env bash
# Queue 27 (2026-10-26, cambc 4.0.0): the 4- and 5-pick draft after patch 4.0 cut Vesper's strength 55 -> 45 and
# Marcella's growth (Varg's strength went 40 -> 45). Base = queue 26's z26g flags (BUILD_30 4 + FIGHT_PRIO + LOCKED_GOLD).
#   y27b = base (4 = Vendetta, Vesper, Tavi, Marcella; 5 = + Ryth)
#   y27v = Varg instead of Vesper          y27m = Varg instead of Marcella
# Seed 1 on the 58 maps with 4 or 5 picks (3-pick drafts are unchanged).
cd "$(dirname "$0")/.."
PY=.venv/Scripts/python.exe; [ -x "$PY" ] || PY=.venv/bin/python
V=tools/variant.py
B="bot.py:BUILD_30 = 0=>BUILD_30 = 4"; F="bot.py:FIGHT_PRIO = False=>FIGHT_PRIO = True"; G="bot.py:LOCKED_GOLD = False=>LOCKED_GOLD = True"
D4="draft.py:4: (CD.VENDETTA, CD.VESPER_VALE, CD.TAVI, CD.MARCELLA)"
D5="5: (CD.VENDETTA, CD.VESPER_VALE, CD.TAVI, CD.MARCELLA, CD.RYTH)"
$PY $V y27b --set "$B" --set "$F" --set "$G"
$PY $V y27v --set "$B" --set "$F" --set "$G" --set "$D4=>4: (CD.VENDETTA, CD.VARG, CD.TAVI, CD.MARCELLA)" \
    --set "draft.py:$D5=>5: (CD.VENDETTA, CD.VARG, CD.TAVI, CD.MARCELLA, CD.RYTH)"
$PY $V y27m --set "$B" --set "$F" --set "$G" --set "$D4=>4: (CD.VENDETTA, CD.VESPER_VALE, CD.TAVI, CD.VARG)" \
    --set "draft.py:$D5=>5: (CD.VENDETTA, CD.VESPER_VALE, CD.TAVI, CD.VARG, CD.RYTH)"
M45=00gemfight,00interlock,00oasis,00quarry,00reverse-spiral,00rows,00rushbait-v2,00swirl,00the-line,00vault,01hooks,01shortcut,02guardians,02stalactites,adgato-gemcombat2,adgato-gemcombat3,00ambush,00contest,00corners,00crater,00dunes,00eight,00elkring,00expanse,00galaxy,00gem-fields,00great-wall,00lanes,00lost-world,00monolith,00pilgrimage,00quadrants,00ribs,00road-of-riches,00split,00stampede,01big-world,01boss-battle,01concentrated-wealth,01corridors,01elk-arena,01fracture,01islands,01starfish,01starvation,01yellow-brick-road,02crossing,02cuts,02famine,02fields,02geodes,02gift-wrapping,02harvest,02tangle,02treasure-box,02uncharted-lands,adgato-gemcombat4,adgato-gemcombat5
N="queue 27; cambc 4.0.0, the 58 maps with 4-5 picks"
$PY tools/gauntlet.py y27v --vs y27b --seeds 1 --no-econ --maps $M45 --note "y27v (Varg for Vesper) vs y27b; $N"
$PY tools/gauntlet.py y27m --vs y27b --seeds 1 --no-econ --maps $M45 --note "y27m (Varg for Marcella) vs y27b; $N"
