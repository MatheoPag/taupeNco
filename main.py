from entities import game
from entities import board
from frontend import menu

if __name__ == "__main__":
    game_menu = menu.Menu()
    game_config = game_menu.display()
    game = game.Game(game_config["nbplayer"], game_config["nbbot"])