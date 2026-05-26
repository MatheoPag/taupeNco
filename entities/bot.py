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


def _movement_options(game) -> list[tuple[int, int, tuple[int, int]]]:
    """Triples (indice disque, indice pion, destination) realisables."""
    cur = game.players[game.current_player]
    disks = cur.disks.get_disks()
    hidden_disks = [i for i, d in enumerate(disks) if not d[1]]
    placed_pawns = [
        (i, p) for i, p in enumerate(cur.pawns) if p.position is not None
    ]
    options = []
    for disk_idx in hidden_disks:
        for pawn_idx, _pawn in placed_pawns:
            moves = game.possible_moves(pawn_idx, disk_idx)
            for dest in moves:
                options.append((disk_idx, pawn_idx, dest))
    return options


def play_placement(game) -> bool:
    cells = _placement_cells(game)
    if not cells:
        return False
    row, col = random.choice(cells)
    return game.try_place_current_pawn(row, col)


def play_movement(game) -> bool:
    options = _movement_options(game)
    if not options:
        return False

    disk_idx, pawn_idx, (row, col) = random.choice(options)
    pawn = game.players[game.current_player].pawns[pawn_idx]
    pr, pc = pawn.position

    game.sub_phase = "choix_disque"
    if not game.try_choose_disk(disk_idx, lambda: None):
        return False
    if not game.try_choose_pawn(pr, pc):
        game.sub_phase = "choix_disque"
        return False
    if game.is_player_blocked():
        game.current_player = (game.current_player + 1) % len(game.players)
        game.begin_player_turn()
        return True
    return game.try_move_chosen_pawn_to(row, col)


def play_turn(game) -> bool:
    """Joue un coup pour le joueur courant (bot). Retourne False si aucun coup."""
    if not game.is_bot():
        return False
    if game.phase == "placement":
        return play_placement(game)
    if game.phase == "mouvement":
        if game.sub_phase == "rejouer":
            game.begin_player_turn()
            return play_movement(game)
        if game.sub_phase == "passer_tour":
            game.current_player = (game.current_player + 1) % len(game.players)
            game.begin_player_turn()
            return True
        return play_movement(game)
    return False
