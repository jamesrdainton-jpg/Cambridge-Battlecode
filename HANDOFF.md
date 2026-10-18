# Handover — Cambridge Battlecode 2026 bot

State as of 2026-10-18. The full history of every experiment is in [DEVLOG.md](DEVLOG.md); rows 82–109 are the platform-data session of 2026-10-16. This note is the short version for picking the work back up.

**Team rule:** more than one person works on this repo, each on their own computer, so every result must be reproducible on a different computer from a git commit. Commit code before testing it, record the commit and the exact command, keep queue scripts and `matches\gauntlet.csv` in git, and use the pinned cambc with the committed maps. Details are in the "Team rule" section near the top of DEVLOG.md.

## Where everything is

- **Project folder:** on James's PC, `C:\Users\james\GitHub\Cambridge-Battlecode`. Teammates work in their own clones.
- **Git:** remote `origin` = `https://github.com/jamesrdainton-jpg/Cambridge-Battlecode.git`. Several people commit and push, so pull before starting. Experiment bots, caches, the venv, replays and `submissions/` stay out of git; results, queue scripts and logs in `matches/` are tracked. Keep the repo private during the competition.
- **Engine: cambc 2.2.2** (upgraded 2026-10-16; the platform runs a 2.2.x engine). **Teammates must upgrade:** `pip install -r requirements-dev.txt`, then run `tools\repro_check.py`. It must print `REPRODUCED` (34 reference games) before your numbers are comparable.
- **Maps:** `maps\` is the platform's current **17-map pool**: 8 maps are new (ambush, contest, eight, fragment, pilgrimage, rushbait-v2, stampede, swirl) and 6 were updated. Every result before DEVLOG row 82 was on the old engine and the old 9 maps.
- **Avast:** exclude `battlecode.co.uk` in Avast's Web Shield, or `cambc maps pull` / `login` / `submit` fail.

## The bot to submit

- **Upload ZIP:** `submissions\cambridge-bot-latest.zip` (on James's PC `C:\Users\james\GitHub\Cambridge-Battlecode\submissions\cambridge-bot-latest.zip`). It is the same file as `cambridge-bot-2026-10-18.zip`, content hash `8d32bd566f06`. It is **v7**, built from commit `8cc11b8` with DEBUG off, and verified 6/6 vs the starter on cambc 2.2.2. ZIPs aren't in git: on another computer, rebuild with `tools\release.py`, which gives the same hash from the same commit.
- **v7 = v6 + early gold:** `GOLD_WEIGHT` 0.4 (was 0.15), fading to 15% of that by round 500 (`GOLD_TAPER`, was 1200). It went 156/272 (57.4%), +10,048 gems vs v6 over seeds 1–8, with every seed set positive. It was adopted by the user's decision, 3 wins short of the pre-registered 159/272.
- **When the user asks for the latest bot:** run `.venv\Scripts\python.exe tools\release.py --verify` (leave out `--verify` while a batch runs) and give the ZIP's full path. The steps are in "Latest bot" at the top of DEVLOG.md.
- **Working copy:** `bots\mybot\src` (DEBUG on) = v7 plus switched-off flags (below). **Frozen versions:** `bots\v1`–`v7`; v7 is the baseline for tests. Freeze the next as `v8` with `tools\variant.py v8`.

### Flags in `mybot` that are off (each tested vs v6, not adopted)

| Flag | What it does | Result vs v6 (68 games unless noted) |
|---|---|---|
| `IGNORE_SPAWN_CAMPERS` | Ignore enemies standing in their own spawn unless we're hurt | 33/68, +196. Fixes **0 gems on rushbait-v2** against spawn-sitters (now wins by round 655) |
| `CAMP_TILE_FIX` | Melee approach avoids camp spawn tiles | 35/68, +1,080. Fixes a **1,700-turn step-on/step-off loop on contest** (contest vs idle: 400 gems → win at round 1,619) |
| `MONOLITH_POKE` | Poke too-strong groups from range 4 with abilities (line-of-sight ring) | 34/68, −1,250. Contest vs idle → win at round 1,851. Clashes with `CAMP_TILE_FIX` on contest |
| `STANDOFF_TURNS` + `TEAM_STALL_ROUNDS` | Stand-off breaker only after 150 rounds of flat team gems | 34/68, +1,086 |
| `WARDS` | Ward bush tiles near our target, as pros do | 71/136, **+9,816**: consistently more gems, not more wins |
| `POWER_FIRST` | Power emblem instead of Monster first | 35/68, −1,608 |
| `TELEMETRY` | Death and activity lines with DEBUG off (printing only) | not needed now that replays decode fully |

The first two are real bug fixes on single maps. A 68-game gauntlet can't see them (each moves the score by ~2 games, inside the ±4 noise). Adopting them as insurance is a judgement call that was not made this session.

## What the platform data shows (DEVLOG rows 82–104)

- **Our 15 games: 6 wins.** We fall behind on gems by round 200 in most losses. **79% of our deaths come from enemy champions**, not camps (fragment 17 in 2 games, interlock 10 in one), and every kill hands them our carried gems.
- **110 pro team-games**, decoded:
  - **Draft:** Cassi & Issac 94%, Stellar 92%, Ren 72%, Varg 70%, Tavi 51%, Ryth 47%. **Vendetta (our first pick) 7%, Marcella 2%.**
  - **Gold:** pros spend **2.4× our gold by round 150** (776 vs 321 per team) and buy their first items at round ~47 (us 71). Items are Power F/S 29% each, Bruiser and Durability H; almost no Monster.
  - **Vision:** 77% ward constantly, 71% of wards on bush tiles near camps and altars.
  - **Other:** almost no altar locks; they recall 5.5 times per 100 rounds and tribute every 24 rounds.
- **With our logic the pro draft loses** (v6 beat `bots/meta` 48/68; Cassi & Issac as 5th pick 31/68). Pros' Stellar/Cassi play is something our bot doesn't do. They probably poke camps from range 4 with focus builds, while our ranged champions stand at range 3, inside camp range.

## Settled by testing (don't redo without a new reason)

- **Spread out.** Pairs and whole-team squads lose.
- **Fight thresholds.** Retreat below 0.9, engage at 1.3 (old engine; real matches now suggest revisiting fights, see next steps).
- **Gold:** 0.4 fading by round 500 beats 0.15 (v7). Shopping at 150 gold at any health is neutral (sh1 33/68).
- **Draft (with our logic):** 3 picks Vendetta, Ryth, Tavi; Tavi 5th, Marcella 4th. The platform meta draft loses with our logic (48/68 for v6), and so does Cassi & Issac as 5th pick.
- **Squad sizing and items.** `NEED_FRAC` 0.55. Wait 40 turns for the squad (60 and 15 are worse). Jungle-first, Jungle-aware sizing, `GEM_HUNT` and Power-first are neutral or worse.

## How to run things (from the project folder)

```
.venv\Scripts\python.exe tools\gauntlet.py mybot --vs v7 --seeds 1,2   # 68 games + economy, ~6 min (17 maps)
.venv\Scripts\python.exe tools\arena.py mybot v7 --maps contest       # quick look at one map, both sides
.venv\Scripts\python.exe tools\variant.py NAME --set "bot.py:OLD=>NEW"  # A/B copy with a changed constant
.venv\Scripts\python.exe tools\release.py --verify                     # build + verify the upload ZIP
.venv\Scripts\python.exe tools\repro_check.py                          # does this PC reproduce the team's games?
.venv\Scripts\python.exe tools\platform_report.py                      # our platform downloads: result, gems, drafts, fuel
.venv\Scripts\python.exe tools\replay_decode.py FILE... [--buys]       # any replay: per-team tributes, deaths, buys, wards
```

On Mac/Linux use `.venv/bin/python` and `.venv/bin/cambc`. **Testing standard on 17 maps:** seeds 1,2 = 68 games; adopt at 40/68 with positive gems; confirm borderline results with seeds 3,4 then 5–8. Don't edit `bots\` while a queue runs (the commit column in `gauntlet.csv` turns `+dirty`), and push without `git pull --rebase` while a queue is writing `gauntlet.csv`. Platform downloads go in `replays\platform\` (not in git).

Nothing is queued or running.

## Paused 2026-10-18 ~16:30 (user short on usage; resume in ~2 hours)

Since the v7 release: upgraded to **cambc 2.2.5** (platform replays are now format 3; game play is identical to 2.2.2). Analysed v7's 25 platform games: **11/25 wins**, the early gold gap mostly closed, 3-pick maps 2/7, and 80% of our deaths are to champions in small fights (DEVLOG rows 110–119). New flags in `mybot`, all off and all neutral vs v7 so far:
- `CAST_FIRST`: ranged champions cast before their basic attack, fixing Tavi's skipped stun (30/68, +644).
- `ALLY_RANGE` / `LOW_HP_RETREAT` / `LOW_HP_REACH`: worse.
- The bug-fix package `IGNORE_SPAWN_CAMPERS` + `CAMP_TILE_FIX`: 32/68, +828, economy 12,118 vs v7's ~13,300–14,200. This is a candidate to include as insurance; it's the user's call.

**Resume plan:** relaunch three agents in git worktrees (briefs below), run their flags through 68-game gauntlets vs v7 one at a time, merge winners, freeze v8, release. Each agent runs tools with the main repo's venv (`export PATH="/c/Users/james/GitHub/Cambridge-Battlecode/.venv/Scripts:$PATH"`, python at `.venv/Scripts/python.exe`), keeps smoke tests to ≤16 games with `--jobs 3`, never runs `gauntlet.py`, puts every change behind an off-by-default flag, and commits on its own branch.
1. **Fights:** cut deaths to enemy champions (80% of deaths; 72% with an ally within 6 tiles; 49% to one attacker). Pros stack stuns (Cassi, Ren, Tavi, Prism) and Stellar burst; our Lanchester ratio ignores stuns. Varg's shield is cast 0.10 per basic attack vs pros' 0.18. Test vs `v7` and `meta`; measure deaths with `tools/replay_decode.py`.
2. **Pro composition:** make Cassi & Issac drafts beat v7, starting on 3-pick maps. Suspected blocker: squad sizing (`NEED_FRAC`) makes weak champions wait for partners even for one wolf, while pros farm with them solo.
3. **Economy:** measure where turns go (DEBUG `ACTS` lines vs `idle`) and cut the biggest waste; the target is rounds-to-1000 per map with no head-to-head loss.

## What to do next

1. **Fights against stun-heavy teams.** 79% of our platform deaths are to champions. Pros stack stuns (Cassi, Ren, Tavi, Prism) and Stellar burst; our fight ratio (HP × damage) ignores stuns. Likely gains: more caution against stun-heavy enemy drafts, and banking gems before contested areas. Testing against v7 alone won't show this, so first build an opponent that fights like the pros (focus up, stun then burst).
2. **Play ability champions properly.** Ranged champions with damaging abilities should stand at range 4 (camps hit at 3) and cast; build focus. That's what the pros' Power F builds suggest. Then re-test the pro draft (Cassi & Issac, Stellar, Ren), which brings an extra champion.
3. **Map-specific fixes** (`IGNORE_SPAWN_CAMPERS`, `CAMP_TILE_FIX`, `MONOLITH_POKE`): decide whether to adopt as insurance, or measure them on their own maps with many seeds.
4. **Wards** add +70 gems a game on average without extra wins. They may pay off against pros, where vision of bushes matters more than against v6.
5. **After submitting v7:** download our new platform games into `replays\platform\`, then run `tools\platform_report.py` and `tools\replay_decode.py` to see whether early gold closed the item gap.
