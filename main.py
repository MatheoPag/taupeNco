from entities import game
from entities import board
from frontend import menu
from frontend import ui

if __name__ == "__main__":
    game_menu = menu.Menu()
    game_config = game_menu.display()
    print(game_config)
    if game_config["connexionmode"] == "local":
        game = game.Game(game_config["nbplayer"], game_config["nbbot"], [0, 0, 0, 0])
        game_ui = ui.Interface(game)
        game_ui.displayInterface()