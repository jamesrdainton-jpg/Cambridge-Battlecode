"""Probe partner for stun_victim.py: Cassi walks to the enemy Vendetta and casts her pure stun (CC, no damage) on it
whenever it is ready and in range; she never attacks. Logs each cast. Copy to bots/probe_caster/src/main.py.
"""
import cambc
from cambc import DistanceField, Bitboard, Team, Vec2, game_map


def walk_to(me, goal, stop):
    p = me.position()
    if max(abs(p.x - goal.x), abs(p.y - goal.y)) <= stop:
        return
    field = DistanceField()
    block = game_map.walls() | game_map.holes() | game_map.altars() | game_map.spawn_region(Team.ENEMY)
    block = block | cambc.vision.champion_tiles()
    block.set(me.position(), False)
    roots = Bitboard()
    roots.draw_chebyshev(goal, 2)
    roots = roots & ~block
    field.compute(block, roots, Bitboard())
    if cambc.round_number() < 4:
        print("walk", goal, field.get(me.position()), field.next_move_from(me.position()), me.position())
    step = field.next_move_from(p)
    if step is not None:
        try:
            me.move_absolute(Vec2(p.x + step.x, p.y + step.y))
        except Exception as e:
            print("move failed", repr(e))


def main():
    while True:
        try:
            if cambc.is_draft():
                taken = cambc.draft.current_draft(Team.ALLY)
                for k in (3, 5, 6, 8, 10, 4, 7, 0, 1, 2, 9):
                    if k not in taken:
                        cambc.draft.pick(k)
                        break
            else:
                me = cambc.me()
                if me.champion_name() == cambc.ChampionType.CASSI:
                    r = cambc.round_number()
                    target = None
                    for e in cambc.champions(Team.ENEMY):
                        if e.champion_name() == cambc.ChampionType.VENDETTA and e.is_visible():
                            target = e
                    goal = target.position() if target else Vec2(game_map.width() // 2, game_map.height() // 2)
                    if r % 20 == 0:
                        print(f"C r{r} at {me.position()} goal {goal} sees_target={target is not None}")
                    walk_to(me, goal, 3)
                    if target:
                        d = max(abs(target.position().x - me.position().x), abs(target.position().y - me.position().y))
                        for ab in me.abilities():
                            inf = ab.info()
                            if type(inf).__name__ == "AbilityCc" and ab.cooldown() == 0 and d <= 4:
                                ok = ab.use(target)
                                print(f"S r{r} stun cast ok={ok} d={d} target_recalling={int(bool(target.state() & cambc.ChampionState.RECALLING))}")
        except Exception as e:
            print("caster error", repr(e))
        cambc.end_turn()


main()
