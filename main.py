from entities import game
from entities import board
from frontend import menu
from frontend import ui

if __name__ == "__main__":
    game_menu = menu.Menu()
    game_config = game_menu.display()
    game = game.Game(game_config["nbplayer"], game_config["nbbot"])
    for ligne in game.boards.get_top().to_2d_grid():
        print(len(ligne))