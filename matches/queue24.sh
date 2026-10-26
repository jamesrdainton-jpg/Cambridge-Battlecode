#!/usr/bin/env bash
# Queue 24 (2026-10-26, cambc 4.0.0, 70 maps): smoke test of v13 (Python) and cpp13 (C++) on the new patch and maps.
cd "$(dirname "$0")/.."
PY=.venv/Scripts/python.exe; [ -x "$PY" ] || PY=.venv/bin/python
$PY tools/arena.py v13 idle --one-side --logs
$PY tools/arena.py cpp13 idle --one-side --logs
