"""Retreat towards allies and fight back when caught (report recommendation #5 part 2, sections 3.2 and 4.6).

Evidence: 39 of 67 local retreat deaths had no ally within 7 tiles and were caught by the same enemies (49 of 67);
retreat() heads for spawn, never towards allies, and never fights back. Pursuers walk as fast as we do and stun or
hit from 4 tiles; contest death traces show retreating champions stunned ("stuck(can_move=False)") or losing a melee
chaser's full damage every turn while walking home.

Two flags, added next to the fight constants (off by default) and switched on in DST:
  RETREAT_ALLY  = 8     tiles; retreat to the nearest healthy ally within this range when it is nearer than spawn
                        (by path: spawn and the ally's surroundings are both roots of the one retreat field), only
                        while we have half our health
  RETREAT_FIGHT = True  hit back while retreating; stand and trade only when cornered

Usage: python retreat.py SRC DST   (builds bots/DST from bots/SRC with tools/variant.py, which forces DEBUG = False)
"""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
src, dst = sys.argv[1], sys.argv[2]
subprocess.run([sys.executable, str(ROOT / "tools" / "variant.py"), dst, "--src", src],
               cwd=ROOT, check=True)
p = ROOT / "bots" / dst / "src" / "bot.py"
s = p.read_text()


def sub(old, new):
    global s
    n = s.count(old)
    assert n == 1, f"expected exactly one occurrence, found {n}: {old[:80]!r}"
    s = s.replace(old, new)


# 1. Flags, next to the low-health retreat constants (off by default).
sub("""LOW_HP_RETREAT = 0.25
LOW_HP_REACH = 2
""", """LOW_HP_RETREAT = 0.25
LOW_HP_REACH = 2
# Retreat towards the nearest healthy ally within this many tiles, when it is nearer than spawn and no nearer the
# enemies than we are, instead of straight to spawn (0 = off). Only with half our health: below that spawn heals and
# an ally doesn't (contest test: 15 of 22 refuges begun under 25% health died within 10 rounds). 39 of 67 local
# retreat deaths had no ally within 7 tiles and were caught by the enemies they fled from.
RETREAT_ALLY = 0
# Hit back while retreating: pursuers walk as fast as we do and stun or hit from 4 tiles, and retreat() only walked.
# Always: walking-compatible casts, melee attack resets, a stun at a lone melee chaser. Cornered (stunned, or melee
# enemies on us, no dash ready and more of their damage on the way to safety than our health): every cast and the
# ranged basic attack too, standing to trade. Low-health retreats only stand when they can't move anyway.
RETREAT_FIGHT = False
""")

# 2. cast_offense: optionally only the casts that leave the walk (Cassi's stun), for use before walking on.
sub("""    def cast_offense(self, unit, upos, champion, kinds=(K_DAMAGE, K_AOE, K_CC)):
        \"\"\"Cast damage/stun abilities at a unit in range. Returns True if something was cast.\"\"\"
""", """    def cast_offense(self, unit, upos, champion, kinds=(K_DAMAGE, K_AOE, K_CC), walking=False):
        \"\"\"Cast damage/stun abilities at a unit in range (walking: only those compatible with walking).
        Returns True if something was cast.\"\"\"
""")
sub("""            if info.exclusive_with_movement and not self.can_move:
                continue
""", """            if info.exclusive_with_movement and (walking or not self.can_move):
                continue
""")

# 3. retreat(): head for spawn or a refuge ally (whichever is nearer by path), hitting back first.
sub("""        if camps is not None:
            zone |= camps
        if self.go(world.my_spawn, allow_dash=True, avoid=zone):
            return
        if DEBUG:
            self.why = f"stuck(can_move={self.can_move})"
""", """        if camps is not None:
            zone |= camps
        goal = world.my_spawn
        if RETREAT_ALLY or RETREAT_FIGHT:
            sd = world.spawn_field().get(self.pos)
            safe = sd if sd is not None and sd < W.UNREACHED else 99
            ally = self.refuge(near, zone, safe) if RETREAT_ALLY else None
            if ally is not None:
                goal = goal | ally[0]  # the field from both: walk to whichever is nearer by path
                safe = min(safe, ally[1])
            if RETREAT_FIGHT:
                self.fight_back(near, safe)
        if self.go(goal, allow_dash=True, avoid=zone):
            return
        if DEBUG:
            self.why = f"stuck(can_move={self.can_move})"
""")

# 4. The two helpers, before try_recall().
sub("""    def try_recall(self):
""", """    def refuge(self, near, zone, sd):
        \"\"\"Tiles within 2 of the nearest ally at most RETREAT_ALLY tiles away, nearer than spawn (sd), with half its
        health and no nearer any enemy than we are, outside enemy and camp reach; with its distance. None if none, or
        if we are below half health (spawn heals, an ally doesn't).\"\"\"
        if self.hp < 0.5 * self.max_hp:
            return None
        pos = self.pos
        best = None
        best_d = min(RETREAT_ALLY + 1, sd)
        for a in self.allies:
            try:
                ap = a.position()
            except Error:
                continue
            d = cheb(ap, pos)
            if d <= 2 or d >= best_d:
                continue  # already together, too far, or not nearer than spawn
            ok = True
            for x in near:
                if cheb(ap, x[1]) < x[5]:
                    ok = False  # walking to this ally walks towards that enemy
                    break
            if not ok:
                continue
            try:
                if a.health() < 0.5 * a.max_health():
                    continue
            except Error:
                continue
            best = ap
            best_d = d
        if best is None:
            return None
        tiles = Bitboard()
        tiles.draw_chebyshev(best, 2)
        tiles &= ~(self.world.block | self.world.all_camp_tiles | zone)
        if tiles.is_empty():
            return None
        if DEBUG:
            self.log(f"REFUGE ally at {best.x},{best.y} d={best_d} spawn={sd}")
        return tiles, best_d

    def fight_back(self, near, safe):
        \"\"\"Hit back while retreating, `safe` tiles from spawn or a refuge ally (RETREAT_FIGHT).\"\"\"
        chase = 0.0  # damage per turn of melee enemies next to us: they follow and hit every turn
        closest = None
        weakest = None
        for x in near:
            if x[3] <= 1 and x[5] <= 1:
                chase += x[4]
            if closest is None or x[5] < closest[5]:
                closest = x
            if x[5] <= 4 and (weakest is None or x[2] < weakest[2]):
                weakest = x
        if weakest is None:
            return
        cast0 = self.can_cast
        cornered = not self.can_move
        if not cornered and chase > 0 and self.hp >= LOW_HP_RETREAT * self.max_hp:
            dash = self.dash_slot
            if dash is None or not self.can_cast or self.abilities[dash].cooldown() != 0:
                cornered = self.hp < chase * safe  # walking to safety costs more than our health
        if cornered:
            # Stuns first, at whoever is closest; then damage at the weakest. Walking-exclusive casts stop the walk.
            self.cast_offense(closest[0], closest[1], champion=True, kinds=(K_CC,))
            self.cast_offense(weakest[0], weakest[1], champion=True)
        else:
            if chase > 0 and len(near) == 1:
                # A stunned lone chaser can neither follow nor hit: standing still for the stun costs nothing.
                self.cast_offense(closest[0], closest[1], champion=True, kinds=(K_CC,))
            self.cast_offense(closest[0], closest[1], champion=True, walking=True)
        if cornered or not self.ranged:
            # Melee attacks leave the walk (the first one was made in fight()); a ranged attack uses it up.
            in_range = [x for x in near if x[5] <= self.rng]
            if in_range:
                x = min(in_range, key=lambda x: x[2])
                self.basic_attack(x[0])
                self.use_reset(x[0])
        if DEBUG:
            self.log(f"FIGHTBACK cornered={cornered} chase={chase:.0f} safe={safe} hp={self.hp:.0f} st={self.st} "
                     f"cast={cast0 and not self.can_cast} can_move={self.can_move} can_attack={self.can_attack}")

    def try_recall(self):
""")

# 5. Switch the flags on in this variant.
sub("RETREAT_ALLY = 0\n", "RETREAT_ALLY = 8\n")
sub("RETREAT_FIGHT = False\n", "RETREAT_FIGHT = True\n")

p.write_text(s)
print("retreat variant", dst)
