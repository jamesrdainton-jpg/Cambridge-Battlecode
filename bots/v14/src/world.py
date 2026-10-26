"""Static map data, cached once per champion, plus what this champion knows about camp groups.

Engine calls are expensive in this sandbox (a few thousand fuel each, and game_map.camp_groups()
costs ~600k), so everything static is read once here and kept in plain Python structures.
"""
import cambc
from cambc import game_map, Vec2, Bitboard, DistanceField, Team

UNREACHED = 65535

# Group knowledge states.
ALIVE = 0      # camps believed alive
REWARD = 1     # all camps dead, reward waiting for a capture
RESPAWN = 2    # captured; respawns at alive_at

WOLF, ELK, GEM, GOLD, MONOLITH, GOLEM = 0, 1, 2, 3, 4, 5
# Camp health, strength and attack range per camp kind, read from the engine's camp designs the first time a kind is
# seen. cambc 3.0 changed them (gem and gold clusters 500 -> 120 HP, elk range 4, monolith range 5) and added the golem
# (kind 5: 5,000 HP, 120 strength, range 4); v12's fixed 5-entry tuples raised IndexError on every map with a golem,
# so the whole team stood still all game.
CAMP_HP = {}
CAMP_STR = {}
CAMP_RNG = {}


def learn_camp(c):
    """Return the camp's kind, recording its design stats on first sight (one engine call per kind)."""
    k = c._type
    if k not in CAMP_HP:
        try:
            s = c.base_stats()
            CAMP_HP[k] = s.base_health
            CAMP_STR[k] = s.base_strength
            CAMP_RNG[k] = s.base_attack_range
        except Exception:  # noqa: BLE001 - unknown kind: assume a boss, never crash
            CAMP_HP[k] = 5000.0
            CAMP_STR[k] = 120.0
            CAMP_RNG[k] = 4
    return k


class Group:
    __slots__ = ("idx", "handle", "gold", "gems", "respawn", "kinds", "handles", "cells", "tiles",
                 "anchor", "ax", "ay", "hp_max", "dps", "status", "alive_at", "seen", "hp", "near_altar", "obj",
                 "enemy_side", "hp_now", "lin", "cell_of", "nbrs", "cluster", "rng", "boss")

    def __init__(self, idx, obj):
        # Reads the SDK objects' attributes directly: method calls cost ~1k fuel each and this runs
        # for every group on the first turn.
        self.idx = idx
        self.obj = obj
        self.handle = obj._handle
        self.gold = obj._gold
        self.gems = obj._gems
        self.respawn = obj._respawn
        kinds = []
        handles = []
        cells = []
        xs = []
        ys = []
        tiles = Bitboard()
        hp_max = 0
        dps = 0
        rng = 0
        boss = False
        for c in obj._camps:
            k = learn_camp(c)
            p = c._spawn_position
            if CAMP_STR[k] > 0 and CAMP_RNG[k] > rng:
                rng = CAMP_RNG[k]
            if CAMP_HP[k] >= 5000:
                boss = True  # monolith or golem
            kinds.append(k)
            handles.append(c._handle)
            cells.append(p)
            xs.append(p.x)
            ys.append(p.y)
            tiles.set(p)
            hp_max += CAMP_HP[k]
            dps += CAMP_STR[k]
        self.kinds = kinds
        self.handles = handles
        self.cells = cells
        self.tiles = tiles
        self.anchor = cells[0]
        self.ax = xs[0]
        self.ay = ys[0]
        self.lin = 0
        # Camp handle -> spawn tile (camps never move).
        self.cell_of = dict(zip(handles, cells))
        # Camp handle -> handles of the group's other camps within one tile (splash / AoE reach).
        n = len(handles)
        nbrs = {}
        total = 0
        for i in range(n):
            near = []
            if n > 1:
                x = xs[i]
                y = ys[i]
                for j in range(n):
                    if j != i and -1 <= xs[j] - x <= 1 and -1 <= ys[j] - y <= 1:
                        near.append(handles[j])
                total += len(near)
            nbrs[handles[i]] = near
        self.nbrs = nbrs
        self.cluster = total / n
        self.enemy_side = False
        self.hp_max = hp_max
        self.hp_now = hp_max
        self.dps = dps
        # Reach of the group's damaging camps (0 when none deal damage).
        self.rng = rng
        # Holds a monolith or golem (a camp with 5,000+ HP): sized with BOSS_NEED_FRAC and BOSS_WAIT.
        self.boss = boss
        self.status = ALIVE
        self.alive_at = 0
        self.seen = -1
        # Last seen health per camp handle (missing = full).
        self.hp = {}
        self.near_altar = UNREACHED

    def hp_left(self):
        return self.hp_now

    def refresh_hp(self):
        total = 0
        hp = self.hp
        for h, k in zip(self.handles, self.kinds):
            total += hp.get(h, CAMP_HP[k])
        self.hp_now = total

    def reset_hp(self):
        self.hp = {}
        self.hp_now = self.hp_max


class World:
    def __init__(self):
        self.prof = [("start", cambc.fuel_remaining())]
        self.w = game_map.width()
        self.h = game_map.height()
        walls = game_map.walls()
        holes = game_map.holes()
        altars = game_map.altars()
        self.walls = walls
        self.bushes = game_map.bushes()
        self.my_spawn = game_map.spawn_region(Team.ALLY)
        self.enemy_spawn = game_map.spawn_region(Team.ENEMY)
        # Tiles nobody on our team can stand on.
        self.block = walls | holes | altars | self.enemy_spawn
        self.altar_list = altars.positions()
        self.altars = altars
        # Tiles from which a tribute can be made.
        approach = Bitboard()
        for a in self.altar_list:
            approach.draw_chebyshev(a, 1)
        self.altar_approach = approach & ~self.block
        self.spawn_tiles = self.my_spawn.positions()
        sp = self.spawn_tiles[len(self.spawn_tiles) // 2]
        self.spawn_center = sp
        esp = self.enemy_spawn.positions()
        self.enemy_spawn_center = esp[len(esp) // 2]
        sx, sy = sp.x, sp.y
        ex, ey = self.enemy_spawn_center.x, self.enemy_spawn_center.y

        self.prof.append(("terrain", cambc.fuel_remaining()))
        raw = game_map.camp_groups()
        self.prof.append(("camp_groups", cambc.fuel_remaining()))
        self.groups = [Group(i, g) for i, g in enumerate(raw)]
        self.prof.append(("Group objs", cambc.fuel_remaining()))
        self.camp_group = {}
        self.all_camp_tiles = Bitboard()
        w = self.w
        # Coarse 10x10 buckets so "groups near me" never scans the whole list.
        self.buckets = {}
        for g in self.groups:
            self.buckets.setdefault((g.ax // 10, g.ay // 10), []).append(g)
        for g in self.groups:
            g.lin = g.ay * w + g.ax
            self.all_camp_tiles |= g.tiles
            de = max(abs(g.ax - ex), abs(g.ay - ey))
            dm = max(abs(g.ax - sx), abs(g.ay - sy))
            g.enemy_side = de < dm
            for h in g.handles:
                self.camp_group[h] = g
        self.fields = {}
        self._altar_field = None
        self._spawn_field = None

    # Distance fields rooted at static goals, computed lazily and cached.
    def altar_field(self):
        f = self._altar_field
        if f is None:
            f = DistanceField()
            f.compute(self.block, self.altar_approach, Bitboard())
            self._altar_field = f
        return f

    def spawn_field(self):
        f = self._spawn_field
        if f is None:
            f = DistanceField()
            f.compute(self.block, self.my_spawn, Bitboard())
            self._spawn_field = f
        return f

    def group_field(self, g, cells, rng):
        """Field rooted at tiles within rng of the given camp cells (camp cells themselves excluded)."""
        key = (g.idx, rng, tuple((c.x, c.y) for c in cells))
        f = self.fields.get(key)
        if f is None:
            roots = Bitboard()
            for c in cells:
                roots.draw_chebyshev(c, rng)
            roots &= ~(self.block | g.tiles)
            if rng == 0 or roots.is_empty():
                roots = g.tiles.copy()
            f = DistanceField()
            f.compute(self.block, roots, Bitboard())
            self.fields[key] = f
        return f

    def capture_field(self, g):
        key = (g.idx, -1)
        f = self.fields.get(key)
        if f is None:
            f = DistanceField()
            f.compute(self.block, g.tiles, Bitboard())
            self.fields[key] = f
        return f
