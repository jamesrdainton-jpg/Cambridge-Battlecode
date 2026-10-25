"""Clone bots/mybot into bots/<name> with an optional draft priority override.

Usage: python tools/variant.py NAME [--draft "VENDETTA,VARG,..."] [--set "bot.py:OLD=>NEW"]...
"""
import argparse
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

parser = argparse.ArgumentParser()
parser.add_argument("name")
parser.add_argument("--src", default="mybot")
parser.add_argument("--draft", default="")
parser.add_argument("--set", action="append", default=[])
args = parser.parse_args()

dst = ROOT / "bots" / args.name
src_dir = dst / "src"
if src_dir.exists():
    shutil.rmtree(src_dir, ignore_errors=True)
# Overwrite in place: the old build cache (.cambc) can be locked briefly on Windows.
shutil.copytree(ROOT / "bots" / args.src, dst, ignore=shutil.ignore_patterns(".cambc", ".ruff_cache", "__pycache__"),
                dirs_exist_ok=True)
for needed in ("main.py", "bot.py", "draft.py", "world.py"):
    if not (src_dir / needed).exists():
        raise SystemExit(f"copy of {args.src} into {args.name} is missing {needed}")
if args.draft:
    picks = ", ".join(f"CD.{p.strip()}" for p in args.draft.split(","))
    d = dst / "src" / "draft.py"
    text = d.read_text()
    start = text.index("PRIORITY = (")
    end = text.index(")", text.index("PRIORITY = (")) + 1
    d.write_text(text[:start] + f"PRIORITY = ({picks},)" + text[end:])
for spec in args.set:
    fname, change = spec.split(":", 1)
    old, new = change.split("=>", 1)
    f = dst / "src" / fname
    text = f.read_text()
    if old not in text:
        raise SystemExit(f"{old!r} not found in {fname}")
    f.write_text(text.replace(old, new))
b = dst / "src" / "bot.py"
b.write_text(b.read_text().replace("DEBUG = True", "DEBUG = False"))
print("created", dst)
