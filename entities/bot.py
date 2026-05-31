import random

def _placement_cells(game) -> list[tuple[int, int]]:
    """Cases valides en placement : valeur 0 sur la grille et coup legal."""
    grid = game.boards.get_top().to_2d_grid()
    cells = []
    for row, line in enumerate(grid):
        for col, value in enumerate(line):
            if value == 0 and game.is_legal_target_cell(row, col, "placement"):
                cells.append((row, col))
    return cells


def _pawn_on_hole(game, pawn) -> bool:
    """True si le pion est sur une case trou (X) du plateau courant."""
    if pawn.position is None:
        return False
    board = game.boards.get_top()
    row, col = pawn.position
    q, r = board.from_2d_to_axial(row, col)
    return board.grid.get((q, r)) == "X"


def _movement_options_for_pawns(
    game,
    pawn_filter,
) -> list[tuple[int, int, tuple[int, int]]]:
    """Triples (indice disque, indice pion, destination) pour les pions retenus."""
    cur = game.players[game.current_player]
    disks = cur.disks.get_disks()
    hidden_disks = [i for i, d in enumerate(disks) if not d[1]]
    placed_pawns = [
        (i, p)
        for i, p in enumerate(cur.pawns)
        if p.position is not None and pawn_filter(game, p)
    ]
    options = []
    for disk_idx in hidden_disks:
        for pawn_idx, _pawn in placed_pawns:
            moves = game.possible_moves(pawn_idx, disk_idx)
            for dest in moves:
                options.append((disk_idx, pawn_idx, dest))
    return options


def _movement_options(game) -> list[tuple[int, int, tuple[int, int]]]:
    """Priorise les pions hors trou ; sinon ceux dans un trou si seuls mobilisables."""
    options = _movement_options_for_pawns(
        game, lambda g, p: not _pawn_on_hole(g, p)
    )
    if options:
        return options
    return _movement_options_for_pawns(
        game, lambda g, p: _pawn_on_hole(g, p)
    )


def play_placement(game) -> bool:
    cells = _placement_cells(game)
    if not cells:
        return False
    row, col = random.choice(cells)
    return game.try_place_current_pawn(row, col)


def play_replay_turn(game) -> bool:
    """Le bot rejoue toujours apres une case speciale."""
    game.start_bonus_turn()
    return play_movement(game)


def _zero_disk_options(game) -> list[int]:
    """Indices des disques 0 encore faces cachees."""
    cur = game.players[game.current_player]
    return [
        i for i, d in enumerate(cur.disks.get_disks()) if not d[1] and d[0] == 0
    ]


def play_movement(game) -> bool:
    if game.is_all_pawns_in_holes():
        cur = game.players[game.current_player]
        game._finish_disk_cycle(cur, shuffle_disks=True)
        return True

    options = _movement_options(game)
    if not options:
        zero_disks = _zero_disk_options(game)
        if not zero_disks:
            return False
        game.enter_disk_choice_phase(shuffle_disks=True)
        return game.try_choose_disk(random.choice(zero_disks), lambda: None)

    disk_idx, pawn_idx, (row, col) = random.choice(options)
    pawn = game.players[game.current_player].pawns[pawn_idx]
    pr, pc = pawn.position

    game.enter_disk_choice_phase(shuffle_disks=True)
    if not game.try_choose_disk(disk_idx, lambda: None):
        return False
    if not game.try_choose_pawn(pr, pc):
        game.enter_disk_choice_phase(shuffle_disks=True)
        return False
    if game.is_player_blocked():
        cur = game.players[game.current_player]
        game._finish_disk_cycle(cur, shuffle_disks=True)
        return True
    if not game.try_move_chosen_pawn_to(row, col):
        return False
    if game.sub_phase == "rejouer":
        return play_replay_turn(game)
    return True


def play_turn(game) -> bool:
    """Joue un coup pour le joueur courant (bot). Retourne False si aucun coup."""
    if not game.is_bot():
        return False
    if game.phase == "placement":
        return play_placement(game)
    if game.phase == "mouvement":
        if game.sub_phase == "rejouer":
            return play_replay_turn(game)
        if game.sub_phase == "passer_tour":
            cur = game.players[game.current_player]
            game._finish_disk_cycle(cur, shuffle_disks=True)
            return True
        return play_movement(game)
    return False
