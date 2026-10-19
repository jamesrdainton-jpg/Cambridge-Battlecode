"""Chase check (report recommendation #5, part 1): before walking after an enemy champion that is out of reach, add to
their side of the fight ratio the enemies that may be near the target: visible ones beyond our 9-tile fight radius within
CHASE_NEAR of it, and unseen "phantoms" last seen within CHASE_NEAR of it in the last CHASE_MEMORY rounds (half weight;
skipped once is_alive() says they died, or if our burst would finish them). Chase only if the ratio still clears the
engage threshold, or the target dies within two turns of our damage. Optional leash (CHASE_LEASH, off). Retreat logic
unchanged. Flag CHASE_SAFE, ON in the variant.
Usage: python chase.py SRC DST"""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
src, dst = sys.argv[1], sys.argv[2]
subprocess.run([sys.executable, str(ROOT / "tools" / "variant.py"), dst, "--src", src],
               check=True, cwd=str(ROOT))
p = ROOT / "bots" / dst / "src" / "bot.py"
s = p.read_text()


def rep(old, new):
    global s
    n = s.count(old)
    assert n == 1, f"expected exactly one match, found {n}: {old[:200]!r}"
    s = s.replace(old, new)


# 1. Flag and constants, next to the fight thresholds (defined OFF, switched ON for the variant at the end).
rep("""FIGHT_GEM_EXTRA = 0.25
""", """FIGHT_GEM_EXTRA = 0.25
# Chase check: before walking after an enemy out of reach, add to their side the enemies that may be near the target:
# visible ones beyond our fight radius within CHASE_NEAR of it, and unseen ones last seen within CHASE_NEAR of it in the
# last CHASE_MEMORY rounds (half weight, alive per is_alive()); chase only if the ratio still clears the engage threshold,
# or the target dies within two turns of our damage. Retreat is unchanged. Self-play (v10 vs v11/meta, 1,487 chases):
# 55% met enemies not visible at contact and died 16.7% (8.7% without); Vendetta's chases died 22.5% (others 8-12%).
CHASE_SAFE = False
CHASE_NEAR = 8
CHASE_MEMORY = 10
# Chase leash: stop chasing this many tiles from where the chase began unless an ally is within 3 of the target (0 = off;
# chases that went 6+ tiles from contact died less often, 7-10%, than those of 2-4 tiles, 17-19%).
CHASE_LEASH = 0
""")

# 2. Per-champion state.
rep("""        self.ready = {}
        self.target_need = 1
""", """        self.ready = {}
        self.target_need = 1
        self.foes = {}  # enemy handle -> (round, position, health, dps, unit) when last seen in our fight radius
        self.chase_from = None
        self.chase_round = -100
""")

# 3. fight(): keep visible enemies outside the fight radius (and those ignored at their spawn) for the chase check.
rep("""        near = []
        campers = self.world.enemy_spawn if IGNORE_SPAWN_CAMPERS and not self.taking_damage() else None
        for e in self.enemies:
            try:
                ep = e.position()
            except Error:
                continue
            if campers is not None and campers.is_set(ep):
                continue
            d = cheb(ep, pos)
            if d <= 10:
                self.enemy_seen = self.now
            if d > 9:
                continue
""", """        near = []
        far = []  # visible enemies outside the fight radius or ignored at their spawn (chase check only)
        campers = self.world.enemy_spawn if IGNORE_SPAWN_CAMPERS and not self.taking_damage() else None
        for e in self.enemies:
            try:
                ep = e.position()
            except Error:
                continue
            if campers is not None and campers.is_set(ep):
                if CHASE_SAFE:
                    far.append((e, ep))
                continue
            d = cheb(ep, pos)
            if d <= 10:
                self.enemy_seen = self.now
            if d > 9:
                if CHASE_SAFE:
                    far.append((e, ep))
                continue
""")

# 4. Remember enemies in the fight radius.
rep("""        self.near_n = len(near)
        if not near:
            return False
""", """        self.near_n = len(near)
        if not near:
            return False
        if CHASE_SAFE:
            foes = self.foes
            for x in near:
                foes[int(x[0])] = (self.now, x[1], x[2], x[4], x[0])
""")

# 5. Record the allies counted in the ratio (same sums as before).
rep("""        for a in self.allies:
            try:
                ap = a.position()
                if cheb(ap, pos) > ALLY_RANGE:
                    continue
                our_hp += a.health()
                prof = PROFILE[a.champion_name()]
                our_dps += a.strength() * prof[0] + a.focus() * prof[1]
            except Error:
                pass
""", """        sup = []  # (position, health, dps) of the allies counted, for the chase check
        for a in self.allies:
            try:
                ap = a.position()
                if cheb(ap, pos) > ALLY_RANGE:
                    continue
                ahp = a.health()
                our_hp += ahp
                prof = PROFILE[a.champion_name()]
                adps = a.strength() * prof[0] + a.focus() * prof[1]
                our_dps += adps
                sup.append((ap, ahp, adps))
            except Error:
                pass
""")

# 6. The gate: only where fight() would chase (engage, target out of reach within 5, not at their spawn).
rep("""        engage = ratio >= engage_at
        if d <= self.rng:
""", """        engage = ratio >= engage_at
        if (CHASE_SAFE and engage and self.rng < d <= 5 and cheb(ep, world.enemy_spawn_center) > 3
                and not self.chase_ok(best, near, far, sup, burst, ratio, their_hp, their_dps, engage_at)):
            engage = False  # hold-band behaviour: free hits and casts in reach, hold if they close in, else farm
        if d <= self.rng:
""")

# 7. The check itself.
rep("""    def standoff_check(self, near, closest):
""", '''    def chase_ok(self, best, near, far, sup, burst, ratio, their_hp, their_dps, engage_at):
        """Chase check (CHASE_SAFE): whether the fight still favours us once enemies that may be near the target are
        counted: visible ones beyond our fight radius within CHASE_NEAR of it (half weight beyond 7 tiles), and unseen
        ones last seen within CHASE_NEAR of it in the last CHASE_MEMORY rounds (half weight; not the dead, nor those our
        burst would finish). Our side is unchanged. A target that dies within two turns of our damage is always chased."""
        ep = best[1]
        if best[2] <= burst + self.dps_now:
            return True  # it dies within two turns of our damage
        now = self.now
        if CHASE_LEASH:
            if now - self.chase_round > 2:
                self.chase_from = self.pos
            self.chase_round = now
            if cheb(self.pos, self.chase_from) >= CHASE_LEASH:
                backed = False
                for x in sup:
                    if cheb(x[0], ep) <= 3:
                        backed = True
                        break
                if not backed:
                    if DEBUG:
                        self.log(f"CHASE leash from={self.chase_from.x},{self.chase_from.y}")
                    return False
        known = set()
        for x in near:
            known.add(int(x[0]))
        foes = self.foes
        add_hp = 0.0
        add_dps = 0.0
        extra = 0
        for e, fp in far:
            h = int(e)
            known.add(h)
            dt = cheb(fp, ep)
            if dt > CHASE_NEAR:
                continue
            f = foes.get(h)
            if f is not None:
                fhp = f[2]
                fdps = f[3]
            else:
                try:
                    kind = self.kinds.get(h)
                    if kind is None:
                        kind = self.kinds[h] = e.champion_name()
                    prof = PROFILE[kind]
                    fhp = e.health()
                    fdps = e.strength() * prof[0] + e.focus() * prof[1]
                except Error:
                    continue
            foes[h] = (now, fp, fhp, fdps, e)
            w = 1.0 if dt <= 7 else 0.5
            add_hp += w * fhp
            add_dps += w * fdps
            extra += 1
        for h, f in foes.items():
            if h in known or now - f[0] > CHASE_MEMORY or f[2] <= burst or cheb(f[1], ep) > CHASE_NEAR:
                continue
            try:
                if not f[4].is_alive():  # works for unseen enemies
                    continue
            except Error:
                pass
            add_hp += 0.5 * f[2]
            add_dps += 0.5 * f[3]
            extra += 1
        if extra == 0:
            return True
        r = ratio * max(1.0, their_hp * their_dps) / max(1.0, (their_hp + add_hp) * (their_dps + add_dps))
        if DEBUG:
            self.log(f"CHASE {'go' if r >= engage_at else 'no'} ratio={r:.2f} from={ratio:.2f} extra={extra} "
                     f"add={add_hp:.0f}x{add_dps:.0f}")
        return r >= engage_at

    def standoff_check(self, near, closest):
''')

# Variant: flag ON.
rep("CHASE_SAFE = False\n", "CHASE_SAFE = True\n")
p.write_text(s)
print("chase check", dst)
