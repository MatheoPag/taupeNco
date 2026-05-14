from . import board
from . import golden_shovel
from . import player

class Game: 
    def __init__(self, nb_players: int, nb_bots: int) -> None:
        self.board_size = 9
        self.pawns_per_player = {2 : 10, 3 : 7, 4 : 6}
        self.colors = [(0, "Surface"), (1, "Terre arable"), (2, "Sous-sol"), (3, "Roche mère")]

        players = (
            [{"name": f"Player {i+1}", "color": self.colors[i]} for i in range(nb_players)]
            + [{"name": f"Bot {i+1}",    "color": self.colors[i+nb_players]} for i in range(nb_bots)]
        )
        
        self.players = [player.Player(i, players[i]["name"], players[i]["color"], self.pawns_per_player[len(players)]) for i in range(len(players))]

        self.boards = board.BoardPile(self.colors, self.board_size)
        self.golden_shovel = golden_shovel.GoldenShovel(self.boards.get_bottom().center)

    def set_golden_shovel(self, shovel) -> None:
        """Remplace la golden shovel (utilise pour le chargement d'une save)."""
        self.golden_shovel = shovel



if __name__ == "__main__":
    game = Game(
            [
                {"name": "John", "color": "green"}, 
                {"name": "Jane", "color": "red"}, 
                {"name": "Jim", "color": "yellow"}, 
                {"name": "Jill", "color": "blue"}
            ]
        )