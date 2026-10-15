import cambc
while True:
    if cambc.is_draft():
        taken = cambc.draft.current_draft(cambc.Team.ALLY)
        for k in (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10):
            if k not in taken:
                cambc.draft.pick(k)
                break
    cambc.end_turn()
