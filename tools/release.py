"""Package the best bot as an upload ZIP and print where it is.

Usage: python tools/release.py [--src mybot] [--verify] [--check]

1. Copies bots/<src> into bots/release with DEBUG off (tools/variant.py); refuses unless SEED = 0.
2. Bundles it with `cambc bundle` as submissions/cambridge-bot-YYYY-MM-DD.zip (a different release
   on the same day gets -2, -3, ...; an identical one reuses the existing file) and copies that to
   submissions/cambridge-bot-latest.zip.
3. Checks the ZIP: exactly the bot's .py source files, identical to bots/<src> apart from DEBUG,
   DEBUG = False, SEED = 0, and every file compiles.
4. With --verify, plays the release against the starter on packs, lanes and monolith from both sides
   and fails unless it wins all 6 games with no error lines. Don't use it while a batch is running.

With --check, only reports whether cambridge-bot-latest.zip matches bots/<src> (builds nothing).
"""
from __future__ import annotations

import argparse
import datetime
import hashlib
import re
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PY = sys.executable
CAMBC = ROOT / ".venv" / "Scripts" / "cambc.exe"
SUB = ROOT / "submissions"
LATEST = SUB / "cambridge-bot-latest.zip"
VERIFY_MAPS = "packs,lanes,monolith"


def expected_files(src: str) -> dict[str, str]:
    """ZIP member name -> text the release should contain (DEBUG switched off)."""
    files = {}
    for p in sorted((ROOT / "bots" / src / "src").glob("*.py")):
        text = p.read_text(encoding="utf-8").replace("\r\n", "\n")
        if p.name == "bot.py":
            text = text.replace("DEBUG = True", "DEBUG = False")
        files[f"src/{p.name}"] = text
    return files


def zip_files(path: Path) -> dict[str, str]:
    with zipfile.ZipFile(path) as z:
        return {n: z.read(n).decode("utf-8").replace("\r\n", "\n") for n in z.namelist() if not n.endswith("/")}


def digest(files: dict[str, str]) -> str:
    h = hashlib.sha256()
    for name in sorted(files):
        h.update(name.encode() + b"\0" + files[name].encode() + b"\0")
    return h.hexdigest()[:12]


def problems(path: Path, src: str) -> list[str]:
    found = []
    got = zip_files(path)
    want = expected_files(src)
    if sorted(got) != sorted(want):
        found.append(f"ZIP holds {sorted(got)}, expected {sorted(want)}")
    for name in sorted(set(got) & set(want)):
        if got[name] != want[name]:
            found.append(f"{name} differs from bots/{src}/{name}")
        try:
            compile(got[name], name, "exec")
        except SyntaxError as e:
            found.append(f"{name} does not compile: {e}")
    bot = got.get("src/bot.py", "")
    if not re.search(r"^DEBUG = False$", bot, re.MULTILINE):
        found.append("src/bot.py does not set DEBUG = False")
    if not re.search(r"^SEED = 0$", bot, re.MULTILINE):
        found.append("src/bot.py does not set SEED = 0")
    return found


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--src", default="mybot", help="bot folder to release (default: mybot)")
    parser.add_argument("--verify", action="store_true", help="also play 6 games vs the starter")
    parser.add_argument("--check", action="store_true", help="only check that the latest ZIP is current")
    args = parser.parse_args()

    if args.check:
        if not LATEST.exists():
            raise SystemExit(f"no release yet: {LATEST} is missing")
        issues = problems(LATEST, args.src)
        state = "up to date with" if not issues else "OUT OF DATE vs"
        print(f"{LATEST} is {state} bots/{args.src}")
        for issue in issues:
            print("  -", issue)
        raise SystemExit(1 if issues else 0)

    src_bot = (ROOT / "bots" / args.src / "src" / "bot.py").read_text(encoding="utf-8")
    if not re.search(r"^SEED = 0$", src_bot, re.MULTILINE):
        raise SystemExit(f"bots/{args.src}/src/bot.py must have SEED = 0 for a release")
    subprocess.run([PY, str(ROOT / "tools" / "variant.py"), "release", "--src", args.src], cwd=ROOT, check=True,
                   stdout=subprocess.DEVNULL)

    SUB.mkdir(exist_ok=True)
    tmp = SUB / "release-tmp.zip"
    tmp.unlink(missing_ok=True)
    proc = subprocess.run([str(CAMBC), "bundle", "release", "--output", str(tmp)], cwd=ROOT, check=False,
                          capture_output=True, text=True)
    if proc.returncode != 0 or not tmp.exists():
        raise SystemExit(f"cambc bundle failed:\n{proc.stdout}{proc.stderr}")
    issues = problems(tmp, args.src)
    if issues:
        tmp.unlink()
        raise SystemExit("release ZIP failed its checks:\n  - " + "\n  - ".join(issues))

    # Name it by date; keep earlier same-day releases unless this one is identical.
    new_hash = digest(zip_files(tmp))
    day = datetime.date.today().isoformat()
    dated = None
    for i in range(1, 100):
        cand = SUB / (f"cambridge-bot-{day}.zip" if i == 1 else f"cambridge-bot-{day}-{i}.zip")
        if not cand.exists():
            tmp.replace(cand)
            dated = cand
            break
        if digest(zip_files(cand)) == new_hash:
            tmp.unlink()
            dated = cand
            break
    if dated is None:
        raise SystemExit("too many releases today")
    shutil.copyfile(dated, LATEST)

    if args.verify:
        out = subprocess.run([PY, str(ROOT / "tools" / "arena.py"), "release", "starter", "--maps", VERIFY_MAPS,
                              "--logs"], cwd=ROOT, check=False, capture_output=True, text=True).stdout
        print(out.rstrip())
        m = re.search(r"^release\s+wins\s+(\d+)/(\d+)", out, re.MULTILINE)
        errors = sum(int(n) for n in re.findall(r"errlines=(\d+)", out))
        if not m or m.group(1) != m.group(2) or m.group(2) == "0" or errors:
            raise SystemExit(f"verification FAILED (wins {m.group(0) if m else 'n/a'}, error lines {errors}); "
                             f"the ZIP was still written to {dated}")
        print(f"verified: {m.group(1)}/{m.group(2)} wins vs starter on {VERIFY_MAPS}, no error lines")

    size_kb = LATEST.stat().st_size / 1024
    print(f"\nLatest bot ZIP: {LATEST}")
    print(f"  same as       {dated}")
    print(f"  source bots/{args.src}, DEBUG off, {size_kb:.1f} KB, content hash {new_hash}")
    print(f"  files: {', '.join(sorted(zip_files(LATEST)))}")


if __name__ == "__main__":
    main()
