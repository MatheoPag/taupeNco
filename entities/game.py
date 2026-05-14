from typing import Literal

from . import board
from . import golden_shovel
from . import player
import random
class Game: 
    def __init__(self, nb_players: int, nb_bots: int, board_orientation: list[int]) -> None:
        self.board_size = 9
        self.pawns_per_player = {2 : 2, 3 : 7, 4 : 6}
        self.colors = [(0, "Surface"), (1, "Terre arable"), (2, "Sous-sol"), (3, "Roche mère")]
        self.current_player = random.randint(0, nb_players + nb_bots - 1)
        players = (
            [{"name": f"Player {i+1}", "color": self.colors[i]} for i in range(nb_players)]
            + [{"name": f"Bot {i+1}",    "color": self.colors[i+nb_players]} for i in range(nb_bots)]
        )
        
        self.players = [player.Player(i, players[i]["name"], players[i]["color"], self.pawns_per_player[len(players)]) for i in range(len(players))]
        self.boards = board.BoardPile(self.colors, self.board_size, board_orientation)
        self.golden_shovel = golden_shovel.GoldenShovel(self.boards.get_bottom().center)
        self.phase = "placement"

    def set_golden_shovel(self, shovel) -> None:
        """Remplace la golden shovel (utilise pour le chargement d'une save)."""
        self.golden_shovel = shovel

    def check_placement(self, players):
        for player in players:
            for pawn in player.pawns:
                if pawn.position is None:
                    return False
        return True

    def cell_occupied_by_pawn(self, row, col):
        for player in self.players:
            for pawn in player.pawns:
                pos = pawn.position
                if not isinstance(pos, tuple) or len(pos) != 2:
                    continue
                pr, pc = pos
                if pr is None or pc is None:
                    continue
                if pr == row and pc == col:
                    return True
        return False

    def is_legal_target_cell(self, row: int, col: int, phase: str) -> bool:
        """Vérifie si (row, col) est une case cible valide selon la phase."""
        if phase not in ("placement", "mouvement"):
            return False

        grid = self.boards.get_top().to_2d_grid()
        if not grid or not (0 <= row < len(grid) and 0 <= col < len(grid[0])):
            return False

        cell = grid[row][col]
        if cell is None:
            return False

        if self.cell_occupied_by_pawn(row, col):
            return False

        if phase == "placement" and cell == "X":
            return False

        return True

    def try_move_pawn_to_cell(self, pawn: player.Pawn, row: int, col: int, phase: str) -> bool:
        """Valide la case pour la phase donnée et déplace le pion. Pas de changement de joueur ni de phase."""
        if not self.is_legal_target_cell(row, col, phase):
            return False
        pawn.move(row, col)
        return True

    def try_place_current_pawn(self, row: int, col: int) -> bool:
        """Placement : choix automatique du prochain pion du joueur courant, puis coup si légal."""
        if self.phase != "placement":
            return False

        current = self.players[self.current_player]
        last = current.last_pawn_moved
        if last + 1 >= len(current.pawns):
            return False

        pawn = current.pawns[last + 1]
        if not self.try_move_pawn_to_cell(pawn, row, col, "placement"):
            return False

        current.last_pawn_moved = (last + 1) % len(current.pawns)
        self.current_player = (self.current_player + 1) % len(self.players)

        if self.check_placement(self.players):
            self.phase = "mouvement"
        return True

    def try_move_chosen_pawn_to(self, pawn_index: int, row: int, col: int) -> bool:
        """Phase mouvement : déplace le pion désigné du joueur courant (passage de tour à ajouter plus tard)."""
        if self.phase != "mouvement":
            return False
        cur = self.players[self.current_player]
        if not (0 <= pawn_index < len(cur.pawns)):
            return False
        return self.try_move_pawn_to_cell(cur.pawns[pawn_index], row, col, "mouvement")

if __name__ == "__main__":
    game = Game(
            [
                {"name": "John", "color": "green"}, 
                {"name": "Jane", "color": "red"}, 
                {"name": "Jim", "color": "yellow"}, 
                {"name": "Jill", "color": "blue"}
            ]
        )