"""Clone a bot into bots/<dst> and add printing-only instrumentation (decisions unchanged).

Usage: python instrument.py SRC DST [--set "bot.py:OLD=>NEW"]... [--draft "A,B,C"]

Prints (stdout, DEBUG stays off):
  I T <round> <name> <act> <sub> <hp> <maxhp> <gems> <x> <y>   one line per champion turn (compact)
  I F <round> <name> <ratio> <hp> <maxhp> <gems> <x> <y> <n_near> [kind:d:hp:maxhp:gems ...] allies=<n within 7>
  I D <round> <name> <gems_lost>                                   on death
"""
import os as _os
from pathlib import Path as _Path
_HERE = _Path(__file__).resolve().parent
_ROOT = _HERE.parents[2]
_WORK = _Path(_os.environ.get("RS_WORK", str(_ROOT / "matches" / "research")))
import argparse
import shutil
import sys
from pathlib import Path

ROOT = _ROOT

p = argparse.ArgumentParser()
p.add_argument("src")
p.add_argument("dst")
p.add_argument("--set", action="append", default=[])
p.add_argument("--draft", default="")
p.add_argument("--no-turns", action="store_true", help="skip per-turn lines (fights and deaths only)")
a = p.parse_args()

dst = ROOT / "bots" / a.dst
if dst.exists():
    shutil.rmtree(dst)
shutil.copytree(ROOT / "bots" / a.src, dst, ignore=shutil.ignore_patterns(".cambc", ".ruff_cache"))
b = dst / "src" / "bot.py"
s = b.read_text()


def rep(old, new, count=1):
    global s
    if s.count(old) != count:
        sys.exit(f"anchor found {s.count(old)} times (want {count}): {old!r}")
    s = s.replace(old, new)


# Hit flags.
rep("    def basic_attack(self, unit):\n        if not self.can_attack:\n            return False\n        try:\n            self.me.attack(unit)\n        except Error:\n            return False\n",
    "    def basic_attack(self, unit):\n        if not self.can_attack:\n            return False\n        try:\n            self.me.attack(unit)\n        except Error:\n            return False\n        self.i_hit = True\n")
rep("            try:\n                ok = ab.use(target)\n            except Error:\n                continue\n            if ok:\n                self.can_cast = False\n",
    "            try:\n                ok = ab.use(target)\n            except Error:\n                continue\n            if ok:\n                self.i_cast = True\n                self.can_cast = False\n")
# Fight snapshot after the ratio modifiers.
rep("        closest = min(x[5] - x[3] for x in near)  # how soon someone can hit me\n",
    "        closest = min(x[5] - x[3] for x in near)  # how soon someone can hit me\n"
    "        self.i_fight = (ratio, near)\n")

# Fight decision labels.
rep("            if x[5] <= self.rng and x[2] <= burst:\n", "            if x[5] <= self.rng and x[2] <= burst:\n                self.i_dec = 'fin'\n")
rep("            self.retreat(near)\n            return True\n", "            self.i_dec = 'ret'\n            self.retreat(near)\n            return True\n")
rep("        if d <= self.rng:\n            self.hit(e, ep, champion=True)\n            return True\n", "        if d <= self.rng:\n            self.i_dec = 'hit'\n            self.hit(e, ep, champion=True)\n            return True\n")
rep("        if self.cast_offense(e, ep, champion=True) and not engage:\n            return True\n", "        if self.cast_offense(e, ep, champion=True) and not engage:\n            self.i_dec = 'poke'\n            return True\n")
rep("        if engage and d <= 5 and cheb(ep, world.enemy_spawn_center) > 3:\n", "        if engage and d <= 5 and cheb(ep, world.enemy_spawn_center) > 3:\n            self.i_dec = 'chase'\n")
rep("        if not engage and closest <= 2:\n", "        if not engage and closest <= 2:\n            self.i_dec = 'hold'\n")
TURNS = "False" if a.no_turns else "True"
rep("        self._turn()\n",
    "        self.i_hit = False\n        self.i_cast = False\n        self.i_fight = None\n        self.i_dec = '-'\n"
    "        self.i_p0 = None\n"
    "        try:\n            self.i_p0 = self.me.position()\n        except Exception:\n            pass\n"
    "        self._turn()\n        self.i_log()\n")
rep("    def end(self):\n",
    "    def i_log(self):\n"
    "        name = CT.to_string(self.kind)[13:]\n"
    "        now = cambc.round_number()\n"
    "        if self.act == 'dead':\n"
    "            if getattr(self, 'i_alive', True):\n"
    "                print(f'I D {now} {name} {getattr(self, \"i_gems\", 0)}')\n"
    "            self.i_alive = False\n"
    "            if " + TURNS + ":\n"
    "                print(f'I T {now} {name} dead - 0 0 0 0 0')\n"
    "            return\n"
    "        self.i_alive = True\n"
    "        try:\n"
    "            me = self.me\n            p = me.position()\n            hp = me.health()\n            mh = me.max_health()\n            gm = me.gem_count()\n"
    "        except Exception:\n            return\n"
    "        self.i_gems = gm\n"
    "        moved = self.i_p0 is not None and (p.x != self.i_p0.x or p.y != self.i_p0.y)\n"
    "        sub = ('h' if self.i_hit else '') + ('c' if self.i_cast else '') + ('m' if moved else '')\n"
    "        if " + TURNS + ":\n"
    "            print(f'I T {now} {name} {self.act} {sub or \"-\"} {hp:.0f} {mh:.0f} {gm} {p.x} {p.y} {me.gold_count()}')\n"
    "        f = self.i_fight\n"
    "        if f is not None:\n"
    "            ratio, near = f\n"
    "            parts = []\n"
    "            for x in near:\n"
    "                try:\n"
    "                    k = CT.to_string(self.kinds.get(int(x[0]), 0))[13:]\n"
    "                    parts.append(f'{k}:{x[5]}:{x[2]:.0f}:{x[0].max_health():.0f}:{x[6]}')\n"
    "                except Exception:\n"
    "                    pass\n"
    "            na = 0\n"
    "            for al in self.allies:\n"
    "                try:\n"
    "                    if cheb(al.position(), p) <= 7:\n"
    "                        na += 1\n"
    "                except Exception:\n"
    "                    pass\n"
    "            print(f'I F {now} {name} {ratio:.3f} {hp:.0f} {mh:.0f} {gm} {p.x} {p.y} {sub or \"-\"} {self.act}/{self.i_dec} allies={na} ' + ' '.join(parts))\n"
    "\n"
    "    def end(self):\n")

for spec in a.set:
    fname, change = spec.split(":", 1)
    old, new = change.split("=>", 1)
    f = dst / "src" / fname
    t = f.read_text() if fname != "bot.py" else s
    if old not in t:
        sys.exit(f"{old!r} not found in {fname}")
    t = t.replace(old, new)
    if fname == "bot.py":
        s = t
    else:
        f.write_text(t)
b.write_text(s)
if a.draft:
    d = dst / "src" / "draft.py"
    text = d.read_text()
    start = text.index("PRIORITY = (")
    end = text.index(")", start) + 1
    picks = ", ".join(f"CD.{x.strip()}" for x in a.draft.split(","))
    d.write_text(text[:start] + f"PRIORITY = ({picks},)" + text[end:])
print("created", dst)
