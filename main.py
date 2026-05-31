import threading

from entities import game as game_entity
from frontend import menu
from frontend import ui
from frontend.waiting import Waiting
from system.server import GameServer
from system.client import GameClient


def start_from_save(game_instance):
    game_ui = ui.Interface(game_instance)
    game_ui.displayInterface()


def start_local(nbplayer, bot=False, nb_boards=4, board_orientation=None):
    if board_orientation is None:
        board_orientation = [0, 0, 0, 0, 0, 0]
    game_instance = game_entity.Game(
            nbplayer,
            1 if bot else 0, 
            nb_boards, 
            board_orientation
        )
    game_ui = ui.Interface(game_instance)
    game_ui.displayInterface()


def start_host(nbplayer, host_ip, nb_boards=4, board_orientation=None):
    if board_orientation is None:
        board_orientation = [0, 0, 0, 0, 0, 0]

    waiting = Waiting(host_ip=host_ip, max_players=nbplayer, role="host")
    lobby_ready = threading.Event()
    server_holder = {"value": None}

    def run_lobby():
        game_server = GameServer(max_player=nbplayer, host="0.0.0.0", port=5555)

        def on_player_joined(current, maximum):
            waiting.root.after(
                0,
                lambda c=current, m=maximum: waiting.update_player_count(c, m),
            )

        game_server.on_player_joined = on_player_joined
        server_holder["value"] = game_server
        game_server.start()
        lobby_ready.set()
        waiting.root.after(0, waiting.close)

    threading.Thread(target=run_lobby, daemon=True).start()
    waiting.display()
    lobby_ready.wait()

    game_server = server_holder["value"]
    if game_server is None:
        return

    print(f"Partie hébergée - IP à partager : {host_ip}:5555")
    print("Initialisation de la partie...")
    game_instance = game_entity.Game(nbplayer, 0, nb_boards, board_orientation)

    game_ui = ui.Interface(
        game_instance,
        network=game_server,
        role="host",
        local_player_id=0,
    )

    game_server.on_action_received = game_ui.on_network_message

    game_server.send_data({
        "type": "game_start",
        "nbplayer": nbplayer,
        "nbboard": nb_boards,
        "current_player": game_instance.current_player,
        "players_disks": game_instance.get_players_disks_state(),
        "board_orientation": board_orientation,
    })

    game_ui.displayInterface()


def start_client(target_ip):
    back_requested = {"value": False}

    def on_back():
        back_requested["value"] = True

    waiting = Waiting(
        host_ip=target_ip,
        max_players=None,
        role="client",
        on_back=on_back,
    )

    game_client = None
    local_id = {"value": None}
    start_data = {"value": None}
    ready_event = threading.Event()
    failed = {"value": False}
    ui_holder = {"value": None}

    def connect_and_listen():
        nonlocal game_client
        try:
            game_client = GameClient(target_ip, 5555)
        except OSError:
            failed["value"] = True
            waiting.root.after(0, waiting.show_connection_failed)
            return

        def on_message(msg):
            msg_type = msg.get("type")
            if msg_type == "lobby_update":
                current = msg["current"]
                maximum = msg["max"]
                waiting.root.after(
                    0,
                    lambda c=current, m=maximum: waiting.update_player_count(c, m),
                )
            elif msg_type == "assign_id":
                local_id["value"] = msg["player_id"]
                print(f"ID attribué par l'hôte : {msg['player_id']}")
            elif msg_type == "game_start":
                start_data["value"] = msg
                ready_event.set()
                waiting.root.after(0, waiting.close)
            elif ui_holder["value"] is not None:
                ui_holder["value"].on_network_message(msg)

        game_client.listen(on_message)

    threading.Thread(target=connect_and_listen, daemon=True).start()
    waiting.display()

    if back_requested["value"]:
        return "back"
    if failed["value"] or not ready_event.is_set():
        return "failed"

    data = start_data["value"]
    print(f"Partie démarrée : {data['nbplayer']} joueur(s).")

    game_instance = game_entity.Game(
        data["nbplayer"],
        0,
        data.get("nbboard", 4),
        data.get("board_orientation", [0, 0, 0, 0, 0, 0]),
    )
    game_instance.current_player = data["current_player"]
    if "players_disks" in data:
        game_instance.apply_players_disks_state(data["players_disks"])

    game_ui = ui.Interface(
        game_instance,
        network=game_client,
        role="client",
        local_player_id=local_id["value"],
    )
    ui_holder["value"] = game_ui
    game_ui.displayInterface()
    return "ok"


def main():
    while True:
        game_menu = menu.Menu()
        game_config = game_menu.display()
        game_menu.stop_music()

        board_orientation = game_config.get("board_orientation", [0, 0, 0, 0, 0, 0])

        if game_config.get("connexionmode") == "save":
            loaded_game = game_config.get("loaded_game")
            if loaded_game is not None:
                start_from_save(loaded_game)
            else:
                print("Aucune partie chargee.")
            return

        if game_config["connexionmode"] == "local":
            if game_config["gamemode"] == "classic" or game_config["gamemode"] == "custom":
                if game_config['nbplayer'] > 1:
                    start_local(
                        game_config["nbplayer"],
                        bot=False,
                        nb_boards=game_config["nbboard"],
                        board_orientation=board_orientation
                    )
            if game_config['nbplayer'] == 1 and game_config["gamemode"] == "solobot":
                start_local(
                    game_config["nbplayer"],
                    bot=True,
                    nb_boards=game_config["nbboard"],
                    board_orientation=board_orientation
                )
            return

        if game_config["connexionmode"] == "multiplayer":
            if game_config["iphost"] != "None":
                start_host(
                    game_config["nbplayer"],
                    game_config["iphost"],
                    nb_boards=game_config["nbboard"],
                    board_orientation=board_orientation
                )
                return
            if game_config["iptarget"] != "None":
                result = start_client(game_config["iptarget"])
                if result == "back":
                    continue
                return
            print("Aucune adresse IP fournie.")
            return

        return


if __name__ == "__main__":
    main()
