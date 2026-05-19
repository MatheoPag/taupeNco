# Librairie
import random
import tkinter as tk

class Interface:
    def __init__(self, game, network=None, role="local", local_player_id=0):
        # Palette de couleur
        self.game = game
        self._board_canvas = None

        # Mode de connexion : "local", "host" ou "client"
        # - local  : on applique tout directement (comportement d'origine)
        # - host   : on applique en local ET on diffuse l'action aux clients
        # - client : on envoie l'action au serveur, l'action reviendra par le reseau
        self.role = role
        # GameServer (host), GameClient (client), ou None (local)
        self.network = network
        self.local_player_id = local_player_id

        self.colors = {
            # Main
            'background' : '#D1D1D1',
            'border' : '#2C2E33',
            'white' : '#FFFFFF',
            'black' : '#000000',

            # Plateau
            'layer0' : '#4E7F6E',
            'layer0c' : '#8DCAAA',
            'layer1' : '#B85553',
            'layer1c' : '#E8958A',
            'layer2' : '#C99430',
            'layer2c' : '#F0CC6E',
            'layer3' : '#3F6E9E',
            'layer3c' : '#8CB9DC',

            # Joueur
            'player1' : '#B89FD8',
            'player1c' : '#D3C6E3',
            'player2' : '#72CFC4',
            'player2c' : '#B0DED9',
            'player3' : '#F09FBC',
            'player3c' : '#EDC6D5',
            'player4' : '#EFA96E',
            'player4c' : '#EECBAE',

            # Boutons
            'red' : '#EF4F4F',
            'green' : '#B3D88C',
            'grey' : '#D1D1D1',

            # Autre
            'eliminated' : '#8C8C8C',
        }

        # Création de la fenêtre
        self.root = tk.Tk()
        self.root.title("Taupes&cie - Menu")
        self.root.geometry("1440x800")
        self.root.minsize(1400, 800)
        self.root.maxsize(1400, 800)
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        self.root.config(bg = self.colors['background'])

        # Création des widgets
        self._build_widgets()


    # Construction des widgets
    def _build_widgets(self):

        # FOND DE L'INTERFACE
        self.frame_main = tk.Frame(self.root, bg=self.colors['background'])
        self.frame_main.grid(row=0, column=0, sticky='nsew')
        self.frame_main.grid_rowconfigure(0, weight=1)
        self.frame_main.grid_columnconfigure(0, weight=1)
        self.frame_main.grid_columnconfigure(1, weight=2)
        self.frame_main.grid_columnconfigure(2, weight=1)


        ''' GAUCHE : Infos sur le statut des joueurs '''
        self.frame_left = tk.Frame(self.frame_main, bg="#A3E6AE")
        self.frame_left.grid(row=0, column=0, sticky='nsew')


        ''' CENTRE : Plateau de jeu '''
        self.frame_center = tk.Frame(self.frame_main, bg="#A7EEEB")
        self.frame_center.grid(row=0, column=1, sticky='nsew')

        ''' DROITE : Infos sur la partie en cours '''
        self.frame_right = tk.Frame(self.frame_main, bg="#A3C9E6")
        self.frame_right.grid(row=0, column=2, sticky='nsew')
        
        self.update_ui()
        
    def update_ui(self):
        print(f"Current phase : {self.game.phase}")
        print(f"Current sub phase : {self.game.sub_phase}")
        print(self.game.boards.get_top().to_2d_grid())
        self.center()
        self.right()

    def _redraw_center_pawns(self):
        if self._board_canvas is None:
            return
        self._board_canvas.delete('pawns')
        pad = self._center_pad
        STEP_X = self._center_STEP_X
        STEP_Y = self._center_STEP_Y
        for player in self.game.players:
            for pawn in player.pawns:
                if pawn.position is None:
                    continue
                x = pad + pawn.position[1] * STEP_X
                y = pad + pawn.position[0] * STEP_Y
                r_node = 10
                fill = self.colors[player.name.lower().replace(" ", "")]
                self._board_canvas.create_oval(
                    x - r_node, y - r_node, x + r_node, y + r_node,
                    fill=fill, outline='', tags='pawns',
                )

    def _setup_center_board(self):
        canvas_circle = tk.Canvas(
            self.frame_center,
            bg=self.colors['background'],
            highlightthickness=0,
        )
        self._canvas_circle = canvas_circle
        canvas_circle.pack(fill='both', expand=True)

        def draw(event):
            self._canvas_circle.delete('all')
            w = event.width
            h = event.height

            cx = w // 2 # NE PAS TOUCHER
            cy = h // 2 - 70 # NE PAS TOUCHER
            r = min(w, h) // 2.5  # NE PAS TOUCHER
            self._canvas_circle.create_oval(
                cx - r,
                cy - r,
                cx + r,
                cy + r,
                outline=self.colors['border'],
                width=1,
            )

        canvas_circle.bind('<Configure>', draw)

        self._center_rows = 9
        self._center_columns = 17
        STEP_X = 50
        STEP_Y = 50
        self._center_STEP_X = STEP_X
        self._center_STEP_Y = STEP_Y
        self._center_pad = 40
        rows, columns = self._center_rows, self._center_columns
        pad = self._center_pad

        canvas_w = (columns - 1) * STEP_X + 2 * pad
        canvas_h = (rows - 1) * STEP_Y + 2 * pad

        self._board_canvas = tk.Canvas(
            canvas_circle, width=canvas_w, height=canvas_h,
            bg=self.colors['background'], highlightthickness=0,
        )
        self._board_canvas.place(relx=0.5, rely=0.5, anchor='center')

        grid = self.game.boards.get_top().to_2d_grid()

        # 1ère couche : plateau (cases existantes)
        for r in range(rows):
            for c in range(columns):
                if grid[r][c] is not None:
                    x = pad + c * STEP_X
                    y = pad + r * STEP_Y

                    match grid[r][c]:
                        case 0:
                            r_node, size = 5, self.colors['layer0']
                            self._board_canvas.create_oval(
                                x - r_node,
                                y - r_node,
                                x + r_node,
                                y + r_node,
                                fill=size,
                                outline='',
                            )
        # 2ème couche : plateau (trous, cases spéciales)
        for r in range(rows):
            for c in range(columns):
                if grid[r][c] is not None:
                    x = pad + c * STEP_X
                    y = pad + r * STEP_Y

                    match grid[r][c]:
                        case "X":
                            r_node, size = 20, self.colors['layer1']
                            self._board_canvas.create_oval(
                                x - r_node,
                                y - r_node,
                                x + r_node,
                                y + r_node,
                                fill=size,
                                outline='',
                            )
                        case "S":
                            r_node, size = 13, self.colors['layer0']
                            self._board_canvas.create_oval(
                                x - r_node,
                                y - r_node,
                                x + r_node,
                                y + r_node,
                                fill=size,
                                outline='',
                            )

        def get_click_coordinate(event):
            # Les coordonnées sont déjà relatives à canvas (la grille)
            grid_live = self.game.boards.get_top().to_2d_grid()
            c = round((event.x - pad) / STEP_X)
            r = round((event.y - pad) / STEP_Y)

            if not (0 <= r < rows and 0 <= c < columns):
                return None

            if grid_live[r][c] is None:
                return None

            return (r, c, grid_live[r][c])

        def gerer_clic(event):
            coords = get_click_coordinate(event)
            if coords is None:
                return
            row, col, _ = coords

            # MULTIJOUEUR
            if self.role != "local":
                # on n'agit que si c'est notre tour
                if self.game.current_player != self.local_player_id:
                    return
                # CLIENT : on envoie au serveur, on n'applique pas tout de suite.
                #          L'action reviendra via le broadcast et sera appliquee
                #          par on_network_message().
                if self.role == "client":
                    if self.game.phase == "placement":
                        self.network.send_action(
                            {"type": "place_pawn", "row": row, "col": col}
                        )
                    elif self.game.phase == "mouvement":
                        if self.game.sub_phase is None:
                            self.game.sub_phase = "choix_disque"
                        if self.game.sub_phase == "choix_disque":
                            # On tire le disque cote client : un seul joueur
                            # envoie a la fois, le broadcast garantit que
                            # tout le monde recoit la meme valeur.
                            selected_idx = self._pick_random_disk()
                            self.network.send_action(
                                {
                                    "type": "choose_disk",
                                    "disk_selected": selected_idx,
                                }
                            )
                        elif self.game.sub_phase == "choix_pion":
                            self.network.send_action(
                                {
                                    "type": "choose_pawn",
                                    "row": row,
                                    "col": col,
                                }
                            )
                        elif self.game.sub_phase == "deplacement":
                            self.network.send_action(
                                {
                                    "type": "move_chosen_pawn_to",
                                    "row": row,
                                    "col": col,
                                }
                            )
                    return

            # LOCAL ou HOST : on applique directement (logique d'origine)
            print(f"Phase : {self.game.phase}")
            action = None
            if self.game.phase == "placement":
                self.game.try_place_current_pawn(row, col)
                action = {"type": "place_pawn", "row": row, "col": col}
            elif self.game.phase == "mouvement":
                if self.game.sub_phase is None:
                    self.game.sub_phase = "choix_disque"
                if self.game.sub_phase == "choix_disque":
                    selected_idx = self._pick_random_disk()
                    self.game.try_choose_disk(selected_idx)
                    action = {"type": "choose_disk", "disk_selected": selected_idx}
                elif self.game.sub_phase == "choix_pion":
                    self.game.try_choose_pawn(row, col)
                    action = {"type": "choose_pawn", "row": row, "col": col}
                elif self.game.sub_phase == "deplacement":
                    self.game.try_move_chosen_pawn_to(row, col)
                    action = {"type": "move_chosen_pawn_to", "row": row, "col": col}
                

            # HOST : on previent les clients de ce qu'on vient de jouer
            if self.role == "host" and action is not None:
                self.network.send_data(action)

            self.update_ui()

        self._board_canvas.bind('<Button-1>', gerer_clic)

    # WIDGET PARTIE CENTRE
    def center(self):
        if self._board_canvas is None:
            self._setup_center_board()
        self._redraw_center_pawns()

    # WIDGET PARTIE DROITE
    def right(self):
        for w in self.frame_right.winfo_children():
            w.destroy()

        canvas_right = tk.Canvas(
            self.frame_right, highlightthickness=0, width=0, height=0
        )
        canvas_right.pack(fill='both', expand=True)
        player = self.game.players[self.game.current_player]

        name = player.name
        label_round = tk.Label(
            self.frame_right,
            text=f"Au tour de {name}",
            bg=self.colors['white'],
            fg=self.colors['black'],
            anchor="n",
        )

        def draw_right(event):
            
            canvas_right.delete('all')
            w = event.width 
            h = event.height
            
            size = min(w, h) * 0.6
            x0 = (w - size) / 2
            y0 = (h - size) / 2
            x1 = x0 + size
            y1 = y0 + size

            canvas_right.create_rectangle(
                x0,
                y0,
                x1,
                y1,
                fill=self.colors['white'],
                outline=self.colors['border'],
                width=3,
            )
            label_round.place(
                x=w / 2,
                y=h / 2 - 40,
                anchor='center',
                width=size * 0.8,
                height=size * 0.35,
            )
            label_round.lift()


            cx = w // 2 # NE PAS TOUCHER
            cy = h // 2 + 10 # NE PAS TOUCHER (mat : je me suis permis de toucher)

            canvas_pions = tk.Canvas(
                canvas_right,
                highlightthickness=3,
                highlightbackground=self.colors['border'],
                highlightcolor=self.colors['border'],
                bg=self.colors['white'],
            )
            
            test_data = [ # liste de liste a remplacer par la liste de mat
                [1, True],
                [2, False],
                [2, True],
                [3, False],
                [3, True],
                [4, True],
]

            self.draw_pions(canvas_pions, test_data)


            canvas_right.create_window(
                cx,
                cy,
                window=canvas_pions,
                width=size * 0.7,
                height=size * 0.3,
            )

            
        canvas_right.bind('<Configure>', draw_right)
        
    def draw_pions(self, canvas, data):
        canvas.delete("all")
        rayon = 10
        espace_x = 30
        espace_y = 20

        for i, (valeur, visible) in enumerate(data):
            colonons = i % 3
            row = i // 3
            x = 20 + colonons * espace_x # a peu pres centrer mais faudra modifier le 20
            y =10 + row * espace_y
            if visible:
                texte = str(valeur)
            else:
                texte = "?"
                
            canvas.create_oval(x - rayon, y - rayon, x + rayon, y + rayon, outline='black',width=1)
            
            canvas.create_text(x,y,text=texte)    
            
        
        
        
        

    # TEMPORAIRE : pour le moment, on tire au hasard le disque a choisir.
    # Tire au hasard l'indice d'un disque non encore utilise du joueur courant.
    # Retourne None s'il n'y a plus de disque disponible.
    def _pick_random_disk(self):
        disks = self.game.players[self.game.current_player].disks.get_disks()
        available = {idx: d for idx, d in enumerate(disks) if not d[1]}
        if not available:
            print("aucun disque disponible")
            return None
        return random.choice(list(available.keys()))


    # RESEAU : appele depuis un thread d'ecoute, on bascule sur le thread Tkinter
    def on_network_message(self, msg):
        self.root.after(0, lambda: self._apply_remote(msg))

    # Applique une action venant du reseau
    # (host : action d'un client, client : action broadcastee)
    def _apply_remote(self, msg):
        action_type = msg.get("type")
        if action_type == "place_pawn":
            self.game.try_place_current_pawn(msg["row"], msg["col"])
        elif action_type == "next_player":
            self.game.current_player = (
                (self.game.current_player + 1) % len(self.game.players)
            )
        elif action_type == "choose_disk":
            self.game.try_choose_disk(msg["disk_selected"])
        elif action_type == "choose_pawn":
            self.game.try_choose_pawn(msg["row"], msg["col"])
        elif action_type == "move_chosen_pawn_to":
            self.game.try_move_chosen_pawn_to(msg["row"], msg["col"])
        self.update_ui()


    # Affichage de l'interface du jeu
    def displayInterface(self):
        self.root.mainloop()


if __name__=="__main__":
    ui = Interface()
    ui.displayInterface()