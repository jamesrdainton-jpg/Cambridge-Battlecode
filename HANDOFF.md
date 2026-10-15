# Handover — Cambridge Battlecode 2026 bot

State as of 2026-10-15. The full history of every experiment is in [DEVLOG.md](DEVLOG.md); this note is the short version for picking the work back up.

## Where everything is

- **Project folder:** `C:\Users\james\GitHub\Cambridge-Battlecode` (moved off OneDrive on 2026-10-14). The old OneDrive folder is empty and can be deleted once VS Code is no longer open on it.
- **Git:** remote `origin` = `https://github.com/jamesrdainton-jpg/Cambridge-Battlecode.git`. Nothing has been committed yet.
- **Python:** `.venv` (Python 3.13) holds the `cambc` CLI, pyright, ruff and pytest. Recreate it with `python -m venv .venv` and `.venv\Scripts\pip install -r requirements-dev.txt` if the folder ever moves.
- **Avast:** HTTPS scanning breaks `cambc maps pull`, `cambc login` and `cambc submit` unless `battlecode.co.uk` is excluded in Avast's Web Shield.

## The bots

| Bot | What it is |
|---|---|
| `bots/mybot` | Working version (DEBUG logging on). It is v4 plus cluster targeting, two in-range attack fixes and altar locks. |
| `bots/v4` | Last frozen version: fuel-safe, equal in strength to v3. Safest to submit if the newer features are not yet confirmed. |
| `bots/v1`–`v3` | Older frozen versions, kept as opponents. |
| `bots/starter`, `bots/idle`, `bots/probe` | Official starter, a do-nothing opponent (economy benchmark), and a map-dump tool. |
| `bots/lk0`, `bots/lk1`, `bots/cl`, `bots/cw40`, `bots/tbig`, `bots/tsmall` | Experiment variants (regenerable with `tools/variant.py`). Seeded copies (`*_s1`…`*_s4`) are temporary. |

**Measured strength (72 seeded games each):** v3 beats v2 42/72. v4 ≈ v3 (33/72). `cl` (cluster targeting) beats v4 38/72, +2,398 gems. The current `mybot` beats the starter 18/18.

## How to run things (from the project folder)

```
.venv\Scripts\cambc.exe run mybot v4 --map packs                 # one game (add --view to watch)
.venv\Scripts\python.exe tools\arena.py mybot v4                  # all 9 maps, both sides, ~1 min
.venv\Scripts\python.exe tools\gauntlet.py mybot --vs v4 --seeds 1,2,3,4   # 72 games + economy, ~7 min
.venv\Scripts\python.exe tools\variant.py NAME --set "bot.py:OLD=>NEW"     # A/B copy with a changed constant
```

Results of every gauntlet are appended to `matches/gauntlet.csv`.

**Judge changes on 72 seeded games, not 18.** One 18-game set swings by ±2 wins and ±800 gems from chaos alone. `gauntlet.py --seeds` perturbs both sides equally so the comparison stays fair.

## What was running at handover

Two background batches may still be finishing; their lines land in `matches/gauntlet.csv`:

- **Batch 1:** tribute-threshold variants. `tsmall` was still running; `cw40` and `tbig` were interrupted and need a re-run.
- **Batch 2:** altar locks, `lk1` (locks) vs `lk0` (no locks, but able to break locks), plus each vs v4. This decides whether locks stay on.

Note that v1–v4 have a bug where an enemy lock on the altar beside them stalls them forever, so beating v4 with locks proves little. Only `lk1` vs `lk0` is a fair test.

## Suggested next steps

1. **Read batch 2.** If `lk1` ≥ `lk0` over 72 games, keep `ALTAR_LOCKS = True` and freeze `mybot` as `v5` (`tools/variant.py v5`).
2. **Submit to the platform** and look at real match results. Real opponents are the most valuable signal we don't have yet. Use a DEBUG-off copy (`tools/variant.py` turns DEBUG off), then `cambc login` and `cambc submit <bot>`.
3. **Re-run the tribute variants** (`cw40`, `tbig`, `tsmall`) against the new baseline.
4. **Tune the draft per team size.** 3-pick maps (packs, collision, expanse) currently take Vendetta, Varg, Ryth; `draft.py` has a `BY_SIZE` hook. Test with `gauntlet.py --maps packs,collision,expanse --seeds 1,...,8`.
5. **Monoliths** (monolith and rows maps: 392–448 gems per capture) are never attempted. A late-game plan with tank rotation and stuns could be a big swing on those maps.
6. **Fight micro:** stun priorities, chasing gem carriers, contesting enemy captures.

## Things to know before changing code

- **Fuel.** Python costs ~150 fuel per bytecode here, so a turn affords only ~15k bytecodes. Keep per-turn loops small. The worst turns measure ~2.05M of the 2.5M budget on lanes (enable `DEBUG` and look for `HEAVY` log lines).
- **Logs.** Bot logs are only stored inside replay bundles; the tools read them for you. The replay viewer is never needed.
- **Shared memory (8 bytes).** Bytes 0–5 are target claims (one per champion, top bit = "ready at target"); bytes 6–7 are free.
