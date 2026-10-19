import os as _os
from pathlib import Path as _Path
_HERE = _Path(__file__).resolve().parent
_ROOT = _HERE.parents[2]
_WORK = _Path(_os.environ.get("RS_WORK", str(_ROOT / "matches" / "research")))
import sys
sys.path.insert(0, str(_ROOT / "tools"))
import replay_decode
sys.argv = ["replay_decode.py"] + sys.argv[1:]
replay_decode.main()
