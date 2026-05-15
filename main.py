import threading

from entities import game as game_entity
from frontend import menu
from frontend import ui
from system.server import GameServer
from system.client import GameClient


def start_local(nbplayer, nbbot):
    game_instance = game_entity.Game(nbplayer, nbbot, [0, 0, 0, 0])
    game_ui = ui.Interface(game_instance)
    game_ui.displayInterface()


def start_host(nbplayer, nbbot, host_ip):
    print(f"Partie hébergée - IP à partager : {host_ip}:5555")
    game_server = GameServer(max_player=nbplayer, host="0.0.0.0", port=5555)
    game_server.start()

    print("Initialisation de la partie...")
    game_instance = game_entity.Game(nbplayer, nbbot, [0, 0, 0, 0])

    game_ui = ui.Interface(
        game_instance,
        network=game_server,
        role="host",
        local_player_id=0,
    )

    # Quand un client envoie une action, l'hote l'applique sur sa propre Game
    game_server.on_action_received = game_ui.on_network_message

    # On annonce le demarrage aux clients : ils ont besoin de connaitre
    # le nb de joueurs/bots et le current_player tire au hasard cote hote.
    game_server.send_data({
        "type": "game_start",
        "nbplayer": nbplayer,
        "nbbot": nbbot,
        "current_player": game_instance.current_player,
    })

    game_ui.displayInterface()


def start_client(target_ip):
    try:
        game_client = GameClient(target_ip, 5555)
    except OSError:
        print("Impossible de rejoindre la partie.")
        return

    # Petits "conteneurs" pour partager des donnees entre le thread d'ecoute
    # et le thread principal (sans introduire de classe).
    local_id = {"value": None}
    start_data = {"value": None}
    ui_holder = {"value": None}
    ready_event = threading.Event()

    def on_message(msg):
        msg_type = msg.get("type")
        if msg_type == "assign_id":
            local_id["value"] = msg["player_id"]
            print(f"ID attribué par l'hôte : {msg['player_id']}")
        elif msg_type == "game_start":
            start_data["value"] = msg
            ready_event.set()
        else:
            # Toute autre action (place_pawn, next_player, ...) -> UI
            if ui_holder["value"] is not None:
                ui_holder["value"].on_network_message(msg)

    game_client.listen(on_message)

    print("En attente du démarrage de la partie par l'hôte...")
    ready_event.wait()

    data = start_data["value"]
    print(f"Partie démarrée : {data['nbplayer']} joueur(s), {data['nbbot']} bot(s).")

    game_instance = game_entity.Game(data["nbplayer"], data["nbbot"], [0, 0, 0, 0])
    # On force le current_player pour etre synchronise avec l'hote
    game_instance.current_player = data["current_player"]

    game_ui = ui.Interface(
        game_instance,
        network=game_client,
        role="client",
        local_player_id=local_id["value"],
    )
    ui_holder["value"] = game_ui
    game_ui.displayInterface()


if __name__ == "__main__":
    game_menu = menu.Menu()
    game_config = game_menu.display()
    print(game_config)

    if game_config["connexionmode"] == "local":
        start_local(game_config["nbplayer"], game_config["nbbot"])

    elif game_config["connexionmode"] == "multiplayer":
        if game_config["iphost"] != "None":
            start_host(
                game_config["nbplayer"],
                game_config["nbbot"],
                game_config["iphost"],
            )
        elif game_config["iptarget"] != "None":
            start_client(game_config["iptarget"])
        else:
            print("Aucune adresse IP fournie.")
