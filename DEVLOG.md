# Cambridge Battlecode 2026 — development log

Running record of everything tried on the bot: setup, discovered game mechanics, tools, every experiment and its result, and the decisions taken. Newest experiments are at the bottom of the experiment log.

## Latest bot

> **When the user asks for "the latest bot":**
> 1. Run `.venv\Scripts\python.exe tools\release.py --verify` from the project folder (on Mac/Linux, `.venv/bin/python tools/release.py --verify`). It rebuilds the upload ZIP from `bots/mybot` (DEBUG off), checks it, and plays 6 games against the starter. If a batch is running, leave out `--verify`, because extra games can make batch games fail. If `bots/mybot` has an experimental change turned on, release the last frozen version instead with `--src v5` (or newer). `submissions/` is not in git, so on a fresh clone this step creates the ZIP; the same commit always gives the same content hash.
> 2. Reply with the ZIP's full path on the computer you are on (the tool prints it; on James's PC it is `C:\Users\james\GitHub\Cambridge-Battlecode\submissions\cambridge-bot-latest.zip`) and the dated copy it matches. Say what changed since the previous release.
> 3. Update the table and the release history below, and add a row to the experiment log.
>
> `tools\release.py --check` reports whether the latest ZIP still matches `bots/mybot`, without building anything.

| | |
|---|---|
| **ZIP to upload** | `submissions\cambridge-bot-latest.zip` in the repo folder (on James's PC: `C:\Users\james\GitHub\Cambridge-Battlecode\submissions\cambridge-bot-latest.zip`) |
| Same file as | `submissions\cambridge-bot-2026-10-16.zip` (content hash `627283f38422`) |
| Bot | `bots/mybot` = frozen `v5`, DEBUG off. 16.5 KB: `src/main.py`, `src/bot.py`, `src/draft.py`, `src/world.py` |
| Verified | 2026-10-16: 6/6 wins vs the starter (packs, lanes, monolith), no error lines |
| New since the previous ZIP | Draft on 3-pick maps: Vendetta, Ryth, Tavi (experiment 54). Two experimental Jungle build flags were added, both off |

To upload, use the platform's submission page, or `.venv\Scripts\cambc.exe submit release`, which sends `bots/release`, the same code as the ZIP (needs `cambc login` and the Avast exception).

**Release history** (the ZIPs live in `submissions/`, which is not in git):

| Date | ZIP | Source | What it added | Verified |
|---|---|---|---|---|
| 2026-10-16 | `cambridge-bot-2026-10-16.zip` | `mybot` at commit `85be59a` (= `v5`) | 3-pick draft Vendetta, Ryth, Tavi | 6/6 vs starter |
| 2026-10-15 | `cambridge-bot-2026-10-15.zip` | `mybot` at commit `40fc0f3` | v4 + cluster targeting, passive altar locks, gold weight 0.15, tribute 30/15, recall travel, safer retreats and recalls | 6/6 vs starter (experiment 51) |

## Team rule: results must reproduce on any computer

More than one person works on this GitHub repo, each on their own computer. A result only counts if a teammate can check out the same commit, run the same command and get the same games. Games are deterministic (the same code, maps and engine version give identical games), so this works as long as everything that affects a game comes from git:

- **Code from a commit.** Run experiments on committed code and note the commit in the log row. A variant is defined by its base commit plus its `tools/variant.py` command, so record the command too.
- **Commands and results in git.** Queue scripts (`matches/*.sh`), their logs and the results table `matches/gauntlet.csv` are tracked. Scripts must run from any clone: no `C:/Users/...` paths, no waiting on temporary files.
- **Same environment.** `cambc` 2.1.6 (pinned in `requirements-dev.txt`), a Python 3.13 venv, and the committed maps in `maps/`. Pulling new maps changes every result, so commit them and log it.
- **Releases.** Frozen versions (`v1`–`v5`) are in git. Release ZIPs are not: anyone can rebuild one with `tools/release.py` from the same commit, and the content hash shows it is identical.
- **New computer.** Before comparing numbers, run `tools/repro_check.py` (about a minute, not during a batch). It must print `REPRODUCED`.
- **Sharing the log.** Pull before adding experiment rows, and renumber on merge if two people added the same number.

Gaps found on 2026-10-16:

| Gap | Fix | Status |
|---|---|---|
| `matches/` was entirely git-ignored, so results, queue scripts and logs never reached teammates | Track `matches/gauntlet.csv`, `matches/*.sh` and `matches/*.log`; replays and arena folders stay ignored | Done (`.gitignore`) |
| Queue and batch scripts hard-code `C:/Users/james/...`, `.venv/Scripts/python.exe` and Claude temp files | Run from the script's own folder and find the venv's Python on Windows or Mac/Linux | Done for `queue2.sh`, `queue3.sh` and every new queue. `batch*.sh` and `queue1.sh` stay as history: they ran variants of never-committed code, so they can't be re-run anyway |
| Tools look for `cambc` only at `.venv/Scripts/cambc.exe` (Windows layout) | Also try `.venv/bin/cambc` and `PATH` | Done: `tools/common.py`, used by `arena.py`, `stats.py` and `release.py` |
| `gauntlet.csv` lines don't say which code produced them | Add the commit, and a flag for uncommitted changes, to each line | Done: new last column `commit` (`+dirty` = uncommitted changes in `bots/` or `maps/`); older lines have none |
| Nobody has checked that another computer reproduces these games | `tools/repro_check.py`: replay a fixed set of games and compare them with reference results stored in git | Done: reference (`tools/repro_reference.txt`) written on James's PC at commit `d3f40a6`, and a re-run there matched all 18 games. Still needs running on a second computer |
| Experiments before the first commit (2026-10-15 17:18) ran on code that was never committed | Can't be reproduced exactly; treat them as history | — |

**Setting up on a new computer:**
1. Clone the repo.
2. Create a Python 3.13 venv in `.venv`: `py -3.13 -m venv .venv` on Windows, `python3.13 -m venv .venv` on Mac/Linux.
3. Install the tools: `.venv\Scripts\pip install -r requirements-dev.txt` (Mac/Linux: `.venv/bin/pip install -r requirements-dev.txt`).
4. Run `tools/repro_check.py` with the venv's Python. Only compare results from that computer once it prints `REPRODUCED`.

## Setup

- **Toolchain.** Official CLI `cambc` 2.1.6 from PyPI (`pip install cambc`). `cambc init` created `sdk/`, `bots/`, `cambc.toml`; `cambc new mybot --lang python` created the Python starter; `cambc maps pull` downloaded the 9 competition maps.
- **Avast.** Avast "Web/Mail Shield" HTTPS scanning re-signs TLS and cambc rejects it (`invalid peer certificate: UnknownIssuer`). Fixed by adding a battlecode.co.uk exception in Avast. `SSL_CERT_FILE` does not help (cambc bundles its own roots).
- **Python.** Bots run on an embedded WASI Python 3.13 with only the standard library plus the bot's own files. Local dev venv `.venv` uses Python 3.13 (installed with the Python install manager) and holds `cambc`, `pyright`, `ruff`, `pytest` (`requirements-dev.txt`). The venv is not relocatable: recreate it if the folder moves.
- **Location.** 2026-10-14: project moved from OneDrive to `C:\Users\james\GitHub\Cambridge-Battlecode` (OneDrive sync slowed batches and locked folders). Copy verified file-by-file, venv recreated, matches reproduced identical results.
- **Git.** Remote `origin` = `https://github.com/jamesrdainton-jpg/Cambridge-Battlecode.git` (keep it private during the competition). `.gitignore` tracks only `mybot`, `v1`–`v5`, `starter`, `idle`, `probe` under `bots/`; experiment variants, build caches, the venv, `matches/` and `replays/` stay local (a first commit is about 118 files, 1.7 MB).

## Testing tools (`tools/`)

| Tool | What it does |
|---|---|
| `arena.py A B [--maps m1,m2] [--one-side] [--logs]` | Plays A vs B on every map from both sides with `cambc run-batch` (builds once, 18 games in ~1 min). Prints winner, finishing round and gem totals (from the bot's `STAT` lines). Replay bundles go to `matches/arena/A-vs-B/`. |
| `stats.py A B` | Same pairings via `cambc run --statistics`: kills, deaths and gems lost per team. Slower (rebuilds each game). |
| `acts.py matches/arena/<run> [--round N]` | Sums the per-champion activity tallies (`ACTS` debug lines): time spent fighting camps, walking, waiting, capturing, tributing, recalling, dead. |
| `variant.py NAME [--src BOT] [--draft ...] [--set "bot.py:OLD=>NEW"]` | Clones a bot (default `bots/mybot`) into a variant with a changed draft order or constants (DEBUG off) for A/B tests. |
| `gauntlet.py BOT [--vs v4,starter] [--seeds 1,2,3,4] [--maps m1,m2] [--no-econ] [--note ...]` | Plays BOT against each opponent on all maps (or `--maps`) from both sides, plus the economy benchmark vs idle, and appends a summary line to `matches/gauntlet.csv`. With `--seeds`, plays seeded copies of BOT **and** of each opponent that has the SEED hook (see below), so both sides are perturbed alike. |
| `release.py [--src mybot] [--verify] [--check]` | Builds the upload ZIP: copies the bot into `bots/release` with DEBUG off (refuses unless `SEED = 0`), runs `cambc bundle`, and saves `submissions/cambridge-bot-YYYY-MM-DD.zip` (later different releases that day get `-2`, `-3`; an identical rebuild reuses the file) plus a copy as `submissions/cambridge-bot-latest.zip`. Checks that the ZIP holds exactly the bot's `.py` files, identical to the source apart from DEBUG, with `DEBUG = False`, `SEED = 0`, and that every file compiles. `--verify` plays 6 games vs the starter and fails unless all are won with no error lines. `--check` only reports whether the latest ZIP matches the source. Prints the ZIP's full path. |
| `repro_check.py [--write]` | Plays v5 vs v4 on every map from both sides (18 games, ~1 min) and compares every game with `tools/repro_reference.txt`. Prints `REPRODUCED` or the games that differ. `--write` replaces the reference (only after a deliberate change everyone makes, such as a cambc upgrade; commit it). |
| `common.py` | Shared helpers, not run directly: finds `cambc` (Windows or Mac/Linux venv, else `PATH`) and the git commit behind a run. |
| `download_replays.js` | Not Python: paste it into the browser console (F12) on a platform page with replay download buttons. It lists the buttons it found, asks for confirmation, then clicks one every 1.5 s. Skips nav/header links and web-visualiser links. |

**Noise.** Games are deterministic, but any small code change cascades into different games, so a single 18-game set moves by roughly ±2–3 wins and ±500 gems even when nothing meaningful changed. `bot.py` has a testing-only `SEED` constant: a non-zero value perturbs target scores by up to 2%, so seeded copies play different games. `gauntlet.py --seeds 1,2,3,4` uses this to get 72 games per opponent. Production keeps `SEED = 0`.

Reference bots: `starter` (official starter), `idle` (drafts then does nothing — pure economy benchmark), `probe` (dumps map layouts), frozen versions `v1`–`v5` (`v2`–`v5` have the SEED hook). `release` is the DEBUG-off copy that `tools/release.py` bundles; it is regenerated, not edited.

Bot stdout is only stored inside replay bundles (`.repl26a` is a zip with `team-a.stdout` / `team-b.stdout`); the tools read the logs from there. The replay viewer is never opened.

## Engine facts discovered by experiment

**Fuel (CPU budget).** Normal turn 2.5M fuel; first game turn 5M; first draft turn ~25M. Running out suspends the bot until next round.

| Operation | Approx. fuel |
|---|---|
| Python loop iteration / function call | 500–800 |
| Simple SDK getter (`position`, `health`, `cooldown`) | 1,000–3,000 |
| `me.state()` | ~5,000 |
| `cambc.champions(...)` | 35,000–55,000 |
| `vision.camps()` | ~14,000 |
| `DistanceField.compute` on 80×80 | ~45,000 |
| `bitboard.positions()` | ~600 per tile |
| `game_map.camp_groups()` | ~640,000 (cache once) |
| `vision.camp_groups()` | ~1,100,000 (never call per turn) |

**Camps.**
- Camps never regenerate health.
- Abilities (range 4) outrange camps (range 3): Stellar poked a wolf from range 4 for 50 rounds without taking a hit.
- Damage wakes the whole group; an awake group hits the nearest champion in range (both wolves of a pair hit the same champion for 40/round).
- Varg's splash hits the second wolf.
- Capture: stand on a spawn tile of the dead group for 5 rounds. Rewards go to allies standing there.
- An occupied spawn tile blocks the group from respawning (our first bot deadlocked itself this way).
- Tribute takes ceil(gems/10) turns.

**API quirks.**
- Bitboard linear buffers are bit-packed row-major (bit `y*w + x`).
- `DistanceField` uses king moves and returns 65535 for unreached tiles.
- `remaining_channel_time()` throws when not channelling.
- `move_towards()` refuses an occupied target tile.
- Ally handles follow draft order (team A first).
- Positions are absolute (not mirrored for team B).
- Runs are fully deterministic: the same bots on the same map give identical games.

**Maps (current pool).**

| Map | Size | Picks | Notes |
|---|---|---|---|
| collision | 41×41 | 3 | single wolves/gold clusters, elks, `eggg` corner groups (108 gems) |
| corners | 71×71 | 5 | 4 free `gg` groups (48 gems, no damage) around a central altar |
| elkring | 30×30 | 5 | every group is elk + gold cluster |
| expanse | 80×80 | 3 | `gg`, `ggge`/`eggg` groups, many altars |
| interlock | 40×40 | 4 | `ggg` (72 free gems), wolves, elks |
| lanes | 90×30 | 5 | long lanes, 18 altars, wolves/elks/single clusters |
| monolith | 50×50 | 5 | corner monolith groups worth 392 gems + 300 gold |
| packs | 31×31 | 3 | wolf pairs, `GGgg` free clusters, 6 altars |
| rows | 50×50 | 4 | `www` trios, central `MMgg` (two monoliths, 448 gems) |

Map dumps (ASCII) are in `matches/mapdumps/`.

## Bot architecture (`bots/mybot/src`)

- `main.py` — main loop, dispatches draft vs champion turns, catches and logs exceptions so a bug never skips `end_turn`.
- `draft.py` — fixed priority list (Vendetta, Varg, Ryth, Marcella, Tavi, …) with an optional per-team-size override (`BY_SIZE`); 3-pick maps take Vendetta, Ryth, Tavi.
- `world.py` — static map data cached once per champion (walk-blocking tiles, altars, spawn, camp groups) plus knowledge of each group (alive / reward waiting / respawning, last seen camp HP); lazily cached distance fields.
- `bot.py` — the champion brain, each turn: shop → fight/retreat → recall → tribute → farm.
  - **Farming.** Each champion scores every camp group by value (gems + tapering gold weight) divided by team champion-time (champions needed × (travel + kill time) + capture + tribute trip). Groups that need several champions (elks, wolf packs) get a required-champion count; champions claim targets in shared memory (one byte each, top bit = "I'm at the target and ready"), wait just outside camp range until enough allies are ready (25-turn timeout), poke with abilities meanwhile, and step off spawn tiles after capturing.
  - **Safety.** A per-turn danger map of awake damaging camps; movement steers around other groups' danger zones; hurt champions escape out of range and only then recall. Ranged champions hold at exactly distance 3 so melee allies tank.
  - **Combat.** Lanchester-style ratio (our total HP × total DPS vs theirs, with home/away modifiers); retreat below 0.9 (1.1 when carrying 20+ gems), engage at 1.3 (1.6 with gems), always finish an enemy killable this turn, target choice favours low HP, carried gems and in-range targets. **Stand-off breaker:** after 12 turns near enemies with nobody hurt, keep away from them for 40 rounds (experiment 73).
  - **Shopping.** Monster strength (or focus) emblem → Power → Jungle health → more Power → Durability health.
  - **Clusters.** Varg's splash attacks hit the camp with the most live neighbours; area abilities aim at the most crowded camp tile; target scoring credits splash/AoE damage per group's cluster factor.
  - **Altar locks.** Buy one on every spawn visit, drop it on unlocked altars within 2 tiles (detour up to 8), break enemy locks that block our tribute.
  - **Tunable constants** at the top of `bot.py` (`MIN_SQUAD`, `RETARGET_EVERY`, `TRIBUTE_BIG/MID`, `CAUTION_WINDOW`, `ALTAR_LOCKS`, `LOCK_DETOUR`, `SHOP_*`, `SEED`, `DEBUG`) make A/B variants a one-line change via `tools/variant.py --set`.

## Experiment log

| # | Change | Result | Decision |
|---|---|---|---|
| 0 | Starter vs starter on all maps | Finishes rounds 485–1788 | Baseline |
| 1 | First real bot (target scoring, safety filter) | 15/18 vs starter; rows stuck (champions blocked their own camp's respawn), elkring idle (every camp rejected as unsafe solo) | Fix both |
| 2 | Required-champion counts + shared-memory claims + leave spawn tiles | 14/18; corners lost (whole team ground elks at the edge while the starter took free central gems) | Fix scoring |
| 3 | Score by team champion-time; lower gold weight; low-HP rotation out of camp range | 16/18; two deadlocks (champions waiting out of sight of each other) | Fix waiting |
| 4 | "Ready" bit in shared memory, 25-turn wait timeout, dead/recalling champions drop claims | **18/18 vs starter** (finishes rounds 338–676) | Frozen as **v1** |
| 5 | Economy benchmark vs idle (rounds to 1,000 gems, sum over 9 maps) | 4,610 | Benchmark |
| 6 | Activity tally | Camp fights 35%, walking 29%, altar trips 11%, waiting 7%; champions dying to camps (2+ deaths per game) | Fix deaths |
| 7 | Danger map, escape-then-recall, ranged hold at distance 3 | Camp deaths ~0; economy 4,595; **14/18 vs v1** | Frozen as **v2** |
| 8 | Lanchester combat model with ability-based DPS estimates | 11/18 vs v2, gem total even | Inspect fights |
| 9 | Draft experiments vs v2 (economy in rounds) | See table below | Adopt d4 |
| 10 | Stricter fight thresholds, gem-carrier caution, always finish killable enemies | **12/18 vs v2, +1,578 gem margin**; fewer gems lost | Frozen as **v3** |
| 11 | Shopping thresholds (see table) | No variant beat the current rule | Keep current |
| 12 | Determinism check | Identical results on reruns; small code changes cause single-map cascades (e.g. DEBUG logging changed lanes 542 → 615) | Judge on totals, not single maps |
| 13 | Gauntlet baseline: current bot (= v3 with DEBUG on) vs v3, v2, starter + economy | **40/54** (v3 10/18 +468, v2 12/18 +1,490, starter 18/18), economy 4,344 | Reference point |
| 14 | Fuel profiling (per-turn high-water mark, phase timings) | On lanes some turns used ~2.49M of 2.5M: re-scoring targets cost ~1.6M (42 groups × ~38k) and could run twice in one turn | Optimise |
| 15 | Fuel optimisations (see "Fuel work" below) | Worst turn ~2.05M; but gauntlet **34/54** (v3 7/18 −1,149, v2 9/18 +1,289), economy 4,419 | Suspect a behaviour change |
| 16 | Re-target variants: f1 every 8 turns, may switch mid-fight (= original rule); f2 every 8, holds target while fighting; f3 every 10, may switch | f1 32/54 (econ 4,414); f2 35/54 (4,425); f3 33/54 (4,542) — none recovers the baseline | Re-target rule is not the cause |
| 17 | Verified camps never move (logged any camp whose position differed from its spawn tile, 18 games) | 0 mismatches | Using static camp positions is safe |
| 18 | Seeded noise check, v3 vs v3 | **Invalid**: the seeded v3 copies lacked the `SEED` definition (v3 predates the constants block) and crashed every turn (0/72) | Redo properly |
| 19 | Current bot with seeds 1–4 vs unseeded v3 (72 games) | 25/72, −2,590 gems | Looked like a regression, but only one side was perturbed (see 21) |
| 20 | Proper noise check: v3 vs v2 with both sides seeded (SEED hook added to frozen v2/v3; no effect at SEED = 0) | Per 18 games: 10, 10, 9, 13 wins; margins −236 to +1,510. Total **42/72, +2,114** | One 18-game set swings ±2 wins / ±800 gems; use 72 seeded games for decisions |
| 21 | Fair test: fuel-optimised bot vs v3, both seeded | **33/72, +1,074** (7, 7, 10, 9 wins per seed) | Equal strength within noise; the refactor is safe and keeps worst-case fuel at ~2.05M. Keep it. Experiment 19's deficit came from perturbing only one side. |

| 22 | Froze the fuel-optimised bot as **v4** (new primary opponent). Squad test: `MIN_SQUAD = 2` (every camp gets at least two champions) vs v4, seeded | **22/72, −8,806**; economy 5,154 (vs ~4,400) | Pairs lose: the economy cost outweighs fight gains. Keep spreading out |
| 23 | Squad test: `MIN_SQUAD = 99` (whole team on every camp) vs v4, seeded | **13/72, −15,622**; economy 5,874 | Even worse. Spreading out is clearly right; `MIN_SQUAD` stays 1 |
| 24 | Cluster-aware damage (variant `cl`): Varg's splash attacks hit the camp with the most live neighbours; area abilities aim at the most crowded camp tile; target scoring credits splash/AoE damage per group's cluster factor; camp data reused from the knowledge pass instead of re-queried | **38/72, +2,398** vs v4 (10, 10, 7, 11 per seed); economy 4,398 | Mildly positive — kept |
| 25 | Code review fixes: attack an in-range camp/enemy when the chosen one is out of reach; recall no longer requires a free spell slot | Not measured on its own (included in 26) | Kept |
| 26 | Altar locks: buy a lock (10 gold) on every spawn visit, drop it on any unlocked altar within 2 tiles, detour up to 8 tiles to place it; break enemy locks with basic attacks when they block our tribute | Quick test vs starter: 6/6 wins; 1–5 locks placed per game; on collision the starter tributed only 44 gems by round 575 (it skips locked altars) | Being measured fairly in batch 2 (`lk1` vs `lk0`) |
| 27 | **Bug found in v1–v4:** an enemy lock on the altar a champion stands next to made it skip that altar and then sit there forever (its "walk to an altar" step was already satisfied) | Current bot breaks the lock instead | Fixed in the current bot. Means v1–v4 are trivially exploitable by locks, so lock tests must use a lock-aware opponent (`lk0`) |
| 28 | Batch 1 tribute/caution variants on the `cl` code (`cw40` caution window 40, `tbig` 80/40, `tsmall` 45/20) | `cw40` and `tbig` interrupted by the pause. **`tsmall`: 47/72, +5,312 vs v4** (economy 4,423), against 38/72, +2,398 for the identical code with 60/30 (`cl`) | Tributing earlier wins ~9 more games per 72. Confirming on the current bot in batch 5 (`t45` 45/20, `t30` 30/15 vs `base5` at 60/30) |
| 29 | Queued: batch 2 (`lk1` locks vs `lk0` no locks, each also vs v4), batch 3 (3-pick drafts `dA`–`dE` vs `lk1`, 8 seeds, packs/collision/expanse), batch 4 (one-constant sweeps vs `base5`: fight thresholds `fA` 0.8/1.2 and `fB` 1.0/1.5, gold weight `gw1` 0.15 and `gw2` 0.5, enemy-side penalty off `es1`) | Pending | — |
| 30 | First-turn setup fuel (new INITPROF debug line) | Lanes: setup overflowed the 4.6M first-turn budget (building camp-group objects alone cost 2.85M, ~68k per group), so every champion lost its first turn; corners used 4.60M of 4.62M | Rewrote group construction to read SDK object attributes directly with plain loops, and made champion damage profiles lazy: lanes setup 2.9M, corners 2.8M (Group objects 2.85M → 1.22M). Same data, so no behaviour change |
| 31 | Batch 2, part 1: `lk0` (cluster targeting + in-range fixes, no locks, tribute 60/30) vs v4 | **37/72, +4,026**; economy 4,300 | Same level as `cl` (38/72); in-range fixes neutral to slightly positive |
| 32 | Death analysis (DEBUG histories of the last 6 turns before each death, 6 games vs v4) | 26 deaths. Main fixable pattern: champions in "fight" mode retreating from enemies 7–9 tiles away while an awake camp hit them every turn (retreat ignored camp zones and fight mode pre-empted the camp escape). Also: recalls started at low HP interrupted by approaching enemies; a few champions stuck in place for several turns | Retreat now escapes camp range first, avoids camp zones, and recalls when blocked in but safe: 23 deaths in the same test |
| 33 | Lesson: running ad-hoc games while a batch runs can exceed cambc's 2-minute build limit ("Python preparation exceeded its two-minute runtime limit") and the games silently go missing | Batch logs checked: no batch game was affected | Don't run extra games during batches |
| 34 | Batch 2, part 2: `lk1` (altar locks: buy each spawn visit, place within 2 tiles, detour up to 8) vs `lk0` (no locks, breaks enemy locks) and vs v4 | **vs lk0: 27/72, −3,004** (7, 7, 7, 6 per seed). vs v4: 61/72, +29,238 (v4 gets stuck at locked altars). Economy 4,562 vs 4,300 for lk0 | Locks as built lose to a lock-aware bot: the detours and spawn trips cost ~6% economy and a lock only costs the enemy 3 hits. They crush lock-unaware bots. Testing passive placement only (`lk2`, no detour) in batch 6 |
| 35 | Safer recalls: retreating champions recall only when the nearest enemy is 8+ tiles away (was 6); the low-health recall walks home instead while an enemy is within 10 tiles. Endgame: from round 1940 champions tribute whatever they carry (the round limit is decided on tributed gems) | Not measured separately (in `rt0`/`rt1`) | — |
| 36 | Recall as fast travel (`RECALL_TRAVEL`): target scoring treats "recall, then walk from spawn" as a route when it beats walking by 3+ tiles; champions carrying no gems recall to reach such a target, and champions heading to tribute recall when spawn is much closer to an altar | Queued as batch 7 (`rt1` vs `rt0`) | — |
| 37 | Batch 3: 3-pick drafts vs `lk1` (Vendetta, Varg, Ryth), 8 seeds × packs/collision/expanse (48 games each) | `dA` Vendetta/Varg/Marcella 20/48 (−3,106); `dB` Vendetta/Varg/Tavi 18/48 (−4,276); `dC` Varg/Ryth/Marcella 15/48 (−1,818); `dD` Cassi&Issac/Vendetta/Varg 22/48 (−2,984); **`dE` Vendetta/Ryth/Tavi 30/48 (−20)** | Current draft beats every alternative except `dE`, which is level on gems; re-testing `dE` with 8 fresh seeds |
| 38 | Batch 4: `fA` (fight retreat < 0.8, engage ≥ 1.2) vs `base5` (0.9/1.3) | 34/72, −430; economy 4,562 | Neutral — thresholds are not sensitive in this range |
| 39 | Laptop sleep 13:27–16:13 paused the queue mid-batch | All batch logs report "0 failed": no games lost | Results unaffected; queue resumed automatically |
| 40 | Batch 4: `fB` (fight retreat < 1.0, engage ≥ 1.5) vs `base5` | **26/72, −4,586** | Cautious fighting loses; with `fA` neutral, 0.9/1.3 stays |
| 41 | Batch 4: `gw1` (gold weight 0.15 instead of 0.3) vs `base5` | **45/72, +8,360**; economy 4,406 (vs ~4,562) | Strong win: prioritise gems over gold. Adopted in `mybot`; batch 10 tests 0 and 0.075 |
| 42 | Batch 4: `gw2` (gold weight 0.5) vs `base5` | **25/72, −9,154**; economy 4,953 | Confirms the trend: less weight on gold is better (0.5 < 0.3 < 0.15) |
| 43 | Batch 4: `es1` (no enemy-side penalty: 1.0 instead of 0.85) vs `base5` | 37/72, +956; economy 4,560 | Neutral (within noise); keep 0.85 |
| 44 | Batch 5: tribute thresholds on the current code vs `base5` (60/30) | `t45` (45/20): 32/72, −684, economy 4,535. `t30` (30/15): 36/72, +2,526, economy 4,553 | Roughly neutral here (batch 1 showed +9 wins vs v4 for 45/20). No economy cost and fewer gems at risk against gem-stealing opponents, so `mybot` now uses 30/15 |
| 45 | Batch 6: `lk2` (locks placed only when passing an altar, no detours) vs `lk0` (no locks, lock-aware) and vs starter | **vs lk0: 42/72, +1,312** (11, 9, 12, 10 per seed); **vs starter: 72/72, +49,756**; economy 4,387 (lk0 4,300, lk1 4,562) | Passive locks are a net win even against a lock-aware bot and crush naive ones. Kept: `ALTAR_LOCKS = True`, `LOCK_DETOUR = 0` |
| 46 | Batch 7: `rt1` (recall as fast travel) vs `rt0` (same code, off) | **46/72, +3,920** (10, 9, 14, 13 per seed); economy 4,324 vs 4,403 without it; `rt0` also beat the starter 72/72 | Clear win. Kept in `mybot` |
| 47 | Packaged the current `mybot` (DEBUG off) as `submissions/cambridge-bot-2026-10-15.zip` with `cambc bundle` (copy in `bots/release`) | 16.5 KB: `src/main.py`, `bot.py`, `world.py`, `draft.py` | Ready to upload; verification game pending (batches running) |
| 48 | Batch 8 (5th pick on 5-pick maps, 4 seeds × corners/elkring/lanes/monolith vs `base8` = Tavi 5th): `p5S` Stellar 5th | **13/32, −3,212** | Tavi stays 5th over Stellar |
| 49 | Batch 8: `p5V` Vesper 5th | Invalid: only 8 of 32 games recorded (2/8, −698) | Re-run |
| 50 | Paused for the night (user sleeping the PC). Stopped mid-batch-8 | Not yet run: `p5C`, `p5W`, `p4T`, `p4S`, `p4C` (batch 8), `dE` re-test (batch 9), gold weight 0 / 0.075 (batch 10), verification game for the release ZIP | Re-queue on resume (see HANDOFF.md) |
| 51 | Resumed on the evening of 2026-10-15 (19:00; file and CSV timestamps). Verification of the release copy (`bots/release`, same source as the upload ZIP) vs starter on packs/lanes/monolith | 6/6 wins, no errors | Upload ZIP verified. Re-queued the unfinished tests (`matches/queue1.sh`) |
| 52 | Batch 8 complete. 5th pick vs Tavi (32 games each on corners/elkring/lanes/monolith): Stellar 13/32 (−3,212), Vesper 11/32 (−2,438), Cassi & Issac 14/32 (−1,062), Willow 13/32 (−1,920) | All alternatives lose | Tavi stays 5th |
| 53 | Batch 8: 4th pick vs Marcella (24 games each on interlock/rows): Tavi 9/24 (−1,340), Stellar 10/24 (−1,432), **Cassi & Issac 13/24 (+1,046)** | Marcella beats Tavi/Stellar; Cassi & Issac slightly ahead but within noise | Re-test Cassi & Issac with more seeds before switching |
| 54 | Batch 9: `dE` (Vendetta, Ryth, Tavi on 3-pick maps) re-test with seeds 9–16 vs `lk1` | 28/48 (−318). Combined with batch 3: **58/96 wins (60%)**, gems level (−338) | Wins more of the close games (~2 SD above even). Adopted: `draft.py` `BY_SIZE = {3: (Vendetta, Ryth, Tavi)}` |
| 55 | Batch 10: `gw0` (gold weight 0) vs `gw1` (0.15) | 35/72, +1,784; economy 4,514 (gw1: 4,406) | No gain and slower farming; gold still matters a little. Keep 0.15 unless 0.075 wins |
| 56 | Batch 10: `gw075` (gold weight 0.075) vs `gw1` (0.15). Finished at 09:10 on 2026-10-16, after the PC woke (the rest of queue 1 ran 19:03–19:31 on 2026-10-15) | 37/72, −90; economy 4,470 (gw1: 4,406) | Neutral and slightly slower farming. With `gw0` also neutral, `GOLD_WEIGHT` stays 0.15. Queue 1 complete |
| 57 | Checked the previous session's last, untested edit to `mybot`: the flags `TANK_JUNGLE_FIRST` (tanks buy the Jungle health emblem first) and `JUNGLE_AWARE` (squad sizing counts the emblem's 30% camp-damage cut), both off. The emblem bookkeeping runs even with the flags off | The `ItemType.JUNGLE_EMBLEM_*` names exist in the SDK, and `item_count()` is indexed the same way the shop code already uses | Safe to ship with the flags off |
| 58 | Froze the current `mybot` as **v5**: v4 plus every change adopted through experiment 54 (cluster targeting, passive locks, gold weight 0.15, tribute 30/15, recall travel, safer retreats, 3-pick draft). Added `!bots/v5/` to `.gitignore`. New `tools/release.py` builds the upload ZIP in one step (see Testing tools) | Release `submissions/cambridge-bot-2026-10-16.zip` (also saved as `cambridge-bot-latest.zip`, hash `627283f38422`): **6/6 vs starter** on packs, lanes and monolith, no error lines | v5 is the new baseline that variants are judged against. See "Latest bot" at the top |
| 59 | Queue 2 started (`matches/queue2.sh`, log in `matches/queue2.log`; base code `bots/mybot` at commit `85be59a`, unchanged through `d3f40a6`), each test 72 seeded games plus economy unless noted: `v5` vs `v4` (cumulative gain); `tj1` (`TANK_JUNGLE_FIRST`); `ja1` (`JUNGLE_AWARE`); `nf45` / `nf65` (`NEED_FRAC` 0.45 / 0.65, default 0.55); `wl15` / `wl40` (`WAIT_LIMIT` 15 / 40, default 25); `gh2` (`GEM_HUNT` 0.2); `p4C2` (Cassi & Issac as 4th pick, seeds 7–18 on interlock and rows, 48 games) | Results in the rows below | — |
| 60 | Queue 2: `v5` vs `v4`, both seeded | **66/72, +29,354** (16, 16, 17, 17 per seed); economy 4,324 (v4: 4,419 in experiment 15) | The cumulative gain since v4 is confirmed. Part of it comes from v4's altar-lock bug (experiment 27: v4 stalls at altars we lock), so the margin overstates the gain against bots without that bug |
| 61 | Queue 2: `tj1` (Ryth, Varg and Marcella buy the Jungle health emblem first) vs v5 | **26/72, −1,344**; economy 4,289 | Loses. Delaying the Monster and Power emblems weakens fights more than the 30% camp-damage cut helps. `TANK_JUNGLE_FIRST` stays off |
| 62 | Queue 2: `ja1` (squad sizing counts the Jungle emblem's 30% camp-damage cut) vs v5 | 34/72, +90; economy 4,357 | Neutral. `JUNGLE_AWARE` stays off, and the planned `tj1` + `ja1` combination is dropped |
| 63 | Platform replays: looked for a way to bulk-download match replays. The `cambc` CLI has no match or replay command (its only platform endpoints are sign-in, map pool, submissions and distribution on `https://2026a.battlecode.co.uk`), and the website's app code is served only to signed-in browsers. A local replay embeds its map file byte for byte but not the bot or team names | Wrote `tools/download_replays.js`, a browser-console script that clicks every replay download button on a platform page | **Optional**: the user may not bother, and nothing depends on it. If used, replays go in `replays/platform/` (not in git); a replay's map can be identified by matching against `maps/`, and the opponent has to come from the file or folder name |
| 64 | Queue 2: `nf45` (`NEED_FRAC` 0.45: more champions per camp) vs v5 | 29/72, −1,474; economy 4,374 | Worse |
| 65 | Queue 2: `nf65` (`NEED_FRAC` 0.65: fewer champions per camp) vs v5 | 32/72, −2,152; economy 4,277 (faster farming vs idle) | Worse head-to-head despite faster farming. 0.55 sits at the peak; `NEED_FRAC` stays 0.55 |
| 66 | Recorded the team rule (user request): results must reproduce on a different computer, because more than one person works on the repo. Audited the setup against it | Gaps and fixes listed in "Team rule" near the top. Done now: `matches/` results, queue scripts and logs tracked in git; `release.py` finds `cambc` on Windows or Mac/Linux and reports the commit it built from | Remaining fixes after queue 2 |
| 67 | Queue 2: `wl15` (`WAIT_LIMIT` 15: attack sooner without the full squad) vs v5 | **31/72, −3,716** (7, 6, 10, 8 per seed); economy 4,326 | Worse: waiting less for the squad loses |
| 68 | Queue 2: `wl40` (`WAIT_LIMIT` 40) vs v5 | 40/72, +156 (11, 8, 11, 10 per seed); economy 4,343 | Slightly ahead but within noise (about one standard deviation). With 15 clearly worse, longer waits may help: confirm with seeds 5–8 and also try 60 |
| 69 | Queue 2: `gh2` (`GEM_HUNT` 0.2: engage more readily against enemies carrying 40+ gems) vs v5 | 37/72, +930; economy 4,324 | Neutral; `GEM_HUNT` stays 0 |
| 70 | Queue 2: `p4C2` (Cassi & Issac as 4th pick) vs v5, seeds 7–18 on interlock and rows | **16/48, −2,000**. With batch 8's 13/24: 29/72 | Loses; batch 8's 13/24 was noise. Marcella stays 4th. Queue 2 complete: nothing beat v5 clearly, so the ZIP is unchanged |
| 71 | Reproducibility fixes from the Team rule list (no games running): `tools/common.py` (find `cambc` on any OS, commit lookup) used by `arena.py`, `stats.py`, `release.py`; `gauntlet.py` writes a `commit` column; portable `queue2.sh`; new `tools/repro_check.py` | Reference written at commit `d3f40a6`, and an immediate re-run on this PC matched all 18 games (`REPRODUCED`) | The tooling now works from any clone. A teammate's computer still needs a first check |
| 72 | **Stall bug found** (while writing the repro reference): on interlock, v5 reached 992 gems by round 650 and then scored nothing until the round-2000 limit. Scanned every saved replay for teams whose tributed gems stayed flat for 300+ rounds | v5 vs v4 (queue 2): 7 of 72 games had our gems flat for 1,300–1,700 rounds (collision, interlock, monolith). In 552 games against v5-based bots: 2 short stalls (300–325 rounds, corners). Debug logs (`mybot` vs `v4`, same game): a **stand-off livelock**. All champions sat 5–8 tiles from v4's champions, which are parked at altars by v4's lock bug. Each turn the fight ratio swung between 0.6 and 2.2: below 0.9 a champion stepped back, in the hold band it walked back towards its target, in an exact 2-turn cycle. Nobody farmed or tributed, and Marcella carried 44 gems for 1,350 rounds | Fix it: real opponents that guard an altar or chokepoint, or just idle near our path, could cause the same stall |
| 73 | Stand-off breaker (`STANDOFF_TURNS = 12`, `AVOID_ROUNDS = 40`). With enemies within 9 tiles and nobody on either side losing health for 12 turns, a champion marks a zone around them (their attack range + 3). For 40 rounds it ignores them unless they close in (≤ 2 moves from hitting it) or hurt it, skips camp groups in the zone, and steers farm and tribute moves around it. First version: on collision, our champions froze for 1,600 rounds. Their only reachable altar was guarded, the other altar (39,20) can't be reached from there, and tribute refused the guarded one. Fixed: use an unguarded altar only if one can be reached | Same 6 games vs v4 (interlock, collision, monolith, both sides): all won, finishing at rounds 751, 825, 895, 1,334, 611 and 567 (v5: 2,000, 753, 1,020, 986, 581, 593). `STANDOFF_TURNS = 0` reproduces v5's 6 games exactly. Pyright clean | In `mybot` (on). Being measured in queue 3 |
| 74 | Queue 3 started at 11:19 (`matches/queue3.sh`, log `matches/queue3.log`): `so1` (stand-off breaker) vs v5 and v4; `wl40` with fresh seeds 5–8; `wl60` (`WAIT_LIMIT` 60); `cw40` (`CAUTION_WINDOW` 40, never finished in batch 1); `sg200` (`SHOP_GOLD` 200, only ever tested on economy). The last four have the breaker off, so each is v5 plus one change. Code: commit `d8621cb` (11:19, pushed; includes the breaker), which matches the working copy the queue runs on | Pending | — |
| 75 | The user asked for the latest bot (11:27). `mybot` has the untested stand-off breaker on and queue 3 is running, so per the Latest-bot rule: `tools/release.py --src v5`, without `--verify` | Same ZIP as this morning: `submissions/cambridge-bot-latest.zip` = `cambridge-bot-2026-10-16.zip`, content hash `627283f38422` (verified 6/6 vs starter in experiment 58) | Re-release with the breaker only if queue 3 adopts it |
| 76 | Queue 3: `so1` (stand-off breaker, `STANDOFF_TURNS` 12 / `AVOID_ROUNDS` 40) vs v5 and v4, commit `d8621cb` | **vs v5: 26/72, −6,704** (5, 6, 7, 8 per seed). vs v4: 69/72, +33,722 (v5 managed 66/72, +29,354). Economy 4,324 (same as v5) | **Rejected.** It cures the v4 stall but loses badly to v5-like play. Likely cause: 12 turns near enemies with nobody hurt is common in normal contested farming, so champions abandon contested camps and altars for 40 rounds and hand them to the opponent. The real livelock is rare against v5-based bots (2 short stalls in 552 games). Set `STANDOFF_TURNS = 0` in `mybot` once queue 3 ends (editing now would mark its remaining CSV lines `+dirty`). Possible retry: only trigger when the team's tributed gems have been flat for 150+ rounds |
| 77 | Queue 3: `wl40` (`WAIT_LIMIT` 40) with fresh seeds 5–8 vs v5 | 40/72, +496 (11, 9, 11, 9 per seed); economy 4,378. With seeds 1–4: **80/144, +652** | Confirmed small gain, consistent across both sets (about 1.3 standard deviations). Meets the adoption bar set beforehand (80+/144). Choose between 40 and 60 once `wl60` reports |

Tooling fix during 21: `variant.py` used to delete and re-copy the whole bot folder; a locked build cache made one copy silently empty. It now overwrites in place, verifies the source files, and the gauntlet aborts if a copy fails.

### Fuel work (experiments 14–15)

Measured phase costs on lanes before optimising: gathering state ~175–340k, knowledge update ~200–450k, target scoring ~1.6M (sometimes twice per turn), movement ~150–350k. Python costs ~150 fuel per bytecode in this sandbox, so the fixes reduce Python work:

- **Distances.** Group distances read from one exported distance-field buffer.
- **Integer coordinates.** Per-group integer coordinates, linear index and map side are precomputed.
- **Closed-form need.** The required-champions count uses a square root instead of a loop.
- **Score cache.** Scores are cached for the turn, so a second target choice in the same turn is free.
- **Spatial buckets.** Groups sit in 10×10 buckets, so the "groups near me" scan touches only nearby ones.
- **Direct camp access.** Camp handle and type are read directly, and positions come from spawn tiles.
- **Kind cache.** Enemy champion types are cached.
- **Respawn timing.** Respawn expiry moved from the per-turn knowledge update into scoring and the target check, and respawning groups skip state checks until 2 rounds before their known respawn time.

Remaining big costs: the scoring loop (~600k every ~8 turns on lanes), `vision.camps()` with many camps visible, and `cambc.champions()` (~40–55k each).

### Draft experiments (experiment 9)

Each variant is the current bot with only the draft priority changed, played against v2 on all maps from both sides, plus the economy benchmark vs idle.

| Variant | Priority | Wins vs v2 | Economy (rounds, lower is better) |
|---|---|---|---|
| d0 | Vendetta, Varg, Ryth, Tavi, Stellar | 12/18 | 4,519 |
| d1 | Cassi & Issac, Vendetta, Varg, Ryth, Tavi | 8/18 | 4,388 |
| d3 | Vendetta, Varg, Tavi, Ryth, Vesper | 9/18 | 4,578 |
| **d4** | **Vendetta, Varg, Ryth, Marcella, Tavi** | **12/18** | **4,375** |
| d5 | Ryth, Varg, Marcella, Vendetta, Tavi | 11/18 | 4,442 |
| d6 | Vendetta, Stellar, Tavi, Varg, Ryth | 6/18 | 4,868 |
| d7 | Varg, Ryth, Tavi, Vendetta, Stellar | 7/18 | (not finished) |

### Shopping thresholds (experiment 11)

Economy benchmark vs idle (rounds to 1,000 gems summed over 9 maps), DEBUG off.

| Variant | Rule | Rounds |
|---|---|---|
| s0 | Recall to shop at 300 gold if below 75% HP (current) | 4,417 |
| s1 | 150 gold any HP, or walk home with 90 gold when spawn ≤ 10 tiles | 4,442 |
| s2 | 210 gold any HP, or walk home with 120 gold when spawn ≤ 10 tiles | 4,555 |
| s3 | 150 gold below 90% HP | 4,494 |

## Next ideas

- Squad play: test pairs / whole-team movement (local numbers win fights) against spread-out farming.
- Better ability use on camp clusters (AoE centred on the tile that hits most camps).
- Monolith strategy (poke from range 4 with ability champions) for monolith/rows-style maps.
- Altar locks on contested altars; teleport crystals for map shortcuts.
- Map-aware draft (picks chosen from the map during the draft phase).
