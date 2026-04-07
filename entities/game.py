import player
import board
import golden_shovel

class Game: 
    def __init__(self, players: list[dict[str, str]], board_size: int) -> None:
        pawns_per_player = {2 : 10, 3 : 7, 4 : 6}
        self.players = [player.Player(i, players[i]["name"], players[i]["color"], pawns_per_player[len(players)]) for i in range(len(players))]

        colors = ["green", "red", "yellow", "blue"]
        self.boards = board.BoardPile(colors, board_size)
        self.golden_shovel = golden_shovel.GoldenShovel(self.boards.get_bottom().center)



if __name__ == "__main__":
    game = Game(
            [
                {"name": "John", "color": "green"}, 
                {"name": "Jane", "color": "red"}, 
                {"name": "Jim", "color": "yellow"}, 
                {"name": "Jill", "color": "blue"}
            ]
        )