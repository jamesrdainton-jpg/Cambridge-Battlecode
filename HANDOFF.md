# Handover — Cambridge Battlecode 2026 bot

State as of late morning on 2026-10-16. The full history of every experiment is in [DEVLOG.md](DEVLOG.md); this note is the short version for picking the work back up.

**Team rule:** more than one person works on this repo, each on their own computer, so every result must be reproducible on a different computer from a git commit. Commit code before testing it, record the commit and the exact command, keep queue scripts and `matches\gauntlet.csv` in git, and use cambc 2.1.6 with the committed maps. Details and open gaps are in the "Team rule" section near the top of DEVLOG.md.

## Where everything is

- **Project folder:** on James's PC, `C:\Users\james\GitHub\Cambridge-Battlecode` (local disk, not synced by any OneDrive). Teammates work in their own clones.
- **Git:** remote `origin` = `https://github.com/jamesrdainton-jpg/Cambridge-Battlecode.git`. Several people commit and push, so pull before starting. `.gitignore` keeps experiment bots, caches, the venv, replays and `submissions/` out of git; the results table, queue scripts and logs in `matches/` are tracked. Keep the GitHub repo private during the competition.
- **Python:** `.venv` (Python 3.13) holds the `cambc` CLI, pyright, ruff and pytest.
- **Avast:** exclude `battlecode.co.uk` in Avast's Web Shield, or `cambc maps pull` / `login` / `submit` fail.

## The bot to submit

- **Upload ZIP:** `submissions\cambridge-bot-latest.zip` (on James's PC, `C:\Users\james\GitHub\Cambridge-Battlecode\submissions\cambridge-bot-latest.zip`). It is the same file as `cambridge-bot-2026-10-16.zip`, content hash `627283f38422`. Built from `bots\mybot` at commit `85be59a` (= frozen `v5`) with DEBUG off, and verified 6/6 vs the starter. ZIPs aren't in git: on another computer, rebuild with `tools\release.py`, which gives the same hash from the same commit.
- **When the user asks for the latest bot:** run `.venv\Scripts\python.exe tools\release.py --verify` (leave out `--verify` while a batch runs), then give them the ZIP's full path. The steps are in the "Latest bot" section at the top of DEVLOG.md; update it after each release.
- **Working copy:** `bots\mybot\src` (DEBUG on). Tuning constants are at the top of `bot.py`. Experimental flags (`TANK_JUNGLE_FIRST`, `JUNGLE_AWARE`, `GEM_HUNT`) stay off until a test adopts them. **Exception:** the new stand-off breaker (`STANDOFF_TURNS = 12`) is on and under test in queue 3. Until it is adopted, release from v5 (`tools\release.py --src v5`); the current ZIP already has v5's code. `STANDOFF_TURNS = 0` gives exactly v5's behaviour.
- **Frozen versions:** `bots\v1`–`v5` (v5 is the last frozen one and the baseline for tests). Freeze the next best as `v6` with `tools\variant.py v6`.

### What `mybot` / v5 contains beyond v4 (each measured with 72 seeded games unless noted)

| Change | Result |
|---|---|
| Cluster-aware damage (Varg splash / AoE aim) | 38/72 vs v4 |
| Passive altar locks (place when passing, no detours) | 42/72 vs a lock-aware bot; 72/72 vs starter |
| Gold weight 0.15 (gems first) | 45/72, +8,360 |
| Tribute at 30 carried gems (15 near an altar) | neutral to slightly positive, no economy cost |
| Recall as fast travel | 46/72, +3,920 |
| Retreat escapes awake camps; safer recalls; endgame banking; first-turn fuel fix | death count down in tests; not measured on its own |
| 3-pick maps draft Vendetta, Ryth, Tavi | 58/96 over two 48-game sets, gems level |

### Settled by testing (don't redo)

- **Spread out.** Pairs (22/72) and whole-team squads (13/72) both lose.
- **Fight thresholds.** Retreat below 0.9, engage at 1.3: more aggressive is neutral, more cautious loses.
- **Gold weight.** 0.15 beats 0.3 and 0.5; 0 and 0.075 are neutral with slower farming. Stays 0.15.
- **Draft.** 3 picks: Vendetta, Ryth, Tavi. 5th pick: Tavi beats Stellar, Vesper, Cassi & Issac and Willow. 4th pick: Marcella beats Tavi, Stellar and Cassi & Issac (29/72 over two tests).
- **Squad sizing and items.** `NEED_FRAC` 0.55 beats 0.45 and 0.65. Waiting 15 turns for the squad loses (31/72). Jungle-first for tanks loses (26/72), and Jungle-aware sizing is neutral. `GEM_HUNT` 0.2 is neutral.

## How to run things (from the project folder)

```
.venv\Scripts\cambc.exe run mybot v5 --map packs                          # one game (add --view to watch)
.venv\Scripts\python.exe tools\arena.py mybot v5                           # all 9 maps, both sides, ~1 min
.venv\Scripts\python.exe tools\gauntlet.py mybot --vs v5 --seeds 1,2,3,4   # 72 games + economy, ~9 min
.venv\Scripts\python.exe tools\variant.py NAME --set "bot.py:OLD=>NEW"      # A/B copy with a changed constant
.venv\Scripts\python.exe tools\release.py --verify                         # build + verify the upload ZIP
.venv\Scripts\python.exe tools\repro_check.py                              # does this PC reproduce the team's games?
```

On Mac/Linux use `.venv/bin/python` and `.venv/bin/cambc`. Setting up a new computer: see "Setting up on a new computer" in DEVLOG.md.

Results append to `matches\gauntlet.csv`. **Judge changes on 72 seeded games, not 18** (one 18-game set swings ±2 wins / ±800 gems). Don't run extra games while a batch runs (cambc's 2-minute build limit can fail them). Closing the laptop just pauses runs; they resume on wake.

## Queue in progress

**Queue 2 is complete** (experiments 59–70): nothing beat v5 clearly. The only lead was `wl40` (`WAIT_LIMIT` 40) at 40/72, within noise.

**Queue 3** (`matches\queue3.sh`, output in `matches\queue3.log`, started 11:19 on 2026-10-16, about an hour). It runs:
1. `so1`, the stand-off breaker, vs v5 and v4 (experiments 72–73: a livelock that left our team scoring nothing for 1,300+ rounds in 7 of 72 games vs v4).
2. `wl40` with fresh seeds 5–8, then `wl60`, `cw40` (`CAUTION_WINDOW` 40) and `sg200` (`SHOP_GOLD` 200), each vs v5 with the breaker off.

Finished so far:
- `so1` lost to v5 (26/72) though it beat v4 69/72, so the breaker is rejected. Set `STANDOFF_TURNS = 0` in `mybot` after the queue ends.
- `wl40` confirmed: 80/144 over both seed sets.

If it was interrupted, check `matches\gauntlet.csv` for lines tagged `queue3`, delete the finished steps from the script and re-run it. The variant lines at the top are safe to repeat.

When it ends:
1. Log each result in DEVLOG.md.
2. Adopt `so1` if it doesn't lose to v5 and clearly beats v4 (fewer stalls). Adopt `wl40` if seeds 5–8 confirm it (combined 80+/144); other changes need 42/72 or better with positive gems.
3. Freeze `v6` and commit it, run `tools\release.py --verify`, and update the "Latest bot" section. Queue 3's code is commit `d8621cb`.

## Next ideas after that

- **Optional: platform information**, only if someone can be bothered (nothing depends on it). Useful items: the match history (opponent, map, result, both scores), other teams' drafts, a leaderboard snapshot, any platform errors for our bot, and replays. Replays can be bulk-downloaded with `tools\download_replays.js` (browser console) into `replays\platform\`. A replay's map can be found by matching its bytes against `maps\`, but replays don't record team names.
- Monoliths (monolith and rows maps, 392–448 gems per capture) are never attempted.
- Submit to the platform and study real matches — the most valuable signal not yet available.
