# Handover — Cambridge Battlecode 2026 bot

State as of 2026-10-18 21:00 UTC (competition sprint; rows 120–132 of DEVLOG). The full history of every experiment is in [DEVLOG.md](DEVLOG.md); rows 82–109 are the platform-data session of 2026-10-16. This note is the short version for picking the work back up.

**Team rule:** more than one person works on this repo, each on their own computer, so every result must be reproducible on a different computer from a git commit. Commit code before testing it, record the commit and the exact command, keep queue scripts and `matches\gauntlet.csv` in git, and use the pinned cambc with the committed maps. Details are in the "Team rule" section near the top of DEVLOG.md.

## Where everything is

- **Project folder:** on James's PC, `C:\Users\james\GitHub\Cambridge-Battlecode`. Teammates work in their own clones.
- **Git:** remote `origin` = `https://github.com/jamesrdainton-jpg/Cambridge-Battlecode.git`. Several people commit and push, so pull before starting. Experiment bots, caches, the venv, replays and `submissions/` stay out of git; results, queue scripts and logs in `matches/` are tracked. Keep the repo private during the competition.
- **Engine: cambc 2.2.2** (upgraded 2026-10-16; the platform runs a 2.2.x engine). **Teammates must upgrade:** `pip install -r requirements-dev.txt`, then run `tools\repro_check.py`. It must print `REPRODUCED` (34 reference games) before your numbers are comparable.
- **Maps:** `maps\` is the platform's current **17-map pool**: 8 maps are new (ambush, contest, eight, fragment, pilgrimage, rushbait-v2, stampede, swirl) and 6 were updated. Every result before DEVLOG row 82 was on the old engine and the old 9 maps.
- **Avast:** exclude `battlecode.co.uk` in Avast's Web Shield, or `cambc maps pull` / `login` / `submit` fail.

## The bot to submit (competition, 2026-10-18 evening)

- **Upload ZIP: `submissions/cambridge-bot-latest.zip`**, which is **v10**: content hash `43c90c9220c2`, built from commit `36013cc` with DEBUG off, and verified 6/6 vs the starter on cambc 2.2.5 with no error lines. `submissions/` is normally ignored, but this one ZIP is **committed on branch `claude/adoring-fermat-jthwy1`**, so it can be downloaded from GitHub. It is the same file as `cambridge-bot-2026-10-18-2.zip`. Rebuild it anywhere with `tools/release.py --src v10` (or `--src mybot`, which now equals v10 apart from DEBUG); the content hash comes out the same.
- **v10 = v8 + `FIGHT_SHIELD` + `WARDS` + `CAST_FIRST`** (v8 = v7 + `IGNORE_SPAWN_CAMPERS` + `CAMP_TILE_FIX`).
  - **vs v8: 55/68, +13,016** (seeds 1,2) and 24/34, +6,020 (seed 3). It farms faster too: economy 11,623 vs ~12,100.
  - **vs `meta`** (the strong teams' draft): **33/34, +11,258** (seed 3; v11 went 31/34 on the same seed); the partial seed-1 run went 18 of 22.
  - Our champions died **283 times vs v8's 552** in the 68 games.
- **Why not v11** (v10 + `FIGHT_MEMO` 2):
  - Against v10 it is only 108/204 (seeds 1–6: 42, 32, 34 of 68) and +5,644 gems, which is not significant.
  - On seed 3 it did worse than v10 against the two other opponents: vs v8 19/34 against v10's 24/34. It beat `meta` 58/68 on seeds 1,2.
  - It is frozen in `bots/v11` for later testing.
- **When the user asks for the latest bot:** run `.venv\Scripts\python.exe tools\release.py --verify` (leave out `--verify` while a batch runs) and give the ZIP's full path. The steps are in "Latest bot" at the top of DEVLOG.md.
- **Working copy:** `bots/mybot/src` (DEBUG on) = v10 plus switched-off flags. **Frozen versions:** `bots/v1`–`v11`; v10 is the baseline for tests.
- **This machine runs one batch at a time.** Two `run-batch` processes at 18 jobs each run a 15 GB machine out of memory, and the killed games count as losses (DEVLOG 124). Always check `batch.log` for `FAILED` lines.

### Competition sprint results (DEVLOG rows 120–132)

| Flag | What it does | Result | Status |
|---|---|---|---|
| `FIGHT_SHIELD` | Varg casts its self-shield in fights (`support()` only ran while farming) | 40/68, +5,246 vs v8 | **in v10** |
| `WARDS` + `CAST_FIRST` | On top of the shield: wards on bushes near the target; ranged champions cast before the basic attack | 55/68, +13,016 vs v8 (with the shield) | **in v10** |
| `FIGHT_MEMO` 2 | Fight on the lowest strength ratio of the last 2 rounds (stops chase/flee flip-flops) | 108/204, +5,644 vs v10 (seeds 1–6) | off (v11) |
| `FIGHT_MEMO` 3 | Same, 3 rounds | 27/68, −3,538 vs v11 | off |
| `RECALL_SAFE` 4 | No recall within 4 rounds of an enemy within 10 tiles | 15 of 30 valid games vs v10 | off |
| `CC_FIRST` | Ryth and Tavi stun champions before the basic attack | 34/68, +1,564 vs v10 | off |
| `TRIBUTE_BIG/MID` 20/10 | Bank gems sooner | 35/68, +916 vs v10 | off (30/15) |
| `FIGHT_GEM_EXTRA` 0.5 | Gem carriers more cautious | 36/68, +118 vs v11 | off (0.25) |
| `FIGHT_ENGAGE` 1.1 | Chase sooner | 37/68, −1,074 vs v11 | off (1.3) |
| `ALLY_RANGE` 5 | Count fewer allies in the ratio | 26/68, −4,112 vs v11 | off (7) |
| `NEED_FRAC` 0.7 | Fewer champions per camp | 34/68, +190 vs v11; economy 11,304 (faster) | off (0.55) |
| `SHOP_GOLD` 200 | Shop sooner | 32/68, +782 vs v11 | off (300) |

Cloud sessions A–D ran some of these on their own machines; their `gauntlet.csv` rows are on branches `claude/sprint-a-fight-thresholds`, `claude/sprint-b-fight-memory`, `claude/sprint-c-confirm-v11` and `claude/sprint-d-economy`.

### Older flags in `mybot` (tested vs v6; `IGNORE_SPAWN_CAMPERS` and `CAMP_TILE_FIX` are now on, `WARDS` is on in v10)

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

## Paused 2026-10-18 ~16:30 (superseded by the evening sprint above; kept for the agent briefs)

Since the v7 release: upgraded to **cambc 2.2.5** (platform replays are now format 3; game play is identical to 2.2.2). Analysed v7's 25 platform games: **11/25 wins**, the early gold gap mostly closed, 3-pick maps 2/7, and 80% of our deaths are to champions in small fights (DEVLOG rows 110–119). New flags in `mybot`, all off and all neutral vs v7 so far:
- `CAST_FIRST`: ranged champions cast before their basic attack, fixing Tavi's skipped stun (30/68, +644).
- `ALLY_RANGE` / `LOW_HP_RETREAT` / `LOW_HP_REACH`: worse.
- The bug-fix package `IGNORE_SPAWN_CAMPERS` + `CAMP_TILE_FIX`: 32/68, +828, economy 12,118 vs v7's ~13,300–14,200. This is a candidate to include as insurance; it's the user's call.

**Resume plan:** relaunch three agents in git worktrees (briefs below), run their flags through 68-game gauntlets vs v7 one at a time, merge winners, freeze v8, release. Each agent runs tools with the main repo's venv (`export PATH="/c/Users/james/GitHub/Cambridge-Battlecode/.venv/Scripts:$PATH"`, python at `.venv/Scripts/python.exe`), keeps smoke tests to ≤16 games with `--jobs 3`, never runs `gauntlet.py`, puts every change behind an off-by-default flag, and commits on its own branch.
1. **Fights:** cut deaths to enemy champions (80% of deaths; 72% with an ally within 6 tiles; 49% to one attacker). Pros stack stuns (Cassi, Ren, Tavi, Prism) and Stellar burst; our Lanchester ratio ignores stuns. Varg's shield is cast 0.10 per basic attack vs pros' 0.18. Test vs `v7` and `meta`; measure deaths with `tools/replay_decode.py`.
2. **Pro composition:** make Cassi & Issac drafts beat v7, starting on 3-pick maps. Suspected blocker: squad sizing (`NEED_FRAC`) makes weak champions wait for partners even for one wolf, while pros farm with them solo.
3. **Economy:** measure where turns go (DEBUG `ACTS` lines vs `idle`) and cut the biggest waste; the target is rounds-to-1000 per map with no head-to-head loss.

## What to do next

0. **After the competition:** download the platform games and check deaths with `tools/replay_decode.py`. v10 halved our deaths against v8 locally (283 vs 552), so see whether that holds against real teams. The fight path still never calls `support()` for heals (we draft no healer), and FIGHT_MEMO 2 is a candidate that needs more seeds (it is neutral-to-positive head-to-head and worse vs v8 on seed 3).

1. **Fights against stun-heavy teams.** 79% of our platform deaths are to champions. Pros stack stuns (Cassi, Ren, Tavi, Prism) and Stellar burst; our fight ratio (HP × damage) ignores stuns. Likely gains: more caution against stun-heavy enemy drafts, and banking gems before contested areas. Testing against v7 alone won't show this, so first build an opponent that fights like the pros (focus up, stun then burst).
2. **Play ability champions properly.** Ranged champions with damaging abilities should stand at range 4 (camps hit at 3) and cast; build focus. That's what the pros' Power F builds suggest. Then re-test the pro draft (Cassi & Issac, Stellar, Ren), which brings an extra champion.
3. **Map-specific fixes** (`IGNORE_SPAWN_CAMPERS`, `CAMP_TILE_FIX`, `MONOLITH_POKE`): decide whether to adopt as insurance, or measure them on their own maps with many seeds.
4. **Wards** add +70 gems a game on average without extra wins. They may pay off against pros, where vision of bushes matters more than against v6.
5. **After submitting v7:** download our new platform games into `replays\platform\`, then run `tools\platform_report.py` and `tools\replay_decode.py` to see whether early gold closed the item gap.
