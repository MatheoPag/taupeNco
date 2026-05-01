import json
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent / "entities"))

import board
import game
import golden_shovel
import pawn

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
    return {
        "players": [player_to_dict(p) for p in game_obj.players],
        "boards": [board_to_dict(b) for b in game_obj.boards.pile],
        "golden_shovel": list(game_obj.golden_shovel.position),
    }


def player_to_dict(player_obj) -> dict:
    return {
        "id": player_obj.id,
        "name": player_obj.name,
        "color": player_obj.color,
        "pawns": [pawn_to_dict(p) for p in player_obj.pawns],
    }


def pawn_to_dict(pawn_obj) -> dict:
    return {
        "id": pawn_obj.id,
        "color": pawn_obj.color,
        "position": list(pawn_obj.get_position()) if pawn_obj.get_position() else None,
        "on_board": pawn_obj.on_board,
        "moves_history": [list(m) for m in pawn_obj.moves_history],
    }


def board_to_dict(board_obj) -> dict:
    return {
        "size": board_obj.size,
        "color": board_obj.color,
        "grid": [[q, r, value] for (q, r), value in board_obj.grid.items()],
    }


def game_from_dict(data: dict):
    players_init = [{"name": p["name"], "color": p["color"]} for p in data["players"]]
    board_size = data["boards"][0]["size"]

    g = game.Game(players_init, board_size)

    for saved_player, player_obj in zip(data["players"], g.players):
        restored_pawns = [pawn_from_dict(pw) for pw in saved_player["pawns"]]
        player_obj.set_pawns(restored_pawns)

    g.boards.set_pile([board_from_dict(b) for b in data["boards"]])

    g.set_golden_shovel(golden_shovel.GoldenShovel(tuple(data["golden_shovel"])))

    return g


def pawn_from_dict(data: dict):
    p = pawn.Pawn(data["id"], data["color"])
    p.restore(data["position"], data["on_board"], data["moves_history"])
    return p


def board_from_dict(data: dict):
    b = board.Board(data["size"], data["color"])
    b.set_grid({(q, r): v for q, r, v in data["grid"]})
    return b
