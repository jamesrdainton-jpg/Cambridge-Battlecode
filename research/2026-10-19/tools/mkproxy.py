"""Pro-style variant of our bot: instrument SRC into DST with --set options, then optionally add the pack patch
(PACK_UNTIL) and the poke fix (live ring + AoE aim, MONOLITH_POKE on).
Usage: python mkproxy.py SRC DST [--pack N] [--poke] [--set ...]..."""
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
args = sys.argv[1:]
src, dst = args[0], args[1]
rest = args[2:]
pack = None
poke = False
if "--pack" in rest:
    i = rest.index("--pack")
    pack = int(rest[i + 1])
    del rest[i:i + 2]
if "--poke" in rest:
    rest.remove("--poke")
    poke = True
    rest += ["--set", "bot.py:MONOLITH_POKE = False=>MONOLITH_POKE = True"]
subprocess.run([sys.executable, str(_HERE / "instrument.py"), src, dst] + rest, check=True)
p = ROOT / "bots" / dst / "src" / "bot.py"
s = p.read_text()


def rep(old, new):
    global s
    assert s.count(old) == 1, old[:80]
    s = s.replace(old, new)


if poke:
    rep("""        if not reach.is_set(pos) and cheb(cp, pos) <= 4:
            self.aoe_pos = cp
            self.cast_offense(camp, cp, champion=False)
            return
        danger = self.danger()
        self.go(self.poke_ring(g), avoid=self.keep_away(reach if danger is None else (reach | danger)))
""", """        if not reach.is_set(pos) and cheb(cp, pos) <= 4:
            self.aoe_pos = self.best_aoe_tile([x[3] for x in alive], pos) or cp
            self.cast_offense(camp, cp, champion=False)
            return
        ring = Bitboard()
        for x in alive:
            ring.draw_chebyshev(x[3], 4)
        ring &= ~(reach | self.world.block | self.world.all_camp_tiles)
        ring.set(pos, False)
        if ring.is_empty():
            ring = self.poke_ring(g)
        danger = self.danger()
        self.go(ring, avoid=self.keep_away(reach if danger is None else (reach | danger)))
""")
    rep("    def poke_group(self, g, alive):\n", '''    def best_aoe_tile(self, cells, pos):
        best = None
        best_n = 0
        for c in cells:
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    tx = c.x + dx
                    ty = c.y + dy
                    if max(abs(tx - pos.x), abs(ty - pos.y)) > 4:
                        continue
                    n = 0
                    for o in cells:
                        if abs(o.x - tx) <= 1 and abs(o.y - ty) <= 1:
                            n += 1
                    if n > best_n:
                        best_n = n
                        best = Vec2(tx, ty)
        return best

    def poke_group(self, g, alive):
''')
if pack is not None:
    rep('''        best = None
        best_score = 0.0
        best_need = 1
        best_via = False
        for score, g, need, via in cache[1]:
''', '''        if self.now < PACK_UNTIL:
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
''')
    rep("        claims = self.claims()\n", "        claims = self.claims()\n        if self.now < PACK_UNTIL:\n            claims = {}\n")
    rep("    def score_groups(self):\n", '''    def pack_lead(self):
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

    def score_groups(self):
''')
    rep("CAST_FIRST = True\n", f"CAST_FIRST = True\nPACK_UNTIL = {pack}\n")
p.write_text(s)
print("proxy", dst, "pack", pack, "poke", poke)
