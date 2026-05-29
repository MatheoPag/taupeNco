import json
from pathlib import Path

from entities import board
from entities import game
from entities import golden_shovel
from entities import pawn

SAVE_VERSION = 1
SAVE_PATH = Path(__file__).parent.parent / "save" / "save.json"


def save_game(game_obj, path: Path = SAVE_PATH) -> None:
    data = game_to_dict(game_obj)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def load_game(path: Path = SAVE_PATH):
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return game_from_dict(data)


def game_to_dict(game_obj) -> dict:
    winner_id = game_obj.winner.id if game_obj.winner is not None else None
    return {
        "version": SAVE_VERSION,
        "nb_human_players": game_obj.nb_human_players,
        "nb_bots": game_obj.nb_bots,
        "nb_boards": game_obj.nb_boards,
        "board_orientation": game_obj.board_orientation,
        "current_player": game_obj.current_player,
        "phase": game_obj.phase,
        "sub_phase": game_obj.sub_phase,
        "bonus_move": game_obj.bonus_move,
        "winner_id": winner_id,
        "players": [player_to_dict(p) for p in game_obj.players],
        "boards": [board_to_dict(b) for b in game_obj.boards.pile],
        "golden_shovel": list(game_obj.golden_shovel.position),
    }


def player_to_dict(player_obj) -> dict:
    return {
        "id": player_obj.id,
        "name": player_obj.name,
        "color": player_obj.color,
        "last_pawn_moved": player_obj.last_pawn_moved,
        "disk_selected": player_obj.disk_selected,
        "pawn_selected": player_obj.pawn_selected,
        "disks": player_obj.disks.get_disks(),
        "pawns": [pawn_to_dict(p) for p in player_obj.pawns],
    }


def pawn_to_dict(pawn_obj) -> dict:
    position = pawn_obj.get_position()
    return {
        "id": pawn_obj.id,
        "color": pawn_obj.color,
        "position": list(position) if position is not None else None,
        "state": pawn_obj.state,
        "moves_history": [list(m) for m in pawn_obj.moves_history],
    }


def board_to_dict(board_obj) -> dict:
    return {
        "size": board_obj.size,
        "name": board_obj.name,
        "grid": [[q, r, value] for (q, r), value in board_obj.grid.items()],
    }


def game_from_dict(data: dict):
    nb_human = data["nb_human_players"]
    nb_bots = data["nb_bots"]
    nb_boards = data["nb_boards"]
    board_orientation = data.get("board_orientation", [0, 0, 0, 0, 0, 0])

    g = game.Game(nb_human, nb_bots, nb_boards, board_orientation)

    for saved_player, player_obj in zip(data["players"], g.players):
        player_obj.name = saved_player["name"]
        player_obj.color = saved_player["color"]
        player_obj.last_pawn_moved = saved_player.get("last_pawn_moved", -1)
        player_obj.disk_selected = saved_player.get("disk_selected")
        player_obj.pawn_selected = saved_player.get("pawn_selected")
        player_obj.disks.set_disks(saved_player["disks"])
        player_obj.set_pawns([pawn_from_dict(p) for p in saved_player["pawns"]])

    g.boards.set_pile([board_from_dict(b) for b in data["boards"]])
    g.set_golden_shovel(
        golden_shovel.GoldenShovel(tuple(data["golden_shovel"]))
    )

    g.current_player = data["current_player"]
    g.phase = data["phase"]
    g.sub_phase = data.get("sub_phase")
    g.bonus_move = data.get("bonus_move", False)
    g.legal_moves = None
    g._pending_disk_sync = None
    g._board_descended = False

    winner_id = data.get("winner_id")
    g.winner = (
        g.players[winner_id]
        if winner_id is not None and 0 <= winner_id < len(g.players)
        else None
    )

    return g


def pawn_from_dict(data: dict):
    p = pawn.Pawn(data["id"], data["color"])
    p.restore(
        data["position"],
        data.get("on_board", data.get("state") not in ("unplaced", "dead")),
        data["moves_history"],
    )
    p.state = data.get("state", "unplaced")
    return p


def _markers_from_grid(grid: dict) -> dict[str, list[tuple[int, int]]]:
    markers: dict[str, list[tuple[int, int]]] = {"X": [], "S": [], "J": []}
    for (q, r), value in grid.items():
        if value in markers:
            markers[value].append((q, r))
    return markers


def board_from_dict(data: dict) -> board.Board:
    grid = {(q, r): value for q, r, value in data["grid"]}
    name = data.get("name", data.get("color"))
    markers = _markers_from_grid(grid)
    b = board.Board(data["size"], name, markers, orientation=0)
    b.set_grid(grid)
    return b
