import socket
import threading
import json
import argparse

class GameClient:
    def __init__(self, host, port=5555):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.sock.connect((host, port))
        except OSError as err:
            print(f"Échec de la connexion : {err}")
            raise

    def send_action(self, action: dict):
        self.sock.sendall((json.dumps(action) + "\n").encode('utf-8'))

    def listen(self, callback):
        def _run():
            buffer = b""
            while True:
                data = self.sock.recv(4096)
                if not data:
                    break
                buffer += data
                while b"\n" in buffer:
                    line, buffer = buffer.split(b"\n", 1)
                    if not line.strip():
                        continue
                    try:
                        state = json.loads(line.decode('utf-8'))
                    except json.JSONDecodeError:
                        continue
                    callback(state)
        threading.Thread(target=_run, daemon=True).start()
        # thread separer pour ne pas bloquer tkinter. 
        # daemon=True -> s'arrete quand la fenetre principale se ferme
