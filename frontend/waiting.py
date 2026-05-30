# Librairie
import tkinter as tk


class Waiting:
    def __init__(self, host_ip, max_players, role="host", on_back=None):
        self.host_ip = host_ip
        self.max_players = max_players
        self.role = role
        self.on_back = on_back
        self._closed = False

        self.colors = {
            'background': '#EDECED',
            'border': '#2C2E33',
            'white': '#FFFFFF',
            'black': '#000000',
            'layer0': '#4E7F6E',
            'layer1': '#B85553',
            'layer2': '#C99430',
            'layer3': '#3F6E9E',
            'red': '#EF4F4F',
            'green': '#B3D88C',
            'grey': '#D1D1D1',
        }

        self.root = tk.Tk()
        self.root.title("Taupes&cie - En attente")
        self.root.geometry("360x480")
        self.root.minsize(360, 480)
        self.root.maxsize(360, 480)
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        self.root.tk_setPalette(
            background=self.colors['background'],
            foreground=self.colors['black'],
            activeBackground=self.colors['background'],
            activeForeground=self.colors['black'],
        )

        self._build_page()

    def _build_page(self):
        self.frame_main = tk.Frame(self.root, bg=self.colors['background'])
        self.frame_main.grid(row=0, column=0, sticky='nsew')
        self.frame_main.grid_rowconfigure(0, weight=1)
        self.frame_main.grid_rowconfigure(1, weight=1)
        self.frame_main.grid_rowconfigure(2, weight=1)
        self.frame_main.grid_rowconfigure(3, weight=1)
        self.frame_main.grid_rowconfigure(4, weight=2)
        self.frame_main.grid_columnconfigure(0, weight=1)

        self.label_title = tk.Label(
            self.frame_main,
            text="En attente de joueur",
            font=('', 24),
            bg=self.colors['background'],
        )
        self.label_title.grid(row=0, column=0, sticky='nsew')

        self.label_ip_title = tk.Label(
            self.frame_main,
            text="Adresse IP de l'hôte :",
            font=('', 16),
            bg=self.colors['background'],
        )
        self.label_ip_title.grid(row=1, column=0, sticky='nsew')

        self.label_ip = tk.Label(
            self.frame_main,
            text=self.host_ip or "—",
            font=('', 16),
            bg=self.colors['background'],
        )
        self.label_ip.grid(row=2, column=0, sticky='nsew')

        count_text = self._format_count(1, self.max_players)
        self.label_players_title = tk.Label(
            self.frame_main,
            text="Joueurs connectés :",
            font=('', 16),
            bg=self.colors['background'],
        )
        self.label_players_title.grid(row=3, column=0, sticky='nsew')

        self.label_players = tk.Label(
            self.frame_main,
            text=count_text,
            font=('', 20),
            bg=self.colors['background'],
        )
        self.label_players.grid(row=4, column=0, sticky='n')

        self.frame_error = tk.Frame(self.frame_main, bg=self.colors['background'])

        self.label_error = tk.Label(
            self.frame_error,
            text="Partie non trouvée",
            font=('', 18),
            fg=self.colors['red'],
            bg=self.colors['background'],
        )
        self.label_error.pack(pady=20)

        frame_button_back = tk.Frame(
            self.frame_error, bg=self.colors['border'], padx=2, pady=2
        )
        frame_button_back.pack(padx=50, pady=20, fill='x')
        button_back = tk.Button(
            frame_button_back,
            text="Retour",
            font=('', 16),
            bg=self.colors['layer0'],
            bd=0,
            relief='flat',
            command=self._go_back,
        )
        button_back.pack(fill='both', expand=True)

    def _format_count(self, current, maximum):
        max_text = maximum if maximum is not None else "?"
        return f"{current} / {max_text}"

    def update_player_count(self, current, maximum):
        if maximum is not None:
            self.max_players = maximum
        self.label_players.config(
            text=self._format_count(current, self.max_players)
        )

    def show_connection_failed(self):
        for widget in (
            self.label_title,
            self.label_ip_title,
            self.label_ip,
            self.label_players_title,
            self.label_players,
        ):
            widget.grid_remove()
        self.frame_error.grid(row=0, column=0, rowspan=4, sticky='nsew')

    def _go_back(self):
        if self.on_back is not None:
            self.on_back()
        self.close()

    def close(self):
        if self._closed:
            return
        self._closed = True
        self.root.quit()
        self.root.destroy()

    def display(self):
        self.root.mainloop()
        return self._closed


if __name__ == "__main__":
    waiting = Waiting(host_ip="192.168.1.76", max_players=4, role="host")
    waiting.display()
