"""Champion brain: shop, fight, tribute, farm. One instance per champion."""
import cambc
from cambc import game_map, vision, Vec2, Bitboard, DistanceField, Team
from cambc import ChampionType as CT, ItemType as IT, ConsumableType as CON, Error

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
             ("DURABILITY", "H", 5), ("POWER", "S", 30), ("POWER", "H", 30), ("POWER", "S", 60)]
BUILD_FOCUS = [("MONSTER", "F", 5), ("POWER", "F", 5), ("JUNGLE", "H", 5), ("POWER", "F", 10),
               ("DURABILITY", "H", 5), ("POWER", "F", 30), ("POWER", "H", 30), ("POWER", "F", 60)]
BUILD_TANK = [("JUNGLE", "H", 5), ("MONSTER", "S", 5), ("POWER", "S", 5), ("POWER", "S", 10),
              ("DURABILITY", "H", 5), ("POWER", "S", 30), ("POWER", "H", 30), ("POWER", "S", 60)]
FOCUS_CHAMPS = (CT.STELLAR, CT.PRISM, CT.CASSI)
PAIR = (CT.CASSI, CT.ISSAC)
TANK_CHAMPS = (CT.RYTH, CT.VARG, CT.MARCELLA)
# Tanks (Ryth, Varg, Marcella) buy the Jungle health emblem (30% less camp damage) first.
TANK_JUNGLE_FIRST = False
# Count camp damage at 70% when sizing squads once this champion owns a Jungle emblem.
JUNGLE_AWARE = False
JUNGLE_EMBLEMS = (IT.JUNGLE_EMBLEM_OF_STRENGTH, IT.JUNGLE_EMBLEM_OF_FOCUS, IT.JUNGLE_EMBLEM_OF_HEALTH)

DEBUG = True
# Testing only: a non-zero SEED perturbs target scores by up to 2% so repeated matches diverge.
SEED = 0
# Minimum champions sent to any camp group (1 = spread out; 2 = pairs; 99 = whole team).
MIN_SQUAD = 1
RETARGET_EVERY = 8
# A camp group needs enough champions that its damage over the fight stays under this share of their health.
NEED_FRAC = 0.55
# Turns a champion waits outside camp range for the rest of a squad before attacking anyway.
WAIT_LIMIT = 40
# Target scoring: weight of a camp's gold relative to its gems (fades to 15% of this by GOLD_TAPER; 0.4 by 500 adopted in v7),
# and the value multiplier for camps closer to the enemy spawn than ours.
GOLD_WEIGHT = 0.4
ENEMY_SIDE = 0.85
# Fight thresholds on the strength ratio (ours/theirs): retreat below, engage (chase) at or above.
# Champions carrying 20+ gems add FIGHT_GEM_EXTRA to both (more cautious).
FIGHT_RETREAT = 0.9
FIGHT_ENGAGE = 1.3
FIGHT_GEM_EXTRA = 0.25
# Allies within this many tiles count on our side of the fight ratio (platform deaths: 72% had an ally within 6
# tiles yet still died, so far allies may not really be fighting).
ALLY_RANGE = 7
# Retreat whatever the ratio below this health fraction when an enemy could hit us within LOW_HP_REACH moves
# (stuns reach 4 tiles; 49% of our platform champion deaths had a single attacker).
LOW_HP_RETREAT = 0.25
LOW_HP_REACH = 2
# Ranged champions cast before their basic attack. Their attack uses the movement allowance, and casting
# after it skipped every walking-exclusive ability (Tavi's 2.2x stun): our Tavi cast at camps 0.09 times per
# basic attack, pros' ranged champions 0.18-0.25 (experiment 116).
CAST_FIRST = True
# Cast a self-shield (Varg) during fights when an enemy champion can hit us next turn or we are losing health.
# support() only ran while farming, so Varg shielded 0.10 times per basic attack vs strong teams' 0.18.
FIGHT_SHIELD = True
# Don't start a recall (it takes 5 turns, and damage cancels it) within this many rounds of seeing an enemy champion
# within 10 tiles: walk home instead. Debug logs vs v8 showed recalls begun 6-8 tiles from a chaser that were
# interrupted and ended in death (0 = v8: only this turn's sightings, retreat recalls at 8+ tiles and when stuck).
RECALL_SAFE = 0
# Fight on the lowest strength ratio seen in the last FIGHT_MEMO rounds (0 = this turn's only). Debug logs vs v8:
# Ryth chasing a lone Tavi flipped between 6.4 (an ally 7 tiles back counted) and 0.2 (one step on, it wasn't)
# every turn, so it neither closed in nor got away and lost 1,000 health to free shots.
FIGHT_MEMO = 0
# Against enemy champions in reach, cast a stun (Ryth's area stun, Tavi's damage-and-stun) before the basic attack.
# hit() spent the one cast per turn on the attack reset, so Ryth and Tavi never stunned a champion they could hit.
CC_FIRST = False
# Lower the engage threshold by this much when the best target carries 40+ gems (0 = off).
GEM_HUNT = 0.0
# Stand-off breaker: after this many turns facing enemies within 9 tiles with nobody on either side losing
# health, keep away from them for AVOID_ROUNDS (farm and tribute elsewhere) unless they close in (0 = off).
STANDOFF_TURNS = 0
AVOID_ROUNDS = 40
# Ignore enemy champions standing inside their own spawn region unless something is hurting us: we can't
# reach them there, and on maps whose spawns touch (rushbait-v2) they kept us "retreating" at spawn forever.
IGNORE_SPAWN_CAMPERS = True
# Poke camp groups too strong to fight (monoliths: 20,000 HP, 200 damage) from range 4 with damaging abilities,
# outside their range-3 reach. Only champions with a damaging ability do it, when it scores best.
MONOLITH_POKE = False
# Poke fix: rebuild the poke ring each turn from the live camps in view (the cached ring kept pokers on tiles next to
# dead camps forever: on stampede Tavi stood still for hundreds of turns) and aim area casts at the in-range tile
# covering the most live camps.
POKE_LIVE_RING = True
# Capture step for poked groups: once the champions near the group can finish it safely (squad sizing on what is
# left), or enemies come near a group below POKE_CLOSE_FRAC of its health, fight it like any other target so we
# stand on its tiles when it dies. Without it the opponent walked in, finished our poked monoliths and captured.
POKE_CLOSE = True
POKE_CLOSE_FRAC = 0.3
# Stop poking a group for this many rounds after seeing an enemy champion within 8 tiles of it (0 = off): the shop-only
# probe won contest 5/8 against v10, the poking candidates 0/8 (the opponent finished and captured what we poked).
POKE_AVOID_ENEMY = 0
# Melee champions that kill a group's last camp step onto its spawn tile in the same turn (capture in place).
CLAIM_ON_KILL = True
# Pokers publish the poked group's remaining health in shared memory bytes 6-7 (free with up to 6 champions);
# vision isn't shared, so otherwise the rest of the team sizes its squad on a full-health boss and never comes.
POKE_SHARE = True
# Run the stand-off breaker (STANDOFF_TURNS) only while our team's tributed gems have stayed flat for this many
# rounds (0 = whenever STANDOFF_TURNS is on). Experiment 76's always-on breaker fired too often.
TEAM_STALL_ROUNDS = 0
# Melee approach avoids camp spawn tiles: on contest Vendetta stepped onto a dead camp's spawn tile next to its
# target, step_off() moved it back next turn, and it repeated that for 1,700+ turns.
CAMP_TILE_FIX = True
# Put our ward (free, one each, relocatable every turn, 6-tile vision) on the bush tile within 2 nearest our target,
# as strong platform teams do: 71% of their wards sit in bushes, near camps and altars (experiment 97).
WARDS = True
# Skip the Monster emblem: buy Power (six shards' worth, no passive) first, like strong teams' builds.
POWER_FIRST = False
# Gold's weight in target scoring fades linearly to 15% of GOLD_WEIGHT at this round.
GOLD_TAPER = 500
# Platform telemetry with DEBUG off: "T DIED" per death and "T ACTS" activity counts every 250 rounds.
# Printing only, so decisions are unchanged.
TELEMETRY = False
# Tribute thresholds: carried gems that send a champion to any altar / to an altar within 12 tiles.
TRIBUTE_BIG = 30
TRIBUTE_MID = 15
# Before this round every champion farms the group claimed by the lowest-slot ally (pack farming, as the strong
# platform teams do: 76% of their early camp hits come from 3+ champions on one group); 0 = off.
PACK_UNTIL = 150
# Pack farming only when we drafted the pro roster (Cassi & Issac or Stellar): with our draft it lost 8/32 on
# the 3-pick maps (fragment 0/8).
PACK_PRO_ONLY = True
# After seeing an enemy nearby, use the lower thresholds for this many rounds (0 = off).
CAUTION_WINDOW = 0
HOLD_TARGET_IN_FIGHT = False
# Carry an altar lock (10 gold) and drop it on any unlocked altar we pass: blocks enemy tributes there.
ALTAR_LOCKS = True
# Walk up to this many tiles out of the way to place a carried lock (0 = only place when passing).
LOCK_DETOUR = 0
# Use recall as fast travel when a target/altar is much closer to our spawn than to us.
RECALL_TRAVEL = True
RECALL_TURNS = 5
# Shopping trips: recall with this much gold (when below SHOP_HP health), or walk home when spawn is close.
SHOP_GOLD = 150
SHOP_HP = 1.01
# Skip a shopping recall (not a low-health one) while taking damage, next to an enemy or in an awake camp's reach.
SHOP_SAFE = True
SHOP_NEAR = 0
SHOP_NEAR_GOLD = 9999
# Raise the shopping threshold by this much gold per tile of walk from spawn back to where we are (the trip's cost):
# on ambush the nearest camps are ~40 tiles out, so each 150-gold trip cost ~45 turns (0 = off).
SHOP_TRIP = 0
# Long walks to a target follow its cached static field (World.walk_field) when nothing needs avoiding and the next
# tile is free, instead of computing a fresh field every turn: on ambush (100x100) that field cost ~0.5M of the 2.5M
# per-turn fuel, and the heaviest turns reached 2.48M.
FAST_WALK = False
# Target scoring reads each group's distance from its cached walk field (one missing field is built per turn while at
# least FAST_FUEL fuel is left) instead of a fresh field from our tile every re-target (~0.56M on ambush).
FAST_SCORE = False
FAST_FUEL = 1200000
# Size squads for a new target on our current health, not our maximum: Cassi (400/700) and Issac (300/900) joined an
# elk pair and died together. The group we are already fighting keeps the maximum, so nobody abandons a half-dead group.
HP_AWARE = False
# Pack farming: cost the walk for every champion (they all follow the lead). The lead costed it for `need`
# champions only, so on pilgrimage the whole team of six walked 63 tiles to the enemy side's group as one unit.
PACK_WALK_ALL = False
# Packs sized by need: before PACK_UNTIL a champion joins the lead's group only while fewer allies than the group needs
# already claim it; otherwise it scores targets as usual, claims included. Six champions on one wolf was overkill,
# and the whole team walking as one unit farmed one group at a time.
PACK_NEED = False
# Stun camps: Cassi's stun (no damage) and the damaging stuns (Tavi, Ren, Prism) go on the strongest awake camp that
# can hit one of us next round. A stunned camp skips its next attack (probe: a wolf pair hit Issac for 20 instead of
# 40 on the round after each stun); the bot never cast Cassi's stun at camps. A camp whose stun buff still has
# duration 2 will skip its next attack already, so it isn't stunned again (duration 1: that skip has happened).
STUN_CAMPS = False
# Also aim the damaging stuns (Tavi, Ren, Prism) at that camp instead of the one being focused (off: their damage
# helps finish the lowest camp, and a dead camp stops attacking for good while a stun buys one round).
STUN_DAMAGING = False
# Track which camps of a partly seen group are dead (spawn tile in view, camp gone) and size squads on the live
# camps' damage: a group whose elks are dead no longer needs the squad its full strength did.
LIVE_DPS = False
# Poke cost counts area casts by the camps they hit (Group.aoe_cov): the single-target estimate rated Stellar's
# poke on stampede's 3x4 block of elks and gem clusters at a third of its real rate.
AOE_POKE = False
# Cassi & Issac die together (94% of strong teams draft them): in the fight ratio the pair counts with the weaker
# one's health, and a target in the pair is worth both bodies and both bags.
PAIR_KILL = False
# Melee champions only target camps they can stand next to: Varg's splash choice (the most crowded camp) picked
# monolith's Monolith, boxed in by its 8 gem clusters, and walked nowhere for the rest of the game.
MELEE_REACH = False
# Once the squad wait has run out, it stays out until the target changes: the old code reset the count on the
# turn it expired, so a champion whose attack didn't wake the group waited another 40 turns, again and again.
WAIT_FIX = False
# Poking: only damaging camps' reach counts (gem and gold clusters never attack), single-target casts go to the
# damaging camps (they decide when the group can be tanked), and between casts a ranged poker basic-attacks camps
# it can hit from outside that reach, standing where it can.
POKE_SMART = False
# Share of the estimated poke damage counted in the poke's cost (positioning, cooldown gaps and camps dying make real
# pokes slower than focus x modifiers; 1.0 = the estimate as is).
POKE_EFF = 1.0
# When the basic attack kills a camp, spend the attack reset on another live camp in range at once: Vendetta's kill
# passive refreshes her cooldowns, which is wasted if the reset was still unused.
RESET_RETARGET = False
# A group counts as awake only if one of its camps lost health in the last 2 rounds (not whenever one is below full
# health). WRONG, keep off: a probe showed camps keep attacking a champion that stays in range after a single hit
# (a wolf pair hit Ryth for 40 a round for 12+ rounds after one attack), so a damaged camp stays dangerous while anyone
# is near it; with this on, Stellar tributed in an elk's reach, couldn't "escape" an unlisted zone and died.
AWAKE_RECENT = False
# With AWAKE_RECENT, also hold the squad wait until someone of ours is in the group's reach. Off, the wait ends once a
# camp is below full health, as before: a waiting caster's poke ends it, and casters then fight alone (in a trace the
# strict wait tripled the turns spent waiting, 3-4% -> 9-13%; WAIT_LIMIT 40 was tuned with the old behaviour).
WAIT_STRICT = False

DIRS =(Vec2(1, 0), Vec2(-1, 0), Vec2(0, 1), Vec2(0, -1), Vec2(1, 1), Vec2(1, -1), Vec2(-1, 1), Vec2(-1, -1))


class _Profiles(dict):
    """Champion damage profile per type: (strength multiplier, focus per turn multiplier, attack range).

    Built on first use per type (reading a champion design costs ~40k fuel)."""

    def __missing__(self, kind):
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
        value = (str_mul, foc_mul, d.base_stats().base_attack_range)
        self[kind] = value
        return value


PROFILE = _Profiles()


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
        self.world.prof.append(("world done", cambc.fuel_remaining()))
        me = cambc.me()
        self.me = me
        self.handle = int(me)
        self.kind = me.champion_name()
        stats = me.base_stats()
        self.ranged = stats.base_attack_range > 1
        self.rng = stats.base_attack_range
        allies = cambc.champions(Team.ALLY)
        handles = sorted(int(c) for c in allies)
        self.ally_handles = handles
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
        if TANK_JUNGLE_FIRST and self.kind in TANK_CHAMPS:
            self.build = BUILD_TANK
        if POWER_FIRST:
            self.build = [("POWER", stat, n) if fam == "MONSTER" else (fam, stat, n) for fam, stat, n in self.build]
        self.ward_at = None
        self.splash = me.passive() == cambc.PassiveType.SPLASH_ATTACK
        self.aoe_mod = 0.0
        self.poke_mod = 0.0  # damage per turn per point of focus from abilities that can hit camps
        for i in (0, 1):
            if self.ab_kind[i] == K_AOE:
                self.aoe_mod += getattr(self.ab_info[i], "modifier", 0.0) / 8.0
            if self.ab_kind[i] in (K_DAMAGE, K_AOE, K_CC):
                self.poke_mod += getattr(self.ab_info[i], "modifier", 0.0) / 8.0
        self.build_done = 0
        self.remote_shop = self.kind == CT.TAVI
        pro = False
        for c in allies:
            try:
                if c.champion_name() in (CT.CASSI, CT.STELLAR):
                    pro = True
            except Error:
                pass
        self.pack_until = PACK_UNTIL if pro or not PACK_PRO_ONLY else 0
        self.target = None
        self.target_round = -100
        self.mode = "farm"
        self.last_hp = None
        self.errors = 0
        self.idle_turns = 0
        self.wait_turns = 0
        self.acts = {}
        self.jungle = False
        self.history = []
        self.ratio_hist = []
        self.why = ""
        self.last_ratio = None
        self.has_lock = False
        self.locked_altars = set()
        self.altar_xy = [(a.x, a.y, a) for a in self.world.altar_list]
        self.enemy_seen = -1000
        self.standoff = 0
        self.standoff_round = -1000
        self.enemy_hp = {}
        self.avoid_until = -1
        self.avoid_zone = None
        self.avoid_pts = ()
        self.poke_rings = {}
        self.poke_enemy = {}
        self.team_gems = -1
        self.team_gems_round = 0
        self.near_n = 0
        self.tel_alive = True
        self.tel_gems = 0
        self.tel_near = 0
        self.aoe_pos = None
        self.choice_cache = None
        self.kinds = {}
        self.marks = []
        self.max_fuel = 0
        self.max_fuel_act = ""
        self.ready = {}
        self.target_need = 1
        self.world.prof.append(("bot fields", cambc.fuel_remaining()))
        # Altar distances for every group, so target choice can weigh the tribute trip.
        af = self.world.altar_field()
        self.world.prof.append(("altar field", cambc.fuel_remaining()))
        for g in self.world.groups:
            d = af.get(g.anchor)
            g.near_altar = d if d is not None else W.UNREACHED
        self.world.prof.append(("near_altar", cambc.fuel_remaining()))
        sf = self.world.spawn_field()
        self.spawn_dist = sf.export_linear_buffer()
        spawn_altar = af.get(self.world.spawn_center)
        self.spawn_altar = spawn_altar if spawn_altar is not None else W.UNREACHED
        self.target_via = False
        self.walk_fields_done = False
        if DEBUG:
            prev = None
            parts = []
            for name, f in self.world.prof:
                if prev is not None:
                    parts.append(f"{name}={prev - f}")
                prev = f
            print("INITPROF " + " ".join(parts) + f" groups={len(self.world.groups)}")

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
        self.last_ratio = None
        f0 = cambc.fuel_remaining() if DEBUG else 0
        self.near_n = 0
        self._turn()
        if WARDS and self.act not in ("dead", "recall", "submit", "tp", "?"):
            self.ward_bush()
        if TELEMETRY and not DEBUG:
            self.telemetry()
        if DEBUG:
            if self.act == "dead":
                if self.history:
                    self.log("DIED after: " + " | ".join(self.history))
                    self.history = []
            else:
                try:
                    hp = self.me.health()
                except Error:
                    hp = -1
                ne = 0
                for e in getattr(self, "enemies", ()):
                    try:
                        if cheb(e.position(), self.me.position()) <= 6:
                            ne += 1
                    except Error:
                        pass
                r = f"{self.last_ratio:.2f}" if self.last_ratio is not None else "-"
                try:
                    p = self.me.position()
                    mv = "M" if self.st & ST_MOVE else "-"
                    stun = "S" if self.me.restrictions() & 1 else ""
                except Error:
                    p, mv, stun = None, "?", ""
                where = f"{p.x},{p.y}" if p is not None else "?"
                self.history.append(f"r{self.now} {self.act} hp={hp:.0f} gems={getattr(self, 'gems', 0)} en6={ne} "
                                    f"ratio={r} at={where} {mv}{stun} {self.why}")
                self.why = ""
                if len(self.history) > 6:
                    self.history.pop(0)
            used = f0 - cambc.fuel_remaining()
            if used > 900000:
                self.log(f"HEAVY used={used} act={self.act} marks={self.marks}")
            if used > self.max_fuel:
                self.max_fuel = used
                self.max_fuel_act = self.act
            acts = self.acts
            acts[self.act] = acts.get(self.act, 0) + 1
            if self.now % 100 == 0:
                self.log("ACTS " + " ".join(f"{k}={v}" for k, v in sorted(acts.items())))
                self.log(f"FUEL max={self.max_fuel} during={self.max_fuel_act}")

    def telemetry(self):
        """Compact log for platform games, where DEBUG is off: deaths and activity counts."""
        acts = self.acts
        acts[self.act] = acts.get(self.act, 0) + 1
        name = CT.to_string(self.kind)[13:]
        if self.act == "dead":
            if self.tel_alive:
                print(f"T DIED r{self.now} {name} gems={self.tel_gems} enemies_near={self.tel_near}")
            self.tel_alive = False
        else:
            self.tel_alive = True
            self.tel_gems = getattr(self, "gems", 0)
            self.tel_near = self.near_n
        if self.now % 250 == 0:
            print(f"T ACTS r{self.now} {name} " + " ".join(f"{k}={v}" for k, v in sorted(acts.items())))

    def ward_bush(self):
        """Move our ward onto the bush tile within 2 nearest our target (bushes block sight); keep it while near."""
        pos = self.pos
        ward = self.ward_at
        if ward is not None and cheb(ward, pos) <= 4:
            return
        near = Bitboard()
        near.draw_chebyshev(pos, 2)
        near &= self.world.bushes
        if near.is_empty():
            return
        g = self.target
        focus = g.anchor if g is not None else self.world.enemy_spawn_center
        best = None
        best_d = 999
        for p in near.positions():
            d = cheb(p, focus)
            if d < best_d:
                best_d = d
                best = p
        try:
            if best is not None and self.me.place_ward(best):
                self.ward_at = best
        except Error:
            pass

    def team_stalled(self):
        """True when our team's tributed gems haven't changed for TEAM_STALL_ROUNDS rounds."""
        gems = cambc.global_submitted_gems(Team.ALLY)
        if gems != self.team_gems:
            self.team_gems = gems
            self.team_gems_round = self.now
        return self.now - self.team_gems_round >= TEAM_STALL_ROUNDS

    def mark(self, name):
        if DEBUG:
            self.marks.append((name, cambc.fuel_remaining()))

    def _turn(self):
        me = self.me
        self.marks = []
        self.mark("start")
        self.now = cambc.round_number()
        if self.slot == 0 and self.now % 25 == 0:
            print(f"STAT {self.now} {cambc.global_submitted_gems(Team.ALLY)} {cambc.global_submitted_gems(Team.ENEMY)}")
        st = self.read_state()
        if not st & ST_ALIVE:
            self.at_spawn = False
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
        if self.has_lock:
            self.place_lock()
        self.mark("gathered")
        self.update_knowledge()
        self.mark("knowledge")

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
        self.mark("fight")
        if self.gems > 0 and self.want_tribute():
            self.act = "to_altar"
            self.tribute()
            return
        self.act = "farm"
        self.farm()
        self.mark("farm")

    # ------------------------------------------------------------------ shop
    def shop(self, dead):
        me = self.me
        gold = me.gold_count()
        if ALTAR_LOCKS and gold >= 10 and (dead or self.at_spawn):
            try:
                self.has_lock = me.consumables()[CON.ALTAR_LOCK].count() > 0
                if not self.has_lock and me.can_buy(CON.ALTAR_LOCK):
                    me.buy(CON.ALTAR_LOCK)
                    self.has_lock = True
                    gold -= 10
            except Error:
                pass
        if gold < 30:
            return
        counts = None
        while self.build_done < len(self.build):
            fam, stat, need = self.build[self.build_done]
            shard, emblem = SHARD[(fam, stat)]
            if counts is None:
                counts = me.item_count()
            owned = counts[shard] + 5 * counts[emblem]
            if owned >= need:
                self.build_done += 1
                continue
            if gold < 30:
                break
            n = min(need - owned, gold // 30)
            try:
                me.buy(shard, n)
            except Error as e:
                self.log("buy failed", e)
                self.build_done += 1
                continue
            gold -= 30 * n
            counts = me.item_count()
            if not self.jungle:
                for em in JUNGLE_EMBLEMS:
                    if counts[em]:
                        self.jungle = True
            if DEBUG:
                self.log(f"BUY {shard!r} x{n} -> str={me.strength():.1f} foc={me.focus():.1f} "
                         f"maxhp={me.max_health():.0f} items={[(i, c) for i, c in enumerate(counts) if c]}")

    # ------------------------------------------------------------------ knowledge
    def update_knowledge(self):
        now = self.now
        world = self.world
        cg = world.camp_group
        camp_hp = W.CAMP_HP
        seen = set()
        info = []
        awake = set()
        damaged = set()
        for c in self.camps:
            h = c._handle
            g = cg.get(h)
            if g is None:
                continue
            hp = c.health()
            k = c._type
            info.append((c, g, k, g.cell_of[h], hp))
            if DEBUG and now % 7 == 0:
                cp = c.position()
                if cp != g.cell_of[h]:
                    self.log(f"CAMPMOVED {h} at {cp.x},{cp.y} spawn {g.cell_of[h].x},{g.cell_of[h].y} hp={hp}")
            ghp = g.hp
            old = ghp.get(h)
            if old != hp:
                if AWAKE_RECENT and hp < (camp_hp[k] if old is None else old):
                    g.hit_round = now
                ghp[h] = hp
                g.refresh_hp()
            idx = g.idx
            if hp < camp_hp[k]:
                damaged.add(idx)
                if not AWAKE_RECENT or now - g.hit_round <= 2:
                    awake.add(idx)
            g.status = W.ALIVE
            g.seen = now
            seen.add(idx)
        self.camp_info = info
        self.awake = awake
        self.damaged = damaged
        vis = None
        if LIVE_DPS and info:
            # Camps of a group in view whose spawn tile is visible but which aren't there are dead.
            live = {x[0]._handle for x in info}
            for g in {x[1] for x in info}:
                ghp = g.hp
                for h, cell in zip(g.handles, g.cells):
                    if h in live or ghp.get(h) == 0:
                        continue
                    if vis is None:
                        vis = vision.visible_tiles()
                    if vis.is_set(cell):
                        ghp[h] = 0
                        g.refresh_hp()
        if POKE_SHARE and MONOLITH_POKE:
            self.read_poke(seen)
        # Tiles within range of awake, damaging camps (per group, so a target's own zone can be excluded).
        zones = {}
        if awake:
            camp_str = W.CAMP_STR
            for c, g, k, p, hp in info:
                if g.idx in awake and camp_str[k] > 0:
                    z = zones.get(g.idx)
                    if z is None:
                        z = zones[g.idx] = Bitboard()
                    z.draw_chebyshev(p, 3)
        self.zones = zones
        # Groups in view whose camps are not: cleared (reward waiting) or respawning.
        px = self.pos.x
        py = self.pos.y
        bx = px // 10
        by = py // 10
        buckets = world.buckets
        for gx in (bx - 1, bx, bx + 1):
            for gy in (by - 1, by, by + 1):
                lst = buckets.get((gx, gy))
                if not lst:
                    continue
                for g in lst:
                    if g.idx in seen:
                        continue
                    dx = g.ax - px
                    dy = g.ay - py
                    if dx > 9 or dx < -9 or dy > 9 or dy < -9:
                        continue
                    if g.status == W.RESPAWN and now < g.alive_at - 2:
                        continue  # we already know when it comes back
                    if vis is None:
                        vis = vision.visible_tiles()
                    if (vis & g.tiles).is_empty():
                        continue
                    try:
                        state = g.obj.state()
                    except Error:
                        continue
                    g.seen = now
                    if isinstance(state, game_map.CampGroupRespawning):
                        g.status = W.RESPAWN
                        g.alive_at = now + state.timer
                        g.reset_hp()
                    elif isinstance(state, game_map.CampGroupRewardAvailable):
                        g.status = W.REWARD
                    else:
                        g.status = W.ALIVE

    # ------------------------------------------------------------------ combat
    def fight(self):
        """Decide whether to engage, hold or retreat from visible enemy champions."""
        pos = self.pos
        near = []
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
            try:
                h = int(e)
                kind = self.kinds.get(h)
                if kind is None:
                    kind = self.kinds[h] = e.champion_name()
                hp = e.health()
                prof = PROFILE[kind]
                dps = e.strength() * prof[0] + e.focus() * prof[1]
                gems = e.gem_count()
            except Error:
                continue
            near.append((e, ep, hp, prof[2], dps, d, gems))
        self.near_n = len(near)
        if not near:
            return False
        world = self.world
        if self.zones and self.taking_damage() and self.hp < 0.5 * self.max_hp:
            closest_enemy = min(x[5] for x in near)
            dz = self.danger()
            if closest_enemy > 4 and dz is not None and dz.is_set(pos):
                zone = Bitboard()
                for x in near:
                    zone.draw_chebyshev(x[1], x[3] + 1)
                if self.escape(zone):
                    return True
        our_hp = self.hp
        our_dps = self.dps_now
        for a in self.allies:
            try:
                ap = a.position()
                if cheb(ap, pos) > ALLY_RANGE:
                    continue
                our_hp += a.health()
                prof = PROFILE[a.champion_name()]
                our_dps += a.strength() * prof[0] + a.focus() * prof[1]
            except Error:
                pass
        pair_hp = None
        pair_gems = 0
        if PAIR_KILL:
            pair = [x for x in near if self.kinds.get(int(x[0])) in PAIR]
            if len(pair) == 2:
                pair_hp = min(pair[0][2], pair[1][2])
                pair_gems = pair[0][6] + pair[1][6]
        their_hp = 0.0
        their_dps = 0.0
        for x in near:
            w = 1.0 if x[5] <= 7 else 0.5
            if pair_hp is not None and self.kinds.get(int(x[0])) in PAIR:
                their_hp += w * pair_hp / 2  # one kill takes both
            else:
                their_hp += w * x[2]
            their_dps += w * x[4]
        ratio = (our_hp * our_dps) / max(1.0, their_hp * their_dps)
        self.last_ratio = ratio
        home = world.spawn_field().get(pos)
        if home is not None and home <= 6:
            ratio *= 1.4
        if cheb(pos, world.enemy_spawn_center) <= 7:
            ratio *= 0.6
        if FIGHT_MEMO:
            hist = [x for x in self.ratio_hist if self.now - x[0] <= FIGHT_MEMO]
            hist.append((self.now, ratio))
            self.ratio_hist = hist
            for x in hist:
                if x[1] < ratio:
                    ratio = x[1]
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
                self.hit(x[0], x[1], champion=True)
                return True
        if FIGHT_SHIELD:
            self.shield_up(closest)
        if STANDOFF_TURNS and (not TEAM_STALL_ROUNDS or self.team_stalled()) and self.standoff_check(near, closest):
            return False  # a stand-off: leave enemies that aren't fighting alone and work away from them
        extra = FIGHT_GEM_EXTRA if self.gems >= 20 else 0.0
        retreat_at = FIGHT_RETREAT + extra
        engage_at = FIGHT_ENGAGE + extra
        if ratio < retreat_at or (frac < LOW_HP_RETREAT and closest <= LOW_HP_REACH):
            in_range = [x for x in near if x[5] <= self.rng]
            if in_range and not self.ranged and self.can_attack:
                self.basic_attack(min(in_range, key=lambda x: x[2])[0])
            self.retreat(near)
            return True
        # Pick the most valuable target: low health, carrying gems, already in range.
        best = near[0]
        best_v = -1.0
        for x in near:
            if pair_hp is not None and self.kinds.get(int(x[0])) in PAIR:
                v = (200.0 + 2.0 * pair_gems) / (x[2] + 50.0)
            else:
                v = (100.0 + 2.0 * x[6]) / (x[2] + 50.0)
            if x[5] <= self.rng:
                v *= 2.0
            v /= 1.0 + 0.1 * x[5]
            if v > best_v:
                best_v = v
                best = x
        e, ep, d = best[0], best[1], best[5]
        if GEM_HUNT and best[6] >= 40:
            engage_at = max(retreat_at + 0.1, engage_at - GEM_HUNT)
        engage = ratio >= engage_at
        if d <= self.rng:
            self.hit(e, ep, champion=True)
            return True
        in_range = [x for x in near if x[5] <= self.rng]
        if in_range and self.can_attack and (not self.ranged or not engage):
            # Free hit on whoever is in reach (melee can still move afterwards).
            x = min(in_range, key=lambda x: x[2])
            if self.basic_attack(x[0]):
                self.use_reset(x[0])
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

    def standoff_check(self, near, closest):
        """Count turns facing enemies while nobody loses health. After STANDOFF_TURNS, keep away from those
        enemies for AVOID_ROUNDS. Returns True when they should be ignored this turn (not closing in, no one hurt).

        Without this, a champion could alternate forever between retreating (ratio below the retreat
        threshold) and walking back towards its target (ratio in the hold band) next to enemies that never move.
        """
        if self.now - self.standoff_round > 3:
            self.standoff = 0  # a new encounter
        self.standoff_round = self.now
        hurt = self.taking_damage()
        seen = self.enemy_hp
        for x in near:
            h = int(x[0])
            last = seen.get(h)
            if last is not None and x[2] < last:
                hurt = True
            seen[h] = x[2]
        self.standoff = 0 if hurt else self.standoff + 1
        if self.standoff >= STANDOFF_TURNS:
            self.standoff = 0
            zone = Bitboard()
            pts = []
            for x in near:
                r = x[3] + 3
                zone.draw_chebyshev(x[1], r)
                pts.append((x[1].x, x[1].y, r))
            self.avoid_zone = zone
            self.avoid_pts = pts
            self.avoid_until = self.now + AVOID_ROUNDS
            self.target = None  # choose a target away from them
            if DEBUG:
                self.log(f"STANDOFF avoid {pts} until r{self.avoid_until}")
        return self.now < self.avoid_until and not hurt and closest > 2

    def keep_away(self, avoid):
        """A movement avoid set plus the stand-off avoid zone while it is active."""
        if self.now >= self.avoid_until or self.avoid_zone is None:
            return avoid
        return self.avoid_zone if avoid is None else (avoid | self.avoid_zone)

    def hit(self, unit, upos, champion):
        """Basic attack, attack reset and offensive cast on a unit in range (ranged champions cast first if CAST_FIRST)."""
        if CC_FIRST and champion:
            self.cast_offense(unit, upos, champion=True, kinds=(K_AOE, K_CC))
        if CAST_FIRST and self.ranged:
            self.cast_offense(unit, upos, champion=champion)
            self.basic_attack(unit)
            self.use_reset(unit)
        else:
            self.basic_attack(unit)
            self.use_reset(unit)
            self.cast_offense(unit, upos, champion=champion)

    def shield_up(self, closest):
        """Cast a ready self-shield when an enemy champion can hit us next turn or something is hurting us."""
        if not self.can_cast or (closest > 1 and not self.taking_damage()):
            return
        for i in (0, 1):
            if self.ab_kind[i] == K_SHIELD and self.abilities[i].cooldown() == 0:
                try:
                    if self.abilities[i].use():
                        self.can_cast = False
                except Error:
                    pass
                return

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
        zone = Bitboard()
        for x in near:
            zone.draw_chebyshev(x[1], x[3] + 1)
        camps = self.danger()
        in_camp_range = camps is not None and camps.is_set(self.pos)
        if in_camp_range and self.taking_damage() and self.escape(zone):
            return  # a camp is hitting us: get out of its range before anything else
        far = min(x[5] for x in near)
        if far >= (10 if RECALL_SAFE else 8) and not in_camp_range:
            sd = world.spawn_field().get(self.pos)
            if sd is not None and sd > 8 and self.try_recall():
                return
        if camps is not None:
            zone |= camps
        if self.go(world.my_spawn, allow_dash=True, avoid=zone):
            return
        if DEBUG:
            self.why = f"stuck(can_move={self.can_move})"
        # Could not move (blocked in): recall if nobody can reach us before it starts.
        if not in_camp_range:
            for x in near:
                if x[5] - x[3] <= (RECALL_SAFE if RECALL_SAFE else 1):
                    return
            self.try_recall()

    def try_recall(self):
        try:
            self.me.recall()
        except Error:
            return False
        self.target = None
        self.claim(None)
        return True

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
                            unit = self.next_camp(unit) if RESET_RETARGET else None
                            if unit is None:
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

    def next_camp(self, dead):
        """A live camp of the same group in basic-attack range other than the one just killed (None if none, or if
        it was a champion: another group's camp would wake that group)."""
        if not isinstance(dead, cambc.Camp):
            return None
        group = self.world.camp_group.get(dead._handle)
        best = None
        for c, g, k, p, hp in self.camp_info:
            if g is not group or c._handle == dead._handle or cheb(p, self.pos) > self.rng:
                continue
            try:
                h = c.health()
            except Error:
                continue
            if h > 0 and (best is None or h < best[1]):
                best = (c, h)
        return best[0] if best is not None else None

    def cast_offense(self, unit, upos, champion, kinds=(K_DAMAGE, K_AOE, K_CC)):
        """Cast damage/stun abilities at a unit in range. Returns True if something was cast."""
        if not self.can_cast:
            return False
        d = cheb(upos, self.pos)
        for i in (0, 1):
            k = self.ab_kind[i]
            if k not in kinds:
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
            target = unit
            if k == K_AOE:
                target = upos
                if not champion and self.aoe_pos is not None and cheb(self.aoe_pos, self.pos) <= info.range:
                    target = self.aoe_pos
            try:
                ok = ab.use(target)
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

    def place_lock(self):
        """Drop our altar lock on an unlocked altar within two tiles."""
        px = self.pos.x
        py = self.pos.y
        for ax, ay, a in self.altar_xy:
            if -2 <= ax - px <= 2 and -2 <= ay - py <= 2:
                try:
                    if vision.has_altar_lock(a):
                        self.locked_altars.add((ax, ay))
                        continue
                    if self.me.consumables()[CON.ALTAR_LOCK].use(a):
                        self.has_lock = False
                        self.locked_altars.add((ax, ay))
                        if DEBUG:
                            self.log(f"LOCK placed at {ax},{ay}")
                        return
                except Error as e:
                    self.has_lock = False
                    if DEBUG:
                        self.log(f"lock failed at {ax},{ay}: {e}")
                    return

    def lock_detour(self):
        """Walk towards the nearest altar not known to be locked, if it is close. Returns True if moving."""
        px = self.pos.x
        py = self.pos.y
        best = None
        best_d = LOCK_DETOUR + 1
        for ax, ay, a in self.altar_xy:
            if (ax, ay) in self.locked_altars:
                continue
            d = max(abs(ax - px), abs(ay - py))
            if d < best_d:
                best_d = d
                best = a
        if best is None or best_d <= 2:
            return False
        roots = Bitboard()
        roots.draw_chebyshev(best, 2)
        roots &= ~self.world.block
        return self.go(roots, avoid=self.danger())

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
        shop_gold = SHOP_GOLD + SHOP_TRIP * sd if SHOP_TRIP and sd is not None else SHOP_GOLD
        shop = (not self.remote_shop and self.gems == 0 and self.build_done < len(self.build) and
                ((self.gold >= shop_gold and frac < SHOP_HP) or
                 (sd is not None and sd <= SHOP_NEAR and self.gold >= SHOP_NEAR_GOLD)))
        if frac < 0.3 or shop:
            if sd is not None and sd <= 6:
                self.go(self.world.my_spawn)
                return True
            if frac >= 0.3 and SHOP_SAFE:
                # A shopping trip only: don't start a recall that damage would cancel every turn.
                if self.taking_damage() or self.enemy_seen == self.now:
                    return False
                dz = self.danger()
                if dz is not None and dz.is_set(self.pos):
                    return False
            seen = self.now - self.enemy_seen <= RECALL_SAFE if RECALL_SAFE else self.enemy_seen == self.now
            if seen and frac < 0.5:
                # An enemy is within 10 tiles: a recall would likely be interrupted. Walk home instead.
                self.go(self.world.my_spawn, avoid=self.danger())
                return True
            return self.try_recall()
        return False

    def want_tribute(self):
        gems = self.gems
        if gems + cambc.global_submitted_gems(Team.ALLY) >= 1000:
            return True
        if self.now >= 1940:
            return True  # the round limit decides on tributed gems: bank everything
        g = self.target
        if g is not None and g.status == W.REWARD and g.tiles.is_set(self.pos):
            return False
        d = self.world.altar_field().get(self.pos)
        if d is None or d >= W.UNREACHED:
            return False
        big = TRIBUTE_BIG
        mid = TRIBUTE_MID
        if CAUTION_WINDOW and self.now - self.enemy_seen < CAUTION_WINDOW:
            big = mid
            mid = mid // 2
        if gems >= big:
            return True
        if gems >= mid and d <= 12:
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
        locked = None
        for a in world.altar_list:
            if cheb(a, self.pos) <= 1:
                try:
                    if vision.has_altar_lock(a):
                        lock = vision.altar_lock_at(a)
                        if lock.is_enemy():
                            locked = lock
                            continue
                except Error:
                    pass
                try:
                    me.submit_gems(a)
                    return
                except Error as e:
                    self.log("submit failed", e)
        if RECALL_TRAVEL and not self.at_spawn and self.enemy_seen != self.now:
            d = world.altar_field().get(self.pos)
            if d is not None and self.spawn_altar + RECALL_TURNS + 3 < d and self.try_recall():
                self.act = "recall_travel"
                return
        if locked is not None and self.can_attack:
            # Only enemy-locked altars in reach: break the lock (three hits) and tribute after.
            try:
                me.attack(locked)
                self.can_attack = False
                if self.ranged:
                    self.can_move = False
                return
            except Error:
                pass
        roots = world.altar_approach
        if self.now < self.avoid_until and self.avoid_zone is not None:
            # Prefer an altar the stand-off enemies aren't guarding, if one can be reached.
            away = roots & ~self.avoid_zone
            if not away.is_empty() and self.go(away, avoid=self.keep_away(self.danger())):
                return
        self.go(roots, avoid=self.danger())

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
        """Champions needed so the camp's total damage stays under ~55% of the attackers' health.

        With k champions the fight lasts hp/(k*dps) rounds and the camp deals g.dps per round, so we
        need g.dps*hp/(k*dps) <= 0.55*k*H, i.e. k >= sqrt(g.dps*hp / (0.55*H*dps)).
        """
        if g.dps == 0:
            return 1
        k = int((g.dps * hp_left / (0.55 * self.max_hp * dps)) ** 0.5 + 0.999)
        return k if k >= 1 else 1

    def choose_target(self, exclude=None):
        """Best camp group to work on next. Scores are cached for the rest of the turn."""
        cache = self.choice_cache
        if cache is None or cache[0] != self.now:
            self.mark("choose0")
            cache = (self.now, self.score_groups())
            self.choice_cache = cache
            self.mark("choose1")
        if self.now < self.pack_until:
            lead = self.pack_lead()
            if lead is not None and lead is not exclude:
                for score, g, need, via in cache[1]:
                    if g is lead and score > 0 and (need != 0 or not POKE_SMART):  # pack followers don't poke
                        if PACK_NEED:
                            slots = self.claims().get(g.idx)
                            if slots and len(slots) >= need:
                                break  # the lead's group has its squad: choose our own
                        self.target_need = need
                        self.target_via = via
                        return g
        best = None
        best_score = 0.0
        best_need = 1
        best_via = False
        for score, g, need, via in cache[1]:
            if g is not exclude and score > best_score:
                best_score = score
                best = g
                best_need = need
                best_via = via
        self.target_need = best_need
        self.target_via = best_via
        return best

    def pack_lead(self):
        """The group claimed by the lowest-slot ally below us (None if we are the lowest or nobody claims)."""
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
        world = self.world
        now = self.now
        fields = None
        if FAST_SCORE and self.walk_fields_done:
            fields = world.fields
            dist = None
        else:
            field = DistanceField()
            roots = Bitboard()
            roots.set(self.pos)
            field.compute(world.block, roots, Bitboard())
            self.mark("sg_field")
            dist = field.export_linear_buffer()
            self.mark("sg_export")
        claims = self.claims()
        pack_k = 0
        if self.now < self.pack_until and not PACK_NEED:
            claims = {}
            if PACK_WALK_ALL:
                pack_k = self.n_allies
        self.mark("sg_claims")
        dps = self.dps_now
        n_allies = self.n_allies
        gold_w = GOLD_WEIGHT * max(0.15, 1.0 - now / GOLD_TAPER)
        need_k = 1.0 / (NEED_FRAC * self.max_hp * dps)
        need_hurt = need_k
        if HP_AWARE:
            hp = self.hp
            if self.kind in PAIR:
                # Cassi and Issac die together: the weaker one's health share is ours too.
                for a in self.allies:
                    try:
                        if a.champion_name() in PAIR:
                            hp = min(hp, self.max_hp * a.health() / max(1.0, a.max_health()))
                    except Error:
                        pass
            need_hurt = 1.0 / (NEED_FRAC * max(1.0, hp) * dps)
        if JUNGLE_AWARE and self.jungle:
            need_k *= 0.7  # our camp damage taken is 30% lower
        # Extra damage per neighbouring camp from splash attacks and area abilities.
        cluster_dps = 0.7 * (self.strength_now if self.splash else 0.0) + 0.7 * self.focus_now * self.aoe_mod
        squad = MIN_SQUAD if MIN_SQUAD < n_allies else n_allies
        poke_dps = self.focus_now * self.poke_mod if MONOLITH_POKE else 0.0
        aoe_dps = self.focus_now * self.aoe_mod
        current = self.target
        my_slot = self.slot
        out = []
        respawn = W.RESPAWN
        recall_ok = RECALL_TRAVEL and not self.at_spawn and self.enemy_seen != now
        sp = self.spawn_dist
        margin = RECALL_TURNS + 3
        avoid = self.avoid_pts if now < self.avoid_until else ()
        for g in world.groups:
            if avoid:
                near_enemy = False
                for ex, ey, r in avoid:
                    if abs(g.ax - ex) <= r and abs(g.ay - ey) <= r:
                        near_enemy = True
                        break
                if near_enemy:
                    continue
            status = g.status
            if status == respawn:
                if now >= g.alive_at:
                    g.status = status = W.ALIVE
                    g.reset_hp()
                elif g.alive_at - now > 120:
                    continue
            if fields is not None:
                d = fields[(g.idx, -2)].get(self.pos)
                d = W.UNREACHED if d is None else d + 1  # to the camp tile itself, as before
            else:
                d = dist[g.lin]
            via = False
            if recall_ok:
                dr = sp[g.lin] + margin
                if dr < d:
                    d = dr - 3
                    via = True
            if d >= 65535:
                continue
            wait = 0
            if status == respawn:
                wait = g.alive_at - now - d
                if wait > 25:
                    continue
                if wait < 0:
                    wait = 0
            slots = claims.get(g.idx)
            others = len(slots) if slots else 0
            if status == W.REWARD:
                hp_left = 0
                need = 1
            else:
                hp_left = g.hp_now if status == W.ALIVE else g.hp_max
                need = 1
                gd = g.live_dps() if LIVE_DPS and status == W.ALIVE else g.dps
                if gd:
                    nk = need_k if g is current and g.idx in self.damaged else need_hurt
                    need = int((gd * hp_left * nk) ** 0.5 + 0.999)
                    if need > n_allies:
                        if poke_dps <= 0.0:
                            continue
                        need = 0  # too strong to fight: poke it from range 4 (poke_group)
                    elif need < 1:
                        need = 1
                if 0 < need < squad:
                    need = squad
            if need == 0:
                if POKE_AVOID_ENEMY and now - self.poke_enemy.get(g.idx, -1000) < POKE_AVOID_ENEMY:
                    continue
                # Team champion-rounds, as below: every poker walks there; the kill costs hp / one poker's damage.
                pd = poke_dps
                if AOE_POKE and aoe_dps:
                    pd += aoe_dps * (g.aoe_coverage() - 1.0)
                pd *= POKE_EFF
                cost = (others + 1) * (d + wait) + hp_left / pd + 5 + 0.5 * g.near_altar + g.gems / 10
            else:
                k = others + 1
                if k < need:
                    k = need
                if pack_k:
                    k = pack_k
                gdps = dps + cluster_dps * g.cluster if cluster_dps else dps
                # Team champion-rounds spent: everyone involved walks and fights, one captures and tributes.
                cost = k * (d + wait) + hp_left / gdps + 5 + 0.5 * g.near_altar + g.gems / 10
                if others + 1 < need:
                    cost += 4 * (need - others - 1)  # waiting for help to arrive
            value = g.gems + gold_w * g.gold
            if need and others >= need:
                value *= 0.5  # surplus helper
            elif need > 1 and slots and min(slots) < my_slot:
                value *= 1.2  # fill a squad someone already started
            if g.enemy_side:
                value *= ENEMY_SIDE
            if g is current:
                value *= 1.1
            score = value / (cost + 5)
            if SEED:
                score *= 0.98 + 0.04 * (((SEED * 2654435761 + g.idx * 40503 + my_slot * 9973 + now // 50 * 7919)
                                         % 1000) / 1000.0)
            out.append((score, g, need, via))
        self.mark("sg_loop")
        return out

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
        if g is not None and g.status == W.RESPAWN and self.now >= g.alive_at:
            g.status = W.ALIVE
            g.reset_hp()
        fighting = HOLD_TARGET_IN_FIGHT and g is not None and g.idx in self.awake
        if g is not None and (g.status == W.RESPAWN or (not fighting and self.now - self.target_round >= RETARGET_EVERY)):
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
        if self.has_lock and LOCK_DETOUR and g.idx not in self.awake and self.lock_detour():
            self.act = "lock"
            return
        if self.world.all_camp_tiles.is_set(self.pos) and not (g.status == W.REWARD and g.tiles.is_set(self.pos)):
            self.step_off()
        alive = [x for x in self.camp_info if x[1] is g]
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
        # Not in view yet (or hidden in bushes): walk towards it, or recall when that is faster.
        if self.target_via and not self.at_spawn and self.enemy_seen != self.now and self.gems == 0:
            if self.try_recall():
                self.target = g  # keep the target through the recall
                self.claim(g)
                self.act = "recall_travel"
                return
        if self.target_need == 0:
            # Poke target not in view: approach to range 4, never into its reach.
            ring = self.poke_ring(g).copy()
            if ring.is_set(self.pos):
                ring.set(self.pos, False)  # on the ring yet the camps aren't visible: try another tile
            self.go(ring, avoid=self.keep_away(self.danger()))
            return
        roots = Bitboard()
        for c in g.cells:
            roots.draw_chebyshev(c, 1)
        roots &= ~(self.world.block | self.world.all_camp_tiles)
        self.act = "standby" if g.status == W.RESPAWN and cheb(g.anchor, self.pos) <= 2 else "walk"
        avoid = self.keep_away(self.danger(exclude=g))
        if FAST_WALK and (avoid is None or avoid.is_empty()) and self.fast_walk(g):
            return
        if not self.go(roots, avoid=avoid) and cheb(g.anchor, self.pos) <= 2:
            g.status = W.ALIVE

    def fast_walk(self, g):
        """Step (and dash) along the group's cached walk field while it is more than 4 steps away. Returns True if
        moved; False leaves the turn to go()."""
        if not self.can_move:
            return False
        f = self.world.walk_field(g)
        here = f.get(self.pos)
        if here is None or here <= 4 or here >= W.UNREACHED:
            return False
        occ = self.occ
        if self.can_cast and self.dash_slot is not None:
            ab = self.abilities[self.dash_slot]
            if ab.cooldown() == 0:
                d1 = f.next_move_from(self.pos)
                if d1 is not None:
                    p1 = self.pos + d1
                    d2 = f.next_move_from(p1)
                    if d2 is not None:
                        p2 = p1 + d2
                        if not occ.is_set(p1) and not occ.is_set(p2):
                            try:
                                if ab.use(p2):
                                    self.pos = p2
                                    self.can_cast = False
                            except Error:
                                pass
        step = f.next_move_from(self.pos)
        if step is None:
            return False
        dest = self.pos + step
        if occ.is_set(dest):
            return False
        try:
            ok = self.me.move_absolute(dest)
        except Error:
            return False
        if ok:
            self.pos = dest
            self.can_move = False
            if self.ranged:
                self.can_attack = False
        return ok

    def attack_group(self, g, alive):
        """alive: (camp, group, kind, position, hp) tuples of the target group's visible camps."""
        if self.target_need == 0:
            self.poke_group(g, alive)
            return
        pos = self.pos
        awake = g.idx in self.awake
        live = {x[0]._handle for x in alive}
        nbrs = g.nbrs
        best = None
        best_key = None
        aoe_pos = None
        aoe_n = -1
        free = None
        if MELEE_REACH and not self.ranged and len(alive) > 1:
            free = ~(self.world.block | self.occ)
        for x in alive:
            h = x[0]._handle
            n = 0
            for h2 in nbrs[h]:
                if h2 in live:
                    n += 1
            if n > aoe_n:
                aoe_n = n
                aoe_pos = x[3]
            # Splash hits every neighbour of the target, so Varg hits the most crowded camp first.
            key = (-n if self.splash else 0, x[4], cheb(x[3], pos))
            if free is not None and cheb(x[3], pos) > 1:
                ring = Bitboard()
                ring.draw_chebyshev(x[3], 1)
                ring &= free
                if ring.is_empty():
                    key = (1,) + key  # boxed in by other camps: hit those first
            if best_key is None or key < best_key:
                best_key = key
                best = x
        if best is None:
            return
        camp = best[0]
        cp = best[3]
        self.aoe_pos = aoe_pos
        d = cheb(cp, pos)
        need = getattr(self, "target_need", 1)
        engaged = awake
        if AWAKE_RECENT:
            if not WAIT_STRICT:
                engaged = g.idx in self.damaged
            elif awake and need > 1:
                engaged = self.in_reach(alive)  # our own poke from range 4 wakes the group without anyone fighting it
        if need > 1 and not engaged:
            # Wait just outside camp range until enough allies have gathered.
            self.claims()
            present = max(self.ready.get(g.idx, 0), self.allies_near(cp, 5)) + 1
            if present < need and self.wait_turns < WAIT_LIMIT:
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
        if not WAIT_FIX:
            self.wait_turns = 0
        self.claim(g, ready=True)
        if STUN_CAMPS and awake:
            self.stun_camp(alive)
        if self.hp < 0.35 * self.max_hp and self.taking_damage() and (g.dps > 0 or self.zones):
            if self.ranged and d <= 4:
                self.cast_offense(camp, cp, champion=False)
            if not self.escape():
                self.step_away(cp, 4)
            return
        if d <= self.rng:
            self.hit(camp, cp, champion=False)
            if CLAIM_ON_KILL and len(alive) == 1 and not self.ranged and self.can_move:
                self.claim_tile(camp, cp)
            return
        self.cast_offense(camp, cp, champion=False)
        if self.can_attack:
            # Out of range of the chosen camp: hit any other camp of the group that is in range.
            for x in alive:
                if x is not best and cheb(x[3], pos) <= self.rng:
                    if self.basic_attack(x[0]):
                        self.use_reset(x[0])
                    break
        roots = Bitboard()
        roots.draw_chebyshev(cp, self.rng)
        if self.ranged:
            inner = Bitboard()
            inner.draw_chebyshev(cp, self.rng - 1)
            ring = roots & ~(inner | self.world.block | self.world.all_camp_tiles)
            if not ring.is_empty():
                roots = ring
        roots &= ~self.world.block
        avoid = self.danger(exclude=g)
        if CAMP_TILE_FIX:
            spawns = self.world.all_camp_tiles
            off = roots & ~spawns
            if not off.is_empty():
                roots = off
            avoid = spawns if avoid is None else (avoid | spawns)
        self.go(roots, avoid=self.keep_away(avoid))
        if cheb(cp, self.pos) <= self.rng:
            self.basic_attack(camp)
            self.use_reset(camp)

    def stun_camp(self, alive):
        """Cast a ready stun on the strongest awake camp of the group that can hit one of us next round. Cassi's
        stun (no damage) only when no damaging ability is ready, as it would take the turn's one cast. Returns True
        if something was cast."""
        if not self.can_cast:
            return False
        slot = None
        for i in (0, 1):
            k = self.ab_kind[i]
            if k == K_CC:
                info = self.ab_info[i]
                if info.modifier > 0 and not STUN_DAMAGING:
                    continue
                if self.abilities[i].cooldown() == 0 and (self.can_move or not info.exclusive_with_movement):
                    slot = i
            elif k in (K_DAMAGE, K_AOE) and self.abilities[i].cooldown() == 0:
                info = self.ab_info[i]
                if (self.ab_kind[1 - i] == K_CC and self.ab_info[1 - i].modifier == 0 and
                        (self.can_move or not info.exclusive_with_movement)):
                    return False  # Cassi: the damage cast comes first when it can be made
        if slot is None:
            return False
        info = self.ab_info[slot]
        pos = self.pos
        mates = None
        best = None
        best_key = None
        for x in alive:
            s = W.CAMP_STR[x[2]]
            if s <= 0 or cheb(x[3], pos) > info.range:
                continue
            threat = cheb(x[3], pos) <= 3
            if not threat:
                if mates is None:
                    mates = []
                    for a in self.allies:
                        try:
                            mates.append(a.position())
                        except Error:
                            pass
                for ap in mates:
                    if cheb(ap, x[3]) <= 3:
                        threat = True
                        break
            if not threat:
                continue
            try:
                b = x[0].buffs()
                if b.has_stun() and b.get(cambc.BuffTypes.STUN).duration >= 2:
                    continue  # already stunned for its next attack (duration 1 = that skip has happened)
            except Error:
                pass
            key = (s, x[4])
            if best_key is None or key > best_key:
                best_key = key
                best = x
        if best is None:
            return False
        try:
            ok = self.abilities[slot].use(best[0])
        except Error:
            return False
        if ok:
            self.can_cast = False
            if info.exclusive_with_movement:
                self.can_move = False
                if self.ranged:
                    self.can_attack = False
        return ok

    def in_reach(self, alive):
        """True if we or an ally stand within 3 of one of these camps that deals damage (someone is fighting it)."""
        cells = [x[3] for x in alive if W.CAMP_STR[x[2]] > 0]
        if not cells:
            return False
        pts = [self.pos]
        for a in self.allies:
            try:
                pts.append(a.position())
            except Error:
                pass
        for p in pts:
            for c in cells:
                if cheb(p, c) <= 3:
                    return True
        return False

    def claim_tile(self, camp, cp):
        """After killing a group's last camp, stand on its spawn tile at once so an enemy can't take the capture."""
        try:
            if camp.is_visible() and camp.health() > 0:
                return
            if self.me.move_absolute(cp):
                self.pos = cp
                self.can_move = False
        except Error:
            pass

    def poke_ring(self, g):
        """Tiles exactly 4 from the group's camps, outside their range-3 reach, with a straight walk to a camp
        (a ring tile behind a wall gives no vision of the camp). Cached per group."""
        ring = self.poke_rings.get(g.idx)
        if ring is None:
            cells = Bitboard()
            inner = Bitboard()
            ring = Bitboard()
            for c in g.cells:
                cells.set(c, True)
                inner.draw_chebyshev(c, 3)
                ring.draw_chebyshev(c, 4)
            ring &= ~(inner | self.world.block | self.world.all_camp_tiles)
            field = DistanceField()
            field.compute(self.world.block, cells, Bitboard())
            straight = Bitboard()
            for p in ring.positions():
                d = field.get(p)
                if d is not None and d <= 4:
                    straight.set(p, True)
            if not straight.is_empty():
                ring = straight
            self.poke_rings[g.idx] = ring
        return ring

    def poke_group(self, g, alive):
        """Hit a group too strong to fight with abilities from range 4, outside its camps' range-3 reach."""
        reach = Bitboard()
        for x in alive:
            if not POKE_SMART or W.CAMP_STR[x[2]] > 0:
                reach.draw_chebyshev(x[3], 3)
        pos = self.pos
        if POKE_CLOSE and self.poke_close(g, alive):
            return
        if POKE_AVOID_ENEMY and self.enemy_near_group(alive, 8):
            self.poke_enemy[g.idx] = self.now
            self.target_round = -100  # choose another target next turn
        if POKE_SMART:
            best = min(alive, key=lambda x: (cheb(x[3], pos) > 4, W.CAMP_STR[x[2]] == 0, x[4]))
        else:
            best = min(alive, key=lambda x: (cheb(x[3], pos) > 4, x[4]))  # in ability range first, then lowest HP
        camp, cp = best[0], best[3]
        self.act = "poke"
        self.claim(g, ready=True)
        safe = not reach.is_set(pos)
        if safe and cheb(cp, pos) <= 4:
            self.aoe_pos = cp
            if POKE_LIVE_RING and self.aoe_ready():
                self.aoe_pos = self.best_aoe_tile([x[3] for x in alive], pos) or cp
            if self.cast_offense(camp, cp, champion=False) or not POKE_SMART:
                return
            hit = [x for x in alive if cheb(x[3], pos) <= self.rng]
            if hit and self.can_attack:
                x = min(hit, key=lambda x: x[4])
                if self.basic_attack(x[0]):
                    self.use_reset(x[0])
                return
            if not self.ranged or self.ready_cast():
                return  # hold the poke tile for the next cast
        danger = self.danger()
        ring = None
        if POKE_LIVE_RING:
            # Tiles 4 from a live camp, outside every live camp's reach, other than this one.
            ring = Bitboard()
            for x in alive:
                ring.draw_chebyshev(x[3], 4)
            ring &= ~(reach | self.world.block | self.world.all_camp_tiles)
            ring.set(pos, False)
            if POKE_SMART and self.ranged and not ring.is_empty():
                # Prefer tiles from which a basic attack reaches a camp too (only non-damaging ones can be in reach).
                near = Bitboard()
                for x in alive:
                    if W.CAMP_STR[x[2]] == 0:
                        near.draw_chebyshev(x[3], self.rng)
                both = ring & near
                if not both.is_empty():
                    ring = both
                elif safe and cheb(cp, pos) <= 4:
                    return  # already on a poke tile and no better one
            if ring.is_empty():
                ring = None
        if ring is None:
            ring = self.poke_ring(g)
        self.go(ring, avoid=self.keep_away(reach if danger is None else (reach | danger)))

    def ready_cast(self):
        """True if a damaging ability is off cooldown."""
        for i in (0, 1):
            if self.ab_kind[i] in (K_DAMAGE, K_AOE, K_CC) and self.abilities[i].cooldown() == 0:
                return True
        return False

    def enemy_near_group(self, alive, r):
        """True if a visible enemy champion is within r of one of these live camps."""
        for e in self.enemies:
            try:
                ep = e.position()
            except Error:
                continue
            for x in alive:
                if cheb(ep, x[3]) <= r:
                    return True
        return False

    def poke_close(self, g, alive):
        """Capture step: switch from poking to a normal attack once the champions near the group can finish what is
        left (squad sizing on its remaining health and live camps), or when enemy champions come near a group below
        POKE_CLOSE_FRAC of its health. Returns True if it attacked."""
        hp_left = 0.0
        gdps = 0
        for x in alive:
            hp_left += x[4]
            gdps += W.CAMP_STR[x[2]]
        if self.dps_now <= 0:
            return False
        if POKE_SHARE:
            self.share_poke(g, hp_left)
        present = 1
        slots = self.claims().get(g.idx)
        mine = {self.ally_handles[i] for i in slots} if slots else ()
        for a in self.allies:
            if int(a) not in mine:
                continue
            try:
                ap = a.position()
            except Error:
                continue
            for x in alive:
                if cheb(ap, x[3]) <= 6:
                    present += 1
                    break
        need = 1
        if gdps:
            need = int((gdps * hp_left / (NEED_FRAC * self.max_hp * self.dps_now)) ** 0.5 + 0.999)
        close = need <= present
        if not close and hp_left <= POKE_CLOSE_FRAC * g.hp_max and need <= present + 1:
            for e in self.enemies:
                try:
                    ep = e.position()
                except Error:
                    continue
                for x in alive:
                    if cheb(ep, x[3]) <= 8:
                        close = True
                        break
                if close:
                    break
        if not close:
            return False
        if DEBUG:
            self.why = f"close need={need} present={present} hp_left={hp_left:.0f}"
        self.target_need = need if need >= 1 else 1
        self.attack_group(g, alive)
        return True

    def share_poke(self, g, hp_left):
        """Publish a poked group's remaining health: byte 6 = group index + 1, byte 7 = health in hundreds."""
        if self.n_allies > 6:
            return
        try:
            mem = cambc.shared_memory
            mem[6] = g.idx + 1 if g.idx < 255 else 0
            mem[7] = min(255, int(hp_left + 99) // 100)
        except Exception:
            pass

    def read_poke(self, seen):
        """Lower a poked group's believed health to what an ally's poke reported (see share_poke)."""
        if self.n_allies > 6:
            return
        mem = cambc.shared_memory
        v = mem[6]
        if v == 0:
            return
        groups = self.world.groups
        if v - 1 >= len(groups):
            return
        g = groups[v - 1]
        if g.status != W.ALIVE:
            if g.idx in seen or g.status == W.RESPAWN:
                try:
                    mem[6] = 0
                except Exception:
                    pass
            return
        if g.idx in seen:
            return
        hp = mem[7] * 100
        if hp < g.hp_now:
            g.hp_now = hp

    def aoe_ready(self):
        """True if an area ability could be cast this turn (cooldown 0, cast and movement allowance)."""
        if not self.can_cast:
            return False
        for i in (0, 1):
            if self.ab_kind[i] == K_AOE and self.abilities[i].cooldown() == 0:
                return self.can_move or not self.ab_info[i].exclusive_with_movement
        return False

    def best_aoe_tile(self, cells, pos):
        """On-map tile within 4 whose radius-1 square holds the most of these camp cells. Reads each Vec2 once (an
        attribute read costs ~380 fuel) and counts with a set: ~7k fuel for one camp, ~0.8M for twelve."""
        if len(cells) == 1:
            return cells[0]
        pts = set()
        for c in cells:
            pts.add((c.x, c.y))
        px = pos.x
        py = pos.y
        w = self.world.w
        h = self.world.h
        best = None
        best_n = 0
        seen = set()
        for cx, cy in pts:
            for tx in (cx, cx - 1, cx + 1):
                if tx < 0 or tx >= w or tx - px > 4 or px - tx > 4:
                    continue
                for ty in (cy, cy - 1, cy + 1):
                    if ty < 0 or ty >= h or ty - py > 4 or py - ty > 4 or (tx, ty) in seen:
                        continue
                    seen.add((tx, ty))
                    n = 0
                    for ox in (tx - 1, tx, tx + 1):
                        for oy in (ty - 1, ty, ty + 1):
                            if (ox, oy) in pts:
                                n += 1
                    if n > best_n:
                        best_n = n
                        best = (tx, ty)
        return Vec2(best[0], best[1]) if best is not None else None

    def danger(self, exclude=None):
        """Tiles in range of awake camps, except those of the excluded group."""
        out = None
        for idx, z in self.zones.items():
            if exclude is not None and idx == exclude.idx:
                continue
            out = z.copy() if out is None else (out | z)
        return out

    def escape(self, avoid=None):
        """Get out of range of every awake camp (used when hurt), steering clear of avoid tiles."""
        d = self.danger()
        if d is None or not d.is_set(self.pos):
            return False
        roots = Bitboard()
        roots.draw_chebyshev(self.pos, 8)
        roots &= ~(d | self.world.block | self.world.all_camp_tiles)
        if avoid is not None:
            safe = roots & ~avoid
            if not safe.is_empty():
                roots = safe
        return self.go(roots, allow_dash=True, avoid=avoid)

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
        if FAST_SCORE and not self.walk_fields_done and cambc.fuel_remaining() > FAST_FUEL:
            fields = self.world.fields
            for g in self.world.groups:
                if (g.idx, -2) not in fields:
                    self.world.walk_field(g)
                    return
            self.walk_fields_done = True
