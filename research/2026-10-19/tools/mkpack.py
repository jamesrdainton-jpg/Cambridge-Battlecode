"""Make a pack-farming probe from a bot: before PACK_UNTIL, every champion follows the target claimed by the
lowest-slot ally that has a claim (the leader), and scoring ignores allies' claims (no surplus-helper penalty).
Usage: python mkpack.py SRC DST PACK_UNTIL [extra instrument.py args...]"""
import os as _os
from pathlib import Path as _Path
_HERE = _Path(__file__).resolve().parent
_ROOT = _HERE.parents[2]
_WORK = _Path(_os.environ.get("RS_WORK", str(_ROOT / "matches" / "research")))
import subprocess
import sys
from pathlib import Path

SP = _WORK
ROOT = _ROOT
src, dst, until = sys.argv[1], sys.argv[2], int(sys.argv[3])
subprocess.run([sys.executable, str(_HERE / "instrument.py"), src, dst] + sys.argv[4:], check=True)
p = ROOT / "bots" / dst / "src" / "bot.py"
s = p.read_text()
old_choose = '''        best = None
        best_score = 0.0
        best_need = 1
        best_via = False
        for score, g, need, via in cache[1]:
'''
new_choose = '''        if self.now < PACK_UNTIL:
            lead = self.pack_lead()
            if lead is not None and lead is not exclude:
                for score, g, need, via in cache[1]:
                    if g is lead and score > 0:
                        self.target_need = need
                        self.target_via = via
                        return g
        best = None
        best_score = 0.0
        best_need = 1
        best_via = False
        for score, g, need, via in cache[1]:
'''
assert s.count(old_choose) == 1
s = s.replace(old_choose, new_choose)
old_sc = "        claims = self.claims()\n"
assert s.count(old_sc) == 1
s = s.replace(old_sc, "        claims = self.claims()\n        if self.now < PACK_UNTIL:\n            claims = {}\n")
anchor = "    def score_groups(self):\n"
s = s.replace(anchor, '''    def pack_lead(self):
        """The group claimed by the lowest-slot ally below us (None if we are the leader)."""
        mem = cambc.shared_memory
        for i in range(min(self.n_allies, 6)):
            if i >= self.slot:
                return None
            v = mem[i]
            if v != 255:
                idx = v & 127
                if idx < len(self.world.groups):
                    return self.world.groups[idx]
        return None

''' + anchor)
s = s.replace("CAST_FIRST = True\n", f"CAST_FIRST = True\nPACK_UNTIL = {until}\n", 1)
assert f"PACK_UNTIL = {until}" in s
p.write_text(s)
print("pack probe", dst, "until", until)
