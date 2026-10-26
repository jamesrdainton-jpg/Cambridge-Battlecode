# C++ vs Python fuel benchmark (cambc 3.0.5)

Two bots that do the same work, one measurement per gameplay turn (turns 3–9), and print the fuel each step used.

Set up (from the repo root; the bots are throwaway, `bots/*` is git-ignored except the tracked bots):

```
mkdir -p bots/bench_cpp/src bots/bench_py/src
cp sdk/templates/cpp/.clangd bots/bench_cpp/            # C++ bot layout as `cambc new` makes it
cp research/2026-10-25/tools/fuel_bench/bench_cpp_main.cpp bots/bench_cpp/src/main.cpp
cp research/2026-10-25/tools/fuel_bench/bench_py_main.py  bots/bench_py/src/main.py
.venv/Scripts/cambc.exe run bench_cpp bench_py --map 01big-world --rounds 30 --release
```

Then read `BENCH` lines from `team-a.stdout` (C++) and `team-b.stdout` (Python) inside the replay bundle (a zip).
`--release` matters: it builds as the platform does. A step that needs more than one turn's fuel is suspended
and resumes next round, which corrupts its number, so keep each step under the limit (C++ 100k, Python 2.5M).

Results on 2026-10-25 (01big-world, 100×100), fuel and share of one turn's limit:

| Step | C++ (limit 100,000) | Python (limit 2,500,000) |
|---|---|---|
| 2,000-iteration LCG + array update | 45,023 (45%) | 615,833 (25%) |
| Scoring loop: 1,200 evaluations of 24 records | 16,188 (16%) | 815,201 (33%) |
| Hand-written 8-way BFS, 15×15 grid | 10,899 (11%) | 347,827 (14%) |
| 100 × `me.position()` | 8,320 (8.3%) | 277,023 (11%) |
| SDK `DistanceField.compute`, whole 100×100 map | 29,941 (30%) | 754,546 (30%) |
| `game_map.camp_groups()` (24 groups) | 25,200 (25%) | 806,607 (32%) |
| `vision.camps()` | 904 (0.9%) | 20,915 (0.8%) |
