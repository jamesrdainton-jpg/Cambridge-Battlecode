# Handover — Cambridge Battlecode 2026 bot

State as of the evening of 2026-10-15 (paused so the PC can sleep). The full history of every experiment is in [DEVLOG.md](DEVLOG.md); this note is the short version for picking the work back up.

## Where everything is

- **Project folder:** `C:\Users\james\GitHub\Cambridge-Battlecode` (local disk, not synced by any OneDrive). The old `OneDrive\Documents\GitHub\Cambridge-Battlecode` folder is empty; open the new folder in VS Code (File → Open Folder) and delete the old one.
- **Git:** remote `origin` = `https://github.com/jamesrdainton-jpg/Cambridge-Battlecode.git`. Nothing committed yet. `.gitignore` keeps experiment bots, caches, the venv, `matches/`, `replays/` and `submissions/` out of git. Keep the GitHub repo private during the competition.
- **Python:** `.venv` (Python 3.13) holds the `cambc` CLI, pyright, ruff and pytest.
- **Avast:** exclude `battlecode.co.uk` in Avast's Web Shield, or `cambc maps pull` / `login` / `submit` fail.

## The bot to submit

- **Upload ZIP:** `submissions\cambridge-bot-2026-10-15.zip`, made with `cambc bundle` from `bots\release` (the current `mybot` with DEBUG off). Not yet verified in a game, because the test queue was busy; run one first: `.venv\Scripts\cambc.exe run release starter --map packs`.
- **Working copy:** `bots\mybot\src` (DEBUG on). Tuning constants are at the top of `bot.py`.
- **Frozen versions:** `bots\v1`–`v4` (v4 is the last frozen one). Freeze the next best as `v5` with `tools\variant.py v5`.

### What `mybot` contains beyond v4 (each measured with 72 seeded games unless noted)

| Change | Result |
|---|---|
| Cluster-aware damage (Varg splash / AoE aim) | 38/72 vs v4 |
| Passive altar locks (place when passing, no detours) | 42/72 vs a lock-aware bot; 72/72 vs starter |
| Gold weight 0.15 (gems first) | 45/72, +8,360 |
| Tribute at 30 carried gems (15 near an altar) | neutral to slightly positive, no economy cost |
| Recall as fast travel | 46/72, +3,920 |
| Retreat escapes awake camps; safer recalls; endgame banking; first-turn fuel fix | death count down in tests; not measured on its own |

### Settled by testing (don't redo)

- **Spread out.** Pairs (22/72) and whole-team squads (13/72) both lose.
- **Fight thresholds.** Retreat below 0.9, engage at 1.3: more aggressive is neutral, more cautious loses.
- **3-pick draft.** Vendetta, Varg, Ryth beat Marcella/Tavi/Cassi & Issac/no-Vendetta alternatives (one alternative, Vendetta/Ryth/Tavi, was 30/48 but level on gems and is queued for a re-test).
- **5th pick.** Tavi beats Stellar (13/32 for Stellar).

## How to run things (from the project folder)

```
.venv\Scripts\cambc.exe run mybot v4 --map packs                          # one game (add --view to watch)
.venv\Scripts\python.exe tools\arena.py mybot v4                           # all 9 maps, both sides, ~1 min
.venv\Scripts\python.exe tools\gauntlet.py mybot --vs v4 --seeds 1,2,3,4   # 72 games + economy, ~8 min
.venv\Scripts\python.exe tools\variant.py NAME --set "bot.py:OLD=>NEW"      # A/B copy with a changed constant
```

Results append to `matches\gauntlet.csv`. **Judge changes on 72 seeded games, not 18** (one 18-game set swings ±2 wins / ±800 gems). Don't run extra games while a batch runs (cambc's 2-minute build limit can fail them). Closing the laptop just pauses runs; they resume on wake.

## Queue to re-run on resume

The batch scripts are in `matches\` (`batch8.sh`, `batch9.sh`, `batch10.sh`). Their "wait for previous batch" lines need removing or re-pointing before re-running.

1. **Batch 8 (picks):** `p5V` (re-run, last result invalid), `p5C`, `p5W` on corners/elkring/lanes/monolith; `p4T`, `p4S`, `p4C` on interlock/rows. All vs `base8`.
2. **Batch 9:** `dE` (Vendetta, Ryth, Tavi on 3-pick maps) with seeds 9–16 vs `lk1`.
3. **Batch 10:** gold weight 0 (`gw0`) and 0.075 (`gw075`) vs `gw1` (0.15).
4. **Verification game** for the release ZIP, then freeze the best combination as `v5` and re-bundle.

## Next ideas after that

- Sweep `NEED_FRAC` (0.55) and `WAIT_LIMIT` (25); test `GEM_HUNT` (engage more readily vs gem carriers); item build order (Jungle first for tanks).
- Monoliths (monolith and rows maps, 392–448 gems per capture) are never attempted.
- Submit to the platform and study real matches — the most valuable signal not yet available.
