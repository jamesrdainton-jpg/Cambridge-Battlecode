# Handover — Cambridge Battlecode 2026 bot

State as of the morning of 2026-10-16. The full history of every experiment is in [DEVLOG.md](DEVLOG.md); this note is the short version for picking the work back up.

## Where everything is

- **Project folder:** `C:\Users\james\GitHub\Cambridge-Battlecode` (local disk, not synced by any OneDrive).
- **Git:** remote `origin` = `https://github.com/jamesrdainton-jpg/Cambridge-Battlecode.git`; the user commits. `.gitignore` keeps experiment bots, caches, the venv, `matches/`, `replays/` and `submissions/` out of git. Keep the GitHub repo private during the competition.
- **Python:** `.venv` (Python 3.13) holds the `cambc` CLI, pyright, ruff and pytest.
- **Avast:** exclude `battlecode.co.uk` in Avast's Web Shield, or `cambc maps pull` / `login` / `submit` fail.

## The bot to submit

- **Upload ZIP:** `C:\Users\james\GitHub\Cambridge-Battlecode\submissions\cambridge-bot-latest.zip` (same file as `cambridge-bot-2026-10-16.zip`). Built from `bots\mybot` (= frozen `v5`) with DEBUG off, and verified 6/6 vs the starter.
- **When the user asks for the latest bot:** run `.venv\Scripts\python.exe tools\release.py --verify` (leave out `--verify` while a batch runs), then give them the ZIP's full path. The steps are in the "Latest bot" section at the top of DEVLOG.md; update it after each release.
- **Working copy:** `bots\mybot\src` (DEBUG on). Tuning constants are at the top of `bot.py`. Experimental flags (`TANK_JUNGLE_FIRST`, `JUNGLE_AWARE`, `GEM_HUNT`) stay off until a test adopts them.
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
- **Draft.** 3 picks: Vendetta, Ryth, Tavi. 5th pick: Tavi beats Stellar, Vesper, Cassi & Issac and Willow. 4th pick: Marcella beats Tavi and Stellar; Cassi & Issac was 13/24 (within noise), re-test in queue 2.

## How to run things (from the project folder)

```
.venv\Scripts\cambc.exe run mybot v5 --map packs                          # one game (add --view to watch)
.venv\Scripts\python.exe tools\arena.py mybot v5                           # all 9 maps, both sides, ~1 min
.venv\Scripts\python.exe tools\gauntlet.py mybot --vs v5 --seeds 1,2,3,4   # 72 games + economy, ~9 min
.venv\Scripts\python.exe tools\variant.py NAME --set "bot.py:OLD=>NEW"      # A/B copy with a changed constant
.venv\Scripts\python.exe tools\release.py --verify                         # build + verify the upload ZIP
```

Results append to `matches\gauntlet.csv`. **Judge changes on 72 seeded games, not 18** (one 18-game set swings ±2 wins / ±800 gems). Don't run extra games while a batch runs (cambc's 2-minute build limit can fail them). Closing the laptop just pauses runs; they resume on wake.

## Queue in progress

**Queue 2** (`matches\queue2.sh`, output in `matches\queue2.log`, started 09:18 on 2026-10-16, about 80 minutes). It runs v5 vs v4, then each variant vs v5: `tj1` (tanks buy Jungle first), `ja1` (Jungle-aware squad sizing), `nf45` / `nf65` (`NEED_FRAC`), `wl15` / `wl40` (`WAIT_LIMIT`), `gh2` (`GEM_HUNT` 0.2), then `p4C2` (Cassi & Issac 4th, seeds 7–18 on interlock and rows). If it was interrupted, check `matches\gauntlet.csv` for the lines tagged `queue2`, delete the finished steps from the script and re-run it (the variant lines at the top are safe to repeat).

When it ends: log each result in DEVLOG.md, adopt anything at 42/72 or better with positive gems (confirm borderline ones with seeds 5–8), freeze `v6`, run `tools\release.py --verify`, and update the "Latest bot" section.

## Next ideas after that

- Combine `tj1` + `ja1` if either helps on its own.
- Monoliths (monolith and rows maps, 392–448 gems per capture) are never attempted.
- Submit to the platform and study real matches — the most valuable signal not yet available.
