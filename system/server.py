import socket
import threading
import json

class GameServer:
    def __init__(self, max_player=4, host='0.0.0.0', port=5555):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind((host, port))
        self.server.listen(max_player)
        self.max_player = max_player
        # L'hote joue en local : on attend les autres joueurs via le reseau
        self.required_clients = max(0, max_player - 1)
        self.clients = []
        self._running = False
        # 0 est reserve a l'hote, les clients reseau commencent a 1
        self._next_player_id = 1
        # Callback appele quand un client envoie une action (fournie par main.py)
        self.on_action_received = None

    def send_data(self, message: dict):
        data = (json.dumps(message) + "\n").encode('utf-8')
        old = []
        for client in self.clients:
            try:
                client.sendall(data)
            except OSError:
                old.append(client)
        for client in old:
            try:
                self.clients.remove(client)
            except ValueError:
                pass
            try:
                client.close()
            except OSError:
                pass

    def handle_client(self, conn, player_id):
        data_max_size = 4096
        buffer = b""
        while True:
            try:
                chunk = conn.recv(data_max_size)
                if not chunk:
                    break

                buffer += chunk
                while b"\n" in buffer:
                    line, buffer = buffer.split(b"\n", 1)
                    if not line.strip():
                        continue
                    try:
                        action = json.loads(line.decode('utf-8'))
                    except json.JSONDecodeError:
                        continue

                    # Notifier l'hote pour qu'il applique l'action sur sa Game
                    if self.on_action_received is not None:
                        self.on_action_received(action)

                    # Relayer l'action a tous les clients (y compris l'emetteur)
                    self.send_data(action)
            except Exception:
                break

        try:
            self.clients.remove(conn)
        except ValueError:
            pass
        try:
            conn.close()
        except OSError:
            pass

    def start(self):
        """Accepte les clients jusqu'au nombre requis.

        Puis retourne pour lancer la partie.
        """
        self._running = True
        print("En attente de joueur...")

        while len(self.clients) < self.required_clients:
            conn, addr = self.server.accept()
            self.clients.append(conn)

            player_id = self._next_player_id
            self._next_player_id += 1

            # Communique son ID au client qui vient de se connecter
            try:
                payload = json.dumps(
                    {"type": "assign_id", "player_id": player_id}
                )
                conn.sendall((payload + "\n").encode("utf-8"))
            except OSError:
                pass

            threading.Thread(
                target=self.handle_client,
                args=(conn, player_id),
                daemon=True,
            ).start()

            print(
                f"Joueur connecté ({len(self.clients)}/{self.required_clients}) "
                f": {addr[0]}:{addr[1]} -> ID {player_id}"
            )
            if len(self.clients) < self.required_clients:
                print("En attente de joueur...")

        print(f"Lobby complet ({self.max_player} joueur(s)). Démarrage de la partie...")
        self._running = False

    def stop(self):
        self._running = False
        try:
            self.server.close()
        except OSError:
            pass

def get_local_ip():
    """Retourne l'adresse IPv4 locale utilisée pour le réseau"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.connect(("8.8.8.8", 80))
            return sock.getsockname()[0]
    except OSError:
        return None

if __name__ == "__main__":
    GameServer().start()
