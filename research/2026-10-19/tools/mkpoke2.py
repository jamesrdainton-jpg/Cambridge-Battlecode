"""Poke fix probe: MONOLITH_POKE on, the poke ring recomputed from LIVE visible camps each turn (the cached ring
kept pokers on tiles next to dead camps forever), and area casts aimed at the in-range tile covering most live camps.
Usage: python mkpoke2.py SRC DST [instrument args]"""
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
src, dst = sys.argv[1], sys.argv[2]
subprocess.run([sys.executable, str(_HERE / "instrument.py"), src, dst,
                "--set", "bot.py:MONOLITH_POKE = False=>MONOLITH_POKE = True"] + sys.argv[3:], check=True)
p = ROOT / "bots" / dst / "src" / "bot.py"
s = p.read_text()
old = """        if not reach.is_set(pos) and cheb(cp, pos) <= 4:
            self.aoe_pos = cp
            self.cast_offense(camp, cp, champion=False)
            return
        danger = self.danger()
        self.go(self.poke_ring(g), avoid=self.keep_away(reach if danger is None else (reach | danger)))
"""
new = """        if not reach.is_set(pos) and cheb(cp, pos) <= 4:
            self.aoe_pos = self.best_aoe_tile([x[3] for x in alive], pos) or cp
            self.cast_offense(camp, cp, champion=False)
            return
        # Ring around the live camps only: tiles 4 from a live camp, outside every live camp's reach.
        ring = Bitboard()
        for x in alive:
            ring.draw_chebyshev(x[3], 4)
        ring &= ~(reach | self.world.block | self.world.all_camp_tiles)
        ring.set(pos, False)
        if ring.is_empty():
            ring = self.poke_ring(g)
        danger = self.danger()
        self.go(ring, avoid=self.keep_away(reach if danger is None else (reach | danger)))
"""
assert s.count(old) == 1
s = s.replace(old, new)
anchor = "    def poke_group(self, g, alive):\n"
s = s.replace(anchor, '''    def best_aoe_tile(self, cells, pos):
        """In-range (4) tile whose radius-1 square holds the most of these camp cells."""
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

''' + anchor)
p.write_text(s)
print("poke2 probe", dst)
