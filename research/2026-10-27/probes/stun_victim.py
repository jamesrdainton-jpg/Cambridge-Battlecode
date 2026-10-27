"""Probe: does a recall started at the end of a turn protect against stuns? (The top teams recall every turn.)

Copy to bots/probe_victim/src/main.py (TRICK = False) and bots/probe_victim_trick/src/main.py (TRICK = True); play
against stun_caster.py. The first pick (Vendetta) walks to the map centre and stands there without acting; every turn
it logs its health, state flags and buff restrictions before doing anything, then (TRICK) starts a recall at the end
of the turn and cancels it at the start of the next, as Mite, Trzy Kwaterki and others do.
"""
import cambc
from cambc import DistanceField, Bitboard, Team, Vec2, game_map

TRICK = False
CS = cambc.ChampionState


def walk_to(me, goal):
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
    step = field.next_move_from(me.position())
    if step is not None:
        p = me.position()
        try:
            me.move_absolute(Vec2(p.x + step.x, p.y + step.y))
        except Exception as e:
            print("move failed", repr(e))


def main():
    me = None
    while True:
        try:
            if cambc.is_draft():
                taken = cambc.draft.current_draft(Team.ALLY)
                for k in (2, 9, 0, 1, 7, 8, 4, 5, 10, 6, 3):
                    if k not in taken:
                        cambc.draft.pick(k)
                        break
            else:
                me = cambc.me()
                if me.champion_name() == cambc.ChampionType.VENDETTA:
                    r = cambc.round_number()
                    st = me.state()
                    hp = me.health() if st & CS.ALIVE else 0
                    restr = int(me.restrictions()) if st & CS.ALIVE else -1
                    print(f"V r{r} hp={hp:.0f} rec={int(bool(st & CS.RECALLING))} mv={int(bool(st & CS.CAN_MOVE))} "
                          f"at={int(bool(st & CS.CAN_ATTACK))} cast={int(bool(st & CS.CAN_CAST))} restr={restr} at={me.position()}")
                    if TRICK and st & CS.RECALLING:
                        me.cancel_recall()
                    if st & CS.ALIVE:
                        c = Vec2(game_map.width() // 2, game_map.height() // 2)
                        if max(abs(me.position().x - c.x), abs(me.position().y - c.y)) > 1:
                            walk_to(me, c)
                        if TRICK:
                            try:
                                me.recall()
                            except Exception as e:
                                print("recall failed", e)
        except Exception as e:
            print("probe error", repr(e))
        cambc.end_turn()


main()
