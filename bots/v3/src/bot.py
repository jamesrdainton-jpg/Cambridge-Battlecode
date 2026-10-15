"""Champion brain: shop, fight, tribute, farm. One instance per champion."""
import cambc
from cambc import game_map, vision, Vec2, Bitboard, DistanceField, Team
from cambc import ChampionType as CT, ItemType as IT, Error

import world as W

ST_ALIVE, ST_RECALL, ST_SUBMIT, ST_MOVE, ST_ATTACK = 1, 2, 4, 8, 16
ST_CAST, ST_TP = 2048, 4096

K_RESET, K_DAMAGE, K_AOE, K_CC, K_HEAL, K_DASH, K_SHIELD = 1, 2, 3, 4, 5, 6, 7
ABILITY_KIND = {
    "AbilityAttackReset": K_RESET, "AbilityDamage": K_DAMAGE, "AbilityAoeDamage": K_AOE, "AbilityCc": K_CC,
    "AbilityHeal": K_HEAL, "AbilityDash": K_DASH, "AbilityShield": K_SHIELD,
}

SHARD = {  # (shard, emblem) per family/stat
    ("MONSTER", "S"): (IT.MONSTER_SHARD_OF_STRENGTH, IT.MONSTER_EMBLEM_OF_STRENGTH),
    ("MONSTER", "F"): (IT.MONSTER_SHARD_OF_FOCUS, IT.MONSTER_EMBLEM_OF_FOCUS),
    ("POWER", "S"): (IT.POWER_SHARD_OF_STRENGTH, IT.POWER_EMBLEM_OF_STRENGTH),
    ("POWER", "F"): (IT.POWER_SHARD_OF_FOCUS, IT.POWER_EMBLEM_OF_FOCUS),
    ("POWER", "H"): (IT.POWER_SHARD_OF_HEALTH, IT.POWER_EMBLEM_OF_HEALTH),
    ("JUNGLE", "H"): (IT.JUNGLE_SHARD_OF_HEALTH, IT.JUNGLE_EMBLEM_OF_HEALTH),
    ("DURABILITY", "H"): (IT.DURABILITY_SHARD_OF_HEALTH, IT.DURABILITY_EMBLEM_OF_HEALTH),
}
# Each stage: (family, stat, shards owned when the stage is complete).
BUILD_STR = [("MONSTER", "S", 5), ("POWER", "S", 5), ("JUNGLE", "H", 5), ("POWER", "S", 10),
             ("DURABILITY", "H", 5), ("POWER", "S", 30), ("POWER", "H", 30)]
BUILD_FOCUS = [("MONSTER", "F", 5), ("POWER", "F", 5), ("JUNGLE", "H", 5), ("POWER", "F", 10),
               ("DURABILITY", "H", 5), ("POWER", "F", 30), ("POWER", "H", 30)]
FOCUS_CHAMPS = (CT.STELLAR, CT.PRISM, CT.CASSI)

DEBUG = False
# Testing only: a non-zero SEED perturbs target scores by up to 2% so repeated matches diverge.
SEED = 0

DIRS = (Vec2(1, 0), Vec2(-1, 0), Vec2(0, 1), Vec2(0, -1), Vec2(1, 1), Vec2(1, -1), Vec2(-1, 1), Vec2(-1, -1))


PROFILE = {}


def build_profiles():
    for kind in range(12):
        d = cambc.Champion.design(kind)  # type: ignore[arg-type]
        str_mul = 1.0
        foc_mul = 0.0
        for ab in d.abilities():
            info = ab.info()
            name = type(info).__name__
            if name == "AbilityAttackReset":
                str_mul += 0.125
            elif name in ("AbilityDamage", "AbilityAoeDamage", "AbilityCc"):
                foc_mul += getattr(info, "modifier", 0.0) / 8.0
        PROFILE[kind] = (str_mul, foc_mul, d.base_stats().base_attack_range)


def cheb(a, b):
    dx = a.x - b.x
    dy = a.y - b.y
    if dx < 0:
        dx = -dx
    if dy < 0:
        dy = -dy
    return dx if dx > dy else dy


class Bot:
    def __init__(self):
        self.world = W.World()
        build_profiles()
        me = cambc.me()
        self.me = me
        self.handle = int(me)
        self.kind = me.champion_name()
        stats = me.base_stats()
        self.ranged = stats.base_attack_range > 1
        self.rng = stats.base_attack_range
        allies = cambc.champions(Team.ALLY)
        handles = sorted(int(c) for c in allies)
        self.slot = handles.index(self.handle) if self.handle in handles else 0
        self.n_allies = len(handles)
        self.abilities = me.abilities()
        self.ab_kind = []
        self.ab_info = []
        for ab in self.abilities:
            info = ab.info()
            self.ab_info.append(info)
            self.ab_kind.append(ABILITY_KIND.get(type(info).__name__, 0) if info is not None else 0)
        self.build = BUILD_FOCUS if self.kind in FOCUS_CHAMPS else BUILD_STR
        self.build_done = 0
        self.remote_shop = self.kind == CT.TAVI
        self.target = None
        self.target_round = -100
        self.mode = "farm"
        self.last_hp = None
        self.errors = 0
        self.idle_turns = 0
        self.wait_turns = 0
        self.acts = {}
        self.ready = {}
        self.target_need = 1
        # Altar distances for every group, so target choice can weigh the tribute trip.
        af = self.world.altar_field()
        for g in self.world.groups:
            d = af.get(g.anchor)
            g.near_altar = d if d is not None else W.UNREACHED

    # ------------------------------------------------------------------ helpers
    def log(self, *args):
        print(f"r{self.now} {CT.to_string(self.kind)[13:]}", *args)

    def read_state(self):
        st = int(self.me.state())
        self.st = st
        self.can_move = bool(st & ST_MOVE)
        self.can_attack = bool(st & ST_ATTACK)
        self.can_cast = bool(st & ST_CAST)
        return st

    def occupancy(self):
        occ = vision.champion_tiles() | vision.camp_tiles() | vision.teleport_tiles()
        occ.set(self.pos, False)
        return occ

    def go(self, roots, allow_dash=True, avoid=None):
        """Walk one step (plus a dash if available) towards the root tiles, steering clear of the
        avoid tiles when possible. Returns True if moved."""
        if not self.can_move:
            return False
        occ = self.occ
        roots = roots & ~occ
        if roots.is_empty() or roots.is_set(self.pos):
            return False
        walls = self.world.block | occ
        field = DistanceField()
        here = None
        if avoid is not None and not avoid.is_empty():
            soft = walls | (avoid & ~roots)
            soft.set(self.pos, False)
            field.compute(soft, roots, Bitboard())
            here = field.get(self.pos)
        if here is None or here >= W.UNREACHED:
            field.compute(walls, roots, Bitboard())
            here = field.get(self.pos)
        if here is None or here >= W.UNREACHED:
            return False
        me = self.me
        # Dash two tiles along the path first when it is ready and the goal is far.
        if allow_dash and here >= 3 and self.can_cast and self.dash_slot is not None:
            ab = self.abilities[self.dash_slot]
            if ab.cooldown() == 0:
                d1 = field.next_move_from(self.pos)
                if d1 is not None:
                    p1 = self.pos + d1
                    d2 = field.next_move_from(p1)
                    if d2 is not None:
                        p2 = p1 + d2
                        try:
                            if ab.use(p2):
                                self.pos = p2
                                self.can_cast = False
                                here = field.get(p2)
                                if here is None or here == 0:
                                    return True
                        except Error:
                            pass
        step = field.next_move_from(self.pos)
        if step is None:
            return False
        dest = self.pos + step
        try:
            ok = me.move_absolute(dest)
        except Error:
            return False
        if ok:
            self.pos = dest
            self.can_move = False
            if self.ranged:
                self.can_attack = False
        return ok

    # ------------------------------------------------------------------ turn
    def turn(self):
        self.act = "?"
        self._turn()
        if DEBUG:
            acts = self.acts
            acts[self.act] = acts.get(self.act, 0) + 1
            if self.now % 100 == 0:
                self.log("ACTS " + " ".join(f"{k}={v}" for k, v in sorted(acts.items())))

    def _turn(self):
        me = self.me
        self.now = cambc.round_number()
        if self.slot == 0 and self.now % 25 == 0:
            print(f"STAT {self.now} {cambc.global_submitted_gems(Team.ALLY)} {cambc.global_submitted_gems(Team.ENEMY)}")
        st = self.read_state()
        if not st & ST_ALIVE:
            if self.target is not None:
                self.target = None
                self.claim(None)
            self.shop(True)
            self.act = "dead"
            return
        if st & (ST_RECALL | ST_SUBMIT | ST_TP):
            self.act = "recall" if st & ST_RECALL else ("submit" if st & ST_SUBMIT else "tp")
            return
        world = self.world
        self.pos = me.position()
        self.hp = me.health()
        self.max_hp = me.max_health()
        self.gems = me.gem_count()
        self.gold = me.gold_count()
        prof = PROFILE[self.kind]
        self.strength_now = me.strength()
        self.focus_now = me.focus()
        self.dps_now = self.strength_now * prof[0] + self.focus_now * prof[1]
        self.at_spawn = world.my_spawn.is_set(self.pos)
        self.dash_slot = None
        for i in (0, 1):
            if self.ab_kind[i] == K_DASH:
                self.dash_slot = i
        if self.at_spawn or self.remote_shop:
            self.shop(False)
        self.occ = self.occupancy()
        self.enemies = cambc.champions(Team.ENEMY)
        self.allies = [a for a in cambc.champions(Team.ALLY) if int(a) != self.handle]
        self.camps = vision.camps()
        self.update_knowledge()

        if DEBUG and self.hp < 0.3 * self.max_hp:
            g = self.target
            cs = " ".join(f"{cambc.CampType.to_string(c.kind())[9:13]}@{c.position().x},{c.position().y}:{c.health():.0f}"
                          for c in self.camps if cheb(c.position(), self.pos) <= 4)
            self.log(f"LOW hp={self.hp:.0f} pos={self.pos.x},{self.pos.y} target={g.idx if g else None} "
                     f"need={self.target_need} wait={self.wait_turns} camps[{cs}] enemies={len(self.enemies)} "
                     f"last={self.last_hp}")
        if DEBUG and self.now % 50 == 0:
            g = self.target
            self.log(f"pos={self.pos.x},{self.pos.y} hp={self.hp:.0f}/{self.max_hp:.0f} gems={self.gems} "
                     f"gold={self.gold} target={g.idx if g else None} st={g.status if g else None} "
                     f"fuel={cambc.fuel_remaining()}")
        if self.enemies and self.fight():
            self.act = "fight"
            return
        if self.maybe_recall():
            self.act = "go_recall"
            return
        if self.gems > 0 and self.want_tribute():
            self.act = "to_altar"
            self.tribute()
            return
        self.act = "farm"
        self.farm()

    # ------------------------------------------------------------------ shop
    def shop(self, dead):
        me = self.me
        gold = me.gold_count()
        if gold < 30:
            return
        counts = None
        while self.build_done < len(self.build) and gold >= 30:
            fam, stat, need = self.build[self.build_done]
            shard, emblem = SHARD[(fam, stat)]
            if counts is None:
                counts = me.item_count()
            owned = counts[shard] + 5 * counts[emblem]
            if owned >= need:
                self.build_done += 1
                continue
            n = min(need - owned, gold // 30)
            try:
                me.buy(shard, n)
            except Error as e:
                self.log("buy failed", e)
                self.build_done += 1
                continue
            gold -= 30 * n
            counts = me.item_count()
            if DEBUG:
                self.log(f"BUY {shard!r} x{n} -> str={me.strength():.1f} foc={me.focus():.1f} "
                         f"maxhp={me.max_health():.0f} items={[(i, c) for i, c in enumerate(counts) if c]}")

    # ------------------------------------------------------------------ knowledge
    def update_knowledge(self):
        now = self.now
        cg = self.world.camp_group
        seen = set()
        info = []
        awake = set()
        for c in self.camps:
            h = int(c)
            g = cg.get(h)
            if g is None:
                continue
            hp = c.health()
            k = c.kind()
            p = c.position()
            info.append((c, g, k, p, hp))
            g.hp[h] = hp
            if hp < W.CAMP_HP[k]:
                awake.add(g.idx)
            if g.status != W.ALIVE:
                g.status = W.ALIVE
            g.seen = now
            seen.add(g.idx)
        self.camp_info = info
        self.awake = awake
        # Tiles within range of awake, damaging camps (per group, so a target's own zone can be excluded).
        zones = {}
        for c, g, k, p, hp in info:
            if g.idx in awake and W.CAMP_STR[k] > 0:
                z = zones.get(g.idx)
                if z is None:
                    z = zones[g.idx] = Bitboard()
                z.draw_chebyshev(p, 3)
        self.zones = zones
        vis = None
        for g in self.world.groups:
            if g.status == W.RESPAWN and now >= g.alive_at:
                g.status = W.ALIVE
                g.hp = {}
            if g.idx in seen or cheb(g.anchor, self.pos) > 9:
                continue
            if vis is None:
                vis = vision.visible_tiles()
            if (vis & g.tiles).is_empty():
                continue
            # The group's tiles are in view but none of its camps are: it was cleared.
            try:
                state = g.obj.state()
            except Error:
                continue
            g.seen = now
            if isinstance(state, game_map.CampGroupRespawning):
                g.status = W.RESPAWN
                g.alive_at = now + state.timer
                g.hp = {}
            elif isinstance(state, game_map.CampGroupRewardAvailable):
                g.status = W.REWARD
            else:
                g.status = W.ALIVE

    # ------------------------------------------------------------------ combat
    def fight(self):
        """Decide whether to engage, hold or retreat from visible enemy champions."""
        pos = self.pos
        near = []
        for e in self.enemies:
            try:
                ep = e.position()
            except Error:
                continue
            d = cheb(ep, pos)
            if d > 9:
                continue
            try:
                kind = e.champion_name()
                hp = e.health()
                prof = PROFILE[kind]
                dps = e.strength() * prof[0] + e.focus() * prof[1]
                gems = e.gem_count()
            except Error:
                continue
            near.append((e, ep, hp, prof[2], dps, d, gems))
        if not near:
            return False
        world = self.world
        our_hp = self.hp
        our_dps = self.dps_now
        for a in self.allies:
            try:
                ap = a.position()
                if cheb(ap, pos) > 7:
                    continue
                our_hp += a.health()
                prof = PROFILE[a.champion_name()]
                our_dps += a.strength() * prof[0] + a.focus() * prof[1]
            except Error:
                pass
        their_hp = 0.0
        their_dps = 0.0
        for x in near:
            w = 1.0 if x[5] <= 7 else 0.5
            their_hp += w * x[2]
            their_dps += w * x[4]
        ratio = (our_hp * our_dps) / max(1.0, their_hp * their_dps)
        home = world.spawn_field().get(pos)
        if home is not None and home <= 6:
            ratio *= 1.4
        if cheb(pos, world.enemy_spawn_center) <= 7:
            ratio *= 0.6
        closest = min(x[5] - x[3] for x in near)  # how soon someone can hit me
        frac = self.hp / self.max_hp
        if DEBUG:
            self.log(f"FIGHT ratio={ratio:.2f} me={self.hp:.0f}/{self.max_hp:.0f} gems={self.gems} "
                     f"ours={our_hp:.0f}x{our_dps:.0f} theirs={their_hp:.0f}x{their_dps:.0f} "
                     f"enemies={[(CT.to_string(x[0].champion_name())[13:17], x[5], int(x[2]), x[6]) for x in near]}")
        # Finish anything we can kill right now: kills steal carried gems.
        burst = self.burst()
        for x in near:
            if x[5] <= self.rng and x[2] <= burst:
                self.basic_attack(x[0])
                self.use_reset(x[0])
                self.cast_offense(x[0], x[1], champion=True)
                return True
        cautious = self.gems >= 20
        retreat_at = 1.1 if cautious else 0.9
        engage_at = 1.6 if cautious else 1.3
        if ratio < retreat_at or (frac < 0.25 and closest <= 2):
            in_range = [x for x in near if x[5] <= self.rng]
            if in_range and not self.ranged and self.can_attack:
                self.basic_attack(min(in_range, key=lambda x: x[2])[0])
            self.retreat(near)
            return True
        # Pick the most valuable target: low health, carrying gems, already in range.
        best = near[0]
        best_v = -1.0
        for x in near:
            v = (100.0 + 2.0 * x[6]) / (x[2] + 50.0)
            if x[5] <= self.rng:
                v *= 2.0
            v /= 1.0 + 0.1 * x[5]
            if v > best_v:
                best_v = v
                best = x
        e, ep, d = best[0], best[1], best[5]
        engage = ratio >= engage_at
        if d <= self.rng:
            self.basic_attack(e)
            self.use_reset(e)
            self.cast_offense(e, ep, champion=True)
            return True
        if self.cast_offense(e, ep, champion=True) and not engage:
            return True
        if engage and d <= 5 and cheb(ep, world.enemy_spawn_center) > 3:
            roots = Bitboard()
            roots.draw_chebyshev(ep, self.rng)
            self.go(roots, allow_dash=True)
            if cheb(ep, self.pos) <= self.rng:
                self.basic_attack(e)
                self.use_reset(e)
            return True
        if not engage and closest <= 2:
            # Even fight and they are about to reach us: hold position near allies rather than walk into them.
            return True
        return False

    def burst(self):
        """Damage this champion can deal this turn with a basic attack and a ready damage ability."""
        total = self.strength_now if self.can_attack else 0.0
        if self.can_cast:
            for i in (0, 1):
                k = self.ab_kind[i]
                if k in (K_DAMAGE, K_AOE, K_CC) and self.abilities[i].cooldown() == 0:
                    total += self.focus_now * getattr(self.ab_info[i], "modifier", 0.0)
                    break
                if k == K_RESET and self.can_attack and self.abilities[i].cooldown() == 0:
                    total += self.strength_now
                    break
        return total

    def retreat(self, near):
        if self.at_spawn:
            return
        world = self.world
        far = min(x[5] for x in near)
        if far >= 6 and self.can_cast:
            sd = world.spawn_field().get(self.pos)
            if sd is not None and sd > 8:
                try:
                    self.me.recall()
                    self.target = None
                    self.claim(None)
                    return
                except Error:
                    pass
        zone = Bitboard()
        for x in near:
            zone.draw_chebyshev(x[1], x[3] + 1)
        self.go(world.my_spawn, allow_dash=True, avoid=zone)

    def basic_attack(self, unit):
        if not self.can_attack:
            return False
        try:
            self.me.attack(unit)
        except Error:
            return False
        self.can_attack = False
        if self.ranged:
            self.can_move = False
        return True

    def use_reset(self, unit):
        for i in (0, 1):
            if self.ab_kind[i] == K_RESET and self.can_cast and not self.can_attack:
                ab = self.abilities[i]
                if ab.cooldown() == 0:
                    try:
                        if not unit.is_visible() or unit.health() <= 0:
                            return
                        if cheb(unit.position(), self.pos) > self.rng:
                            return
                        ab.use()
                    except Error:
                        return
                    self.can_cast = False
                    self.can_attack = True
                    self.basic_attack(unit)
                    return

    def cast_offense(self, unit, upos, champion):
        """Cast damage/stun abilities at a unit in range. Returns True if something was cast."""
        if not self.can_cast:
            return False
        d = cheb(upos, self.pos)
        for i in (0, 1):
            k = self.ab_kind[i]
            if k not in (K_DAMAGE, K_AOE, K_CC):
                continue
            info = self.ab_info[i]
            if d > info.range:
                continue
            if info.exclusive_with_movement and not self.can_move:
                continue
            if k == K_CC and info.modifier == 0 and not champion:
                continue
            ab = self.abilities[i]
            if ab.cooldown() != 0:
                continue
            try:
                ok = ab.use(upos if k == K_AOE else unit)
            except Error:
                continue
            if ok:
                self.can_cast = False
                if info.exclusive_with_movement:
                    self.can_move = False
                return True
        return False

    def support(self):
        """Heal or shield when useful."""
        if not self.can_cast:
            return
        for i in (0, 1):
            k = self.ab_kind[i]
            ab = self.abilities[i]
            if k == K_SHIELD and self.hp < 0.85 * self.max_hp and self.taking_damage():
                if ab.cooldown() == 0:
                    try:
                        if ab.use():
                            self.can_cast = False
                            return
                    except Error:
                        pass
            elif k == K_HEAL and ab.cooldown() == 0:
                best = None
                for a in self.allies:
                    try:
                        if cheb(a.position(), self.pos) > 4:
                            continue
                        missing = a.max_health() - a.health()
                    except Error:
                        continue
                    if missing > 150 and (best is None or missing > best[1]):
                        best = (a, missing)
                if best is not None:
                    try:
                        if ab.use(best[0]):
                            self.can_cast = False
                            return
                    except Error:
                        pass

    def taking_damage(self):
        last = self.last_hp
        return last is not None and self.hp < last

    # ------------------------------------------------------------------ recall / tribute
    def maybe_recall(self):
        if self.at_spawn:
            return False
        frac = self.hp / self.max_hp
        sd = self.world.spawn_field().get(self.pos)
        if frac < 0.35 and self.taking_damage():
            # A recall would be interrupted: get out of camp range first.
            if self.escape():
                return True
            if frac < 0.3:
                self.go(self.world.my_spawn, avoid=self.danger())
                return True
        if frac < 0.3 or (self.gold >= 300 and self.gems == 0 and frac < 0.75 and not self.remote_shop):
            if sd is not None and sd <= 6:
                self.go(self.world.my_spawn)
                return True
            try:
                self.me.recall()
            except Error:
                return False
            self.target = None
            self.claim(None)
            return True
        return False

    def want_tribute(self):
        gems = self.gems
        if gems + cambc.global_submitted_gems(Team.ALLY) >= 1000:
            return True
        g = self.target
        if g is not None and g.status == W.REWARD and g.tiles.is_set(self.pos):
            return False
        d = self.world.altar_field().get(self.pos)
        if d is None or d >= W.UNREACHED:
            return False
        if gems >= 60:
            return True
        if gems >= 30 and d <= 12:
            return True
        if d <= 4:
            return True
        if self.hp < 0.4 * self.max_hp and gems >= 15:
            return True
        if self.idle_turns >= 3:
            return True
        return False

    def tribute(self):
        world = self.world
        me = self.me
        for a in world.altar_list:
            if cheb(a, self.pos) <= 1:
                try:
                    if vision.has_altar_lock(a):
                        lock = vision.altar_lock_at(a)
                        if lock.is_enemy():
                            continue
                except Error:
                    pass
                try:
                    me.submit_gems(a)
                    return
                except Error as e:
                    self.log("submit failed", e)
        self.go(world.altar_approach, avoid=self.danger())

    # ------------------------------------------------------------------ farming
    def claims(self):
        """Map group index -> list of ally slots claiming it (from shared memory). Also records ready slots."""
        out = {}
        ready = {}
        mem = cambc.shared_memory
        for i in range(min(self.n_allies, 6)):
            if i == self.slot:
                continue
            v = mem[i]
            if v != 255:
                g = v & 127
                out.setdefault(g, []).append(i)
                if v & 128:
                    ready[g] = ready.get(g, 0) + 1
        self.ready = ready
        return out

    def claim(self, g, ready=False):
        try:
            cambc.shared_memory[self.slot] = 255 if g is None else (g.idx | (128 if ready else 0))
        except Exception:
            pass

    def my_dps(self):
        me = self.me
        dps = me.strength()
        for i in (0, 1):
            k = self.ab_kind[i]
            if k == K_DAMAGE or k == K_AOE or (k == K_CC and self.ab_info[i].modifier > 0):
                dps += me.focus() * self.ab_info[i].modifier / 8
            elif k == K_RESET:
                dps += me.strength() / 8
        return dps

    def required(self, g, hp_left, dps):
        """Champions needed so the camp's total damage stays under ~55% of the attackers' health."""
        if g.dps == 0:
            return 1
        hp = self.max_hp
        for k in range(1, self.n_allies + 1):
            t = hp_left / (k * dps)
            if g.dps * t <= 0.55 * k * hp:
                return k
        return 99

    def choose_target(self, exclude=None):
        world = self.world
        now = self.now
        field = DistanceField()
        roots = Bitboard()
        roots.set(self.pos)
        field.compute(world.block, roots, Bitboard())
        claims = self.claims()
        dps = self.my_dps()
        gold_w = 0.3 * max(0.15, 1.0 - now / 1200)
        best = None
        best_score = 0.0
        best_need = 1
        current = self.target
        for g in world.groups:
            if g is exclude or g.near_altar >= W.UNREACHED:
                continue
            d = field.get(g.anchor)
            if d is None or d >= W.UNREACHED:
                continue
            wait = 0
            if g.status == W.RESPAWN:
                wait = g.alive_at - now - d
                if wait > 25:
                    continue
                if wait < 0:
                    wait = 0
            slots = claims.get(g.idx, ())
            others = len(slots)
            if g.status == W.REWARD:
                hp_left = 0
                need = 1
            else:
                hp_left = g.hp_left() if g.status == W.ALIVE else g.hp_max
                need = self.required(g, hp_left, dps)
                if need > self.n_allies:
                    continue
            k = others + 1
            if k < need:
                k = need
            t_kill = hp_left / (k * dps)
            # Team champion-rounds spent: everyone involved walks and fights, one captures and tributes.
            cost = k * (d + wait + t_kill) + 5 + 0.5 * g.near_altar + g.gems / 10
            if others + 1 < need:
                cost += 4 * (need - others - 1)  # waiting for help to arrive
            value = g.gems + gold_w * g.gold
            if others >= need:
                value *= 0.5  # surplus helper
            elif need > 1 and others and min(slots) < self.slot:
                value *= 1.2  # fill a squad someone already started
            if cheb(g.anchor, world.enemy_spawn_center) < cheb(g.anchor, world.spawn_center):
                value *= 0.85
            if g is current:
                value *= 1.1
            score = value / (cost + 5)
            if SEED:
                score *= 0.98 + 0.04 * (((SEED * 2654435761 + g.idx * 40503 + self.slot * 9973 + now // 50 * 7919)
                                         % 1000) / 1000.0)
            if score > best_score:
                best_score = score
                best = g
                best_need = need
        self.target_need = best_need
        return best

    def allies_near(self, p, r):
        n = 0
        for a in self.allies:
            try:
                if cheb(a.position(), p) <= r:
                    n += 1
            except Error:
                pass
        return n

    def farm(self):
        g = self.target
        if g is not None and (g.status == W.RESPAWN or self.now - self.target_round >= 8):
            g = self.choose_target()
            self.target_round = self.now
        elif g is None:
            g = self.choose_target()
            self.target_round = self.now
        if g is not self.target:
            self.wait_turns = 0
        self.target = g
        self.claim(g)
        if g is None:
            self.act = "idle"
            self.idle_turns += 1
            if self.gems > 0:
                self.tribute()
            else:
                self.go(self.world.altar_approach)
            return
        self.idle_turns = 0
        self.support()
        if self.world.all_camp_tiles.is_set(self.pos) and not (g.status == W.REWARD and g.tiles.is_set(self.pos)):
            self.step_off()
        alive = []
        for c in self.camps:
            if self.world.camp_group.get(int(c)) is g:
                alive.append(c)
        if alive:
            self.act = "camp"
            self.attack_group(g, alive)
            return
        if g.status == W.REWARD:
            if g.tiles.is_set(self.pos):
                self.act = "capture"
                return  # capturing
            # Someone else of ours is already capturing it: move on.
            for a in self.allies:
                try:
                    if g.tiles.is_set(a.position()):
                        self.target = self.choose_target(exclude=g)
                        self.claim(self.target)
                        return
                except Error:
                    pass
            free = g.tiles & ~self.occ
            if free.is_empty():
                self.target = None
                return
            self.go(free)
            return
        # Not in view yet (or hidden in bushes): walk towards it.
        roots = Bitboard()
        for c in g.cells:
            roots.draw_chebyshev(c, 1)
        roots &= ~(self.world.block | self.world.all_camp_tiles)
        if not self.go(roots, avoid=self.danger(exclude=g)) and cheb(g.anchor, self.pos) <= 2:
            g.status = W.ALIVE

    def attack_group(self, g, alive):
        pos = self.pos
        best = None
        awake = False
        for c in alive:
            try:
                cp = c.position()
                hp = c.health()
            except Error:
                continue
            if hp < W.CAMP_HP[c.kind()]:
                awake = True
            key = (hp, cheb(cp, pos))
            if best is None or key < best[0]:
                best = (key, c, cp)
        if best is None:
            return
        _, camp, cp = best
        d = cheb(cp, pos)
        need = getattr(self, "target_need", 1)
        if need > 1 and not awake:
            # Wait just outside camp range until enough allies have gathered.
            self.claims()
            present = max(self.ready.get(g.idx, 0), self.allies_near(cp, 5)) + 1
            if present < need and self.wait_turns < 25:
                self.wait_turns += 1
                self.act = "wait"
                self.claim(g, ready=d <= 6)
                self.cast_offense(camp, cp, champion=False)
                if d <= 3:
                    self.step_away(cp, 4)
                elif d > 4:
                    roots = Bitboard()
                    roots.draw_chebyshev(cp, 4)
                    inner = Bitboard()
                    inner.draw_chebyshev(cp, 3)
                    roots &= ~(inner | self.world.block | self.world.all_camp_tiles)
                    self.go(roots)
                return
        self.wait_turns = 0
        self.claim(g, ready=True)
        if self.hp < 0.35 * self.max_hp and self.taking_damage() and (g.dps > 0 or self.zones):
            if self.ranged and d <= 4:
                self.cast_offense(camp, cp, champion=False)
            if not self.escape():
                self.step_away(cp, 4)
            return
        if d <= self.rng:
            self.basic_attack(camp)
            self.use_reset(camp)
            self.cast_offense(camp, cp, champion=False)
            return
        self.cast_offense(camp, cp, champion=False)
        roots = Bitboard()
        roots.draw_chebyshev(cp, self.rng)
        if self.ranged:
            inner = Bitboard()
            inner.draw_chebyshev(cp, self.rng - 1)
            ring = roots & ~(inner | self.world.block | self.world.all_camp_tiles)
            if not ring.is_empty():
                roots = ring
        roots &= ~self.world.block
        self.go(roots, avoid=self.danger(exclude=g))
        if cheb(cp, self.pos) <= self.rng:
            self.basic_attack(camp)
            self.use_reset(camp)

    def danger(self, exclude=None):
        """Tiles in range of awake camps, except those of the excluded group."""
        out = None
        for idx, z in self.zones.items():
            if exclude is not None and idx == exclude.idx:
                continue
            out = z.copy() if out is None else (out | z)
        return out

    def escape(self):
        """Get out of range of every awake camp (used when hurt)."""
        d = self.danger()
        if d is None or not d.is_set(self.pos):
            return False
        roots = Bitboard()
        roots.draw_chebyshev(self.pos, 8)
        roots &= ~(d | self.world.block | self.world.all_camp_tiles)
        return self.go(roots, allow_dash=True)

    def step_off(self):
        """Leave a camp spawn tile so the group can respawn."""
        roots = Bitboard()
        roots.draw_chebyshev(self.pos, 2)
        roots &= ~(self.world.block | self.world.all_camp_tiles)
        self.go(roots, allow_dash=False)

    def step_away(self, danger_pos, dist):
        """Move to a tile at least dist from danger_pos."""
        roots = Bitboard()
        roots.draw_chebyshev(self.pos, 3)
        inner = Bitboard()
        inner.draw_chebyshev(danger_pos, dist - 1)
        roots &= ~(inner | self.world.block | self.world.all_camp_tiles)
        self.go(roots, allow_dash=False)

    def end(self):
        try:
            self.last_hp = self.me.health()
        except Error:
            pass
