import time

from entities import game as game_entity
from frontend import menu
from frontend import ui
from system.server import GameServer
from system.client import GameClient


def _start_game(nbplayer, nbbot):
    game_instance = game_entity.Game(nbplayer, nbbot, [0, 0, 0, 0])
    game_ui = ui.Interface(game_instance)
    game_ui.displayInterface()


if __name__ == "__main__":
    game_menu = menu.Menu()
    game_config = game_menu.display()
    print(game_config)

    if game_config["connexionmode"] == "local":
        _start_game(game_config["nbplayer"], game_config["nbbot"])

    elif game_config["connexionmode"] == "multiplayer":
        if game_config["iphost"] != "None":
            print(f"Partie hébergée - IP à partager : {game_config['iphost']}:5555")
            game_server = GameServer(
                max_player=game_config["nbplayer"],
                host="0.0.0.0",
                port=5555,
            )
            game_server.start()
            print("Initialisation de la partie...")
            _start_game(game_config["nbplayer"], game_config["nbbot"])

        elif game_config["iptarget"] != "None":
            try:
                game_client = GameClient(game_config["iptarget"], 5555)
            except OSError:
                print("Impossible de rejoindre la partie.")
            else:
                game_client.listen(lambda msg: print(f"[serveur] {msg}"))
                print("En attente du démarrage de la partie par l'hôte...")
                try:
                    while True:
                        time.sleep(1)
                except KeyboardInterrupt:
                    print("Déconnexion.")
        else:
            print("Aucune adresse IP fournie.")
