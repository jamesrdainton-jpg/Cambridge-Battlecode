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

WOLF, ELK, GEM, GOLD, MONOLITH = 0, 1, 2, 3, 4
CAMP_HP = (1350, 2400, 500, 500, 20000)
CAMP_STR = (20, 60, 0, 0, 200)


class Group:
    __slots__ = ("idx", "handle", "gold", "gems", "respawn", "kinds", "handles", "cells", "tiles",
                 "anchor", "ax", "ay", "hp_max", "dps", "status", "alive_at", "seen", "hp", "near_altar", "obj",
                 "enemy_side", "hp_now", "lin", "cell_of")

    def __init__(self, idx, obj):
        self.idx = idx
        self.obj = obj
        self.handle = int(obj)
        self.gold = obj.gold_value()
        self.gems = obj.gem_value()
        self.respawn = obj.max_respawn_timer()
        camps = obj.camps()
        self.kinds = [c.kind() for c in camps]
        self.handles = [int(c) for c in camps]
        self.cells = [c.spawn_position() for c in camps]
        self.tiles = obj.spawn_tiles()
        self.anchor = self.cells[0]
        self.ax = self.anchor.x
        self.ay = self.anchor.y
        self.lin = 0
        # Camp handle -> spawn tile (camps never move).
        self.cell_of = dict(zip(self.handles, self.cells))
        self.enemy_side = False
        self.hp_max = sum(CAMP_HP[k] for k in self.kinds)
        self.hp_now = self.hp_max
        self.dps = sum(CAMP_STR[k] for k in self.kinds)
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

        self.groups = [Group(i, g) for i, g in enumerate(game_map.camp_groups())]
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
