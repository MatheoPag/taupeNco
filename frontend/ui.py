# Librairie
import tkinter as tk
import time
import os
from entities import bot as bot_ai

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
        self._bot_after_id = None

        self.colors = {
            # Main
            'background' : '#EDECED',
            'border' : '#2C2E33',
            'white' : '#FFFFFF',
            'black' : '#000000',

            # Plateau
            'layer101' : '#6B7280',
            'layer101c' : '#B1B8C4',
            'layer102' : '#795640',
            'layer102c' : '#C39A7E',
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
            'bot' : '#72CFC4',
            'botc' : '#B0DED9',

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
        self._center_pad_x = 10
        self._center_pad_y = 10

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
        self.frame_left = tk.Frame(self.frame_main, bg=self.frame_main['bg'])
        self.frame_left.grid(row=0, column=0, sticky='nsew')

        ''' CENTRE : Plateau de jeu '''
        self.frame_center = tk.Frame(self.frame_main, bg=self.frame_main['bg'])
        self.frame_center.grid(row=0, column=1, sticky='nsew')

        ''' DROITE : Infos sur la partie en cours '''
        self.frame_right = tk.Frame(self.frame_main, bg=self.frame_main['bg'])
        self.frame_right.grid(row=0, column=2, sticky='nsew')
        
        self.update_ui()

    def update_ui(self):
        print(f"Current phase : {self.game.phase}")
        print(f"Current sub phase : {self.game.sub_phase}")
        self.left()
        self.center()
        self.right()
        self._schedule_bot_turn()

    def _schedule_bot_turn(self) -> None:
        if self.role != "local" or not self.game.is_bot():
            return
        if self._bot_after_id is not None:
            self.root.after_cancel(self._bot_after_id)
        self._bot_after_id = self.root.after(450, self._run_bot_turn)

    def _run_bot_turn(self) -> None:
        self._bot_after_id = None
        if self.role != "local" or not self.game.is_bot():
            return
        if bot_ai.play_turn(self.game):
            self.update_ui()

    def _redraw_center_pawns(self):
        if self._board_canvas is None:
            return
        self._board_canvas.delete('pawns')
        pad = self._center_pad
        STEP_X = self._center_STEP_X
        STEP_Y = self._center_STEP_Y

        for player in self.game.players:
            for pawn in player.pawns:
                if pawn.state != "alive" or pawn.position is None:
                    continue
                x = self._center_pad_x + pawn.position[1] * STEP_X
                y = self._center_pad_y + pawn.position[0] * STEP_Y
                r_node = 10
                fill = self.colors[player.name.lower().replace(" ", "")]
                self._board_canvas.create_oval(
                    x - r_node, y - r_node, x + r_node, y + r_node,
                    fill=fill, outline=self.colors['border'], tags='pawns',
                )

    def _setup_center_board(self):
        current_color_int = self.game.boards.get_top().color_int
        color = f"layer{current_color_int}c"
        canvas_circle = tk.Canvas(
            self.frame_center,
            bg=self.colors["background"],
            highlightthickness=0,
        )
        self._canvas_circle = canvas_circle
        canvas_circle.pack(fill='both', expand=True)
        self._current_board_color = color

        def draw(event):
            self._canvas_circle.delete('all')
            w = event.width
            h = event.height

            cx = w // 2 # NE PAS TOUCHER
            cy = h // 2 - 70 # NE PAS TOUCHER
            r = min(w, h) // 2.5  # NE PAS TOUCHER
            STEP_X = int(r * 1.8 / (self._center_columns - 1))
            STEP_Y = int(r * 0.9 / (self._center_rows - 1)) * 1.7
            self._center_STEP_X = STEP_X
            self._center_STEP_Y = STEP_Y
            self._center_pad_x = cx - ((self._center_columns - 1) * STEP_X) // 2
            self._center_pad_y = cy - ((self._center_rows - 1) * STEP_Y) // 2
            self._canvas_circle.create_oval(
                cx - r,
                cy - r,
                cx + r,
                cy + r,
                fill=self.colors[self._current_board_color],
                outline=self.colors['border'],
                width=1,
            )
            
            grid = self.game.boards.get_top().to_2d_grid()
            for row in grid:
                print(row)
                
            
            for i in range(rows):
                for j in range(columns):
                    if grid[i][j] is None:
                        continue
                    x = self._center_pad_x + j * STEP_X
                    y = self._center_pad_y + i * STEP_Y
                    
                    if j + 2 < columns and grid[i][j + 2] is not None:
                        x2 = self._center_pad_x + (j + 2) * STEP_X
                        y2 = self._center_pad_y + i * STEP_Y
                        self._canvas_circle.create_line(x, y, x2, y2, fill=self.colors[f"layer{current_color_int}"], width=1)
                        
                    if i + 1 < rows and j - 1 >= 0 and grid[i + 1][j - 1] is not None:
                        x2 = self._center_pad_x + (j - 1) * STEP_X
                        y2 = self._center_pad_y + (i + 1) * STEP_Y
                        self._canvas_circle.create_line(x, y, x2, y2, fill=self.colors[f"layer{current_color_int}"], width=1)
    
                    if i + 1 < rows and j + 1 < columns and grid[i + 1][j + 1] is not None:
                        x2 = self._center_pad_x + (j + 1) * STEP_X
                        y2 = self._center_pad_y + (i + 1) * STEP_Y
                        self._canvas_circle.create_line(x, y, x2, y2, fill=self.colors[f"layer{current_color_int}"], width=1)
                    
            # 1ère couche : plateau (cases existantes)
            for r in range(rows):
                for c in range(columns):
                    if grid[r][c] is not None:
                        x = self._center_pad_x + c * STEP_X
                        y = self._center_pad_y + r * STEP_Y

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
                        x = self._center_pad_x + c * STEP_X
                        y = self._center_pad_y + r * STEP_Y

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

            self._redraw_center_pawns()

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

        self._board_canvas = canvas_circle

        
        canvas_circle.bind('<Configure>', draw)
        
        def get_click_coordinate(event):
            # Les coordonnées sont déjà relatives à canvas (la grille)
            grid_live = self.game.boards.get_top().to_2d_grid()
            c = round((event.x - self._center_pad_x) / self._center_STEP_X)
            r = round((event.y - self._center_pad_y) / self._center_STEP_Y)
            

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

            if (
                self.game.phase == "mouvement"
                and self.game.sub_phase in ("rejouer", "passer_tour")
            ):
                return

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
                        if self.game.sub_phase == "choix_pion":
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
                                    "type": (
                                        "choose_pawn"
                                        if self._cell_contains_current_player_pawn(row, col)
                                        else "move_chosen_pawn_to"
                                    ),
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
                if self.game.sub_phase == "choix_pion":
                    self.game.try_choose_pawn(row, col)
                    action = {"type": "choose_pawn", "row": row, "col": col}
                elif self.game.sub_phase == "deplacement":
                    if self.game.try_choose_pawn(row, col):
                        action = {"type": "choose_pawn", "row": row, "col": col}
                    elif self.game.try_move_chosen_pawn_to(
                        row, col, shuffle_disks=self._is_disk_shuffle_authority()
                    ):
                        action = {"type": "move_chosen_pawn_to", "row": row, "col": col}
                        self._send_disk_sync_if_needed()

            if self.role == "host" and action is not None:
                self.network.send_data(action)

            self.update_ui()

        self._board_canvas.bind('<Button-1>', gerer_clic)

    def _reload_center_board(self):
        """Detruit le plateau affiche pour le reconstruire apres un pop_top."""
        for widget in self.frame_center.winfo_children():
            widget.destroy()
        self._board_canvas = None
        self._canvas_circle = None

    def _is_local_turn(self) -> bool:
        return (
            self.role == "local"
            or self.game.current_player == self.local_player_id
        )

    def _send_network_action(self, action: dict) -> None:
        if self.role == "host":
            self.network.send_data(action)
        elif self.role == "client":
            self.network.send_action(action)

    def change_player_and_update(self):
        if not self._is_local_turn():
            return
        if self.role == "client":
            self._send_network_action({"type": "next_player"})
            return
        self.game.bonus_move = False
        self.game.current_player = (
            (self.game.current_player + 1) % len(self.game.players)
        )
        self.game.begin_player_turn()
        if self.role == "host":
            self._send_network_action({"type": "next_player"})
        self.update_ui()

    def replay_turn_and_update(self):
        if not self._is_local_turn():
            return
        if self.role == "client":
            self._send_network_action({"type": "replay_turn"})
            return
        self.game.start_bonus_turn()
        if self.role == "host":
            self._send_network_action({"type": "replay_turn"})
        self.update_ui()

    def play_turn_and_update(self):
        if not self._is_local_turn():
            return
        if self.role == "client":
            self._send_network_action({"type": "play_turn"})
            return
        self.game.sub_phase = "choix_disque"
        if self.role == "host":
            self._send_network_action({"type": "play_turn"})
        self.update_ui()


    # WIDGET PARTIE GAUCHE
    def left(self):
        # Évite la superpositon des widgets à chaque tour
        for w in self.frame_left.winfo_children():
            w.destroy()

        canvas_left = tk.Canvas(
            self.frame_left, bg=self.frame_left['bg'], highlightthickness=0, width=0, height=0
        )
        canvas_left.pack(fill='both', expand=True)

        # Récupération des infos d'un joueur
        def player(indice):
            return self.game.players[indice]

        def draw_left(event):
            # Évite l'accumulation de widgets à chaque redimensionnement
            canvas_left.delete('all')
            for w in canvas_left.winfo_children():
                w.destroy()

            w = event.width
            h = event.height

            # Titre de la manche
            if self.game.phase == 'placement':
                round_title = "Mise en place"
            else:
                round_title = self.game.boards.get_top().name # Attention risque de casser en mode custom

            label_round_title = tk.Label(
                canvas_left,
                text=round_title,
                font=('', 20, 'bold'),
                bg=self.colors['background']
            )
            label_round_title.place(relx=0.5, y=10, anchor='n')

            # Dimensions des cartes
            marge = 10
            titre_h = 50
            carte_w = w - 2 * marge
            carte_h = 150

            ''' Statut d'un joueur '''
            def player_status(p, y_carte):
                pnb = p.id + 1 # Traduit le nom en indice

                ''' Fond de la carte '''
                canvas_left.create_rectangle(
                    marge, y_carte,
                    marge + carte_w, y_carte + carte_h,
                    fill=self.colors[f'player{pnb}c'],
                    outline=self.colors['border'],
                    width=2
                )

                # Nom du joueur
                label_name = tk.Label(
                    canvas_left,
                    text=f"Joueur {pnb}",
                    font=('', 14),
                    bg=self.colors[f'player{pnb}c']
                )
                label_name.place(
                    x=marge + carte_w / 2,
                    y=y_carte + 8,
                    anchor='n'
                )

                ''' Pions restants '''
                frame_pawns = tk.Frame(canvas_left, bg=self.colors[f'player{pnb}c'])

                # Permet de retrouver l'image, peu importe le cwd (src: https://youtu.be/sv8YTbeObHQ?si=wzelL9Dx_BkA3ahx)
                cwd = os.path.dirname(__file__)
                png_path = os.path.join(cwd, "ressources/icons/mole.png")

                # Ajuste la taille de l'icon en fonction du nombre de taupes (soit en fonction du nombre de joueur)
                ''' À ajuster '''
                match len(self.game.players):
                    case 1 : # mode solo
                        dpxb = 40  
                    case 2 : 
                        dpxb = 40
                    case 3 : 
                        dpxb = 20
                    case 4 : 
                        dpxb = 16

                for pawn in p.pawns:
                    img = tk.PhotoImage(file=png_path).subsample(dpxb)
                    lbl_pawn = tk.Label(frame_pawns, image=img, bg=self.colors[f'player{pnb}c'])
                    lbl_pawn.image = img # Empêche le garbage collector de supprimer l'image
                    lbl_pawn.pack(side='left', padx=2)

                frame_pawns.place(
                    x=marge + carte_w / 2,
                    y=y_carte + 35,
                    anchor='n'
                )

                ''' Jetons déjà dévoilés (sur une seule ligne) '''
                frame_disks = tk.Frame(canvas_left, bg=self.colors[f'player{pnb}c'])

                diametre = 35
                data = p.disks.get_disks()

                for valeur, visible in data:
                    coin = tk.Canvas(
                        frame_disks,
                        width=diametre, height=diametre,
                        bg=self.colors[f'player{pnb}c'],
                        bd=0, highlightthickness=0
                    )
                    coin.create_oval(
                        0, 0, diametre, diametre,
                        fill=self.colors[f'player{pnb}'],
                        outline=self.colors['border'],
                        width=1
                    )
                    # Valeur si déjà dévoilé, sinon point d'interrogation (même principe que dans right())
                    texte = str(valeur) if visible else "?"
                    coin.create_text(
                        diametre / 2, diametre / 2,
                        text=texte,
                        font=('', 13),
                        fill=self.colors['white']
                    )
                    coin.pack(side='left', padx=3)

                frame_disks.place(
                    x=marge + carte_w / 2,
                    y=y_carte + carte_h - 8,
                    anchor='s'
                )

            ''' Affichage des statuts des joueurs '''
            for i in range(len(self.game.players)):
                y = titre_h + marge + i * (carte_h + marge)
                player_status(player(i), y)

        canvas_left.bind('<Configure>', draw_left)

    # WIDGET PARTIE CENTRE
    def center(self):
        board_rebuilt = False
        if self.game.consume_board_descent():
            self._reload_center_board()
            board_rebuilt = True
        if self._board_canvas is None:
            self._setup_center_board()
            board_rebuilt = True
        if not board_rebuilt:
            self._redraw_center_pawns()

    # WIDGET PARTIE DROITE
    def right(self):
        # Évite la superpositon des widgets à chaque tour
        for w in self.frame_right.winfo_children():
            w.destroy()

        canvas_right = tk.Canvas(
            self.frame_right, bg=self.frame_right['bg'], highlightthickness=0, width=0, height=0
        )
        canvas_right.pack(fill='both', expand=True)

        # Récupération des infos du joueur
        player = self.game.players[self.game.current_player]
        pnb = player.id + 1 # Traduit le nom en indice

        def draw_right(event):
            canvas_right.delete('all')
            w = event.width 
            h = event.height
            
            sizeW = w * 0.9
            sizeH = h * 0.5

            x0 = (w - sizeW) / 2
            y0 = 70
            x1 = x0 + sizeW
            y1 = y0 + sizeH

            ''' Cadre du menu '''
            canvas_right.create_rectangle(
                x0,
                x0,
                x1,
                70 - x0,
                fill=self.colors['background'],
                outline=self.colors['border'],
                width=2,
            )
            cwd = os.path.dirname(__file__)
            img_path = os.path.join(cwd, "ressources/pictures/sortie.png")
            self.img_quitter = tk.PhotoImage(file=img_path)
            self.img_quitter = self.img_quitter.subsample(16)
            btn_quitter = tk.Button(
                canvas_right,
                image=self.img_quitter,
                bg=self.colors['red'],
                bd=0, 
                relief='flat',
                command=self._popup_quitter,)
            canvas_right.create_window(220, 20, window=btn_quitter, anchor='ne')


            ''' Cadre du statut / actions en cours de la partie '''
            canvas_right.create_rectangle(
                x0,
                y0,
                x1,
                y1,
                fill=self.colors['background'],
                outline=self.colors['border'],
                width=2,
            )

            # Initialisation
            to_show = None

            # Titre (phase du jeu)
            match self.game.phase :
                case "placement":
                    text_title_phase = "Les joueurs place leurs taupes."
                    text_title_subphase = f"Le joueur {pnb} place une taupe"
                case "mouvement":
                    text_title_phase = "Allez à la couche inférieure !"
                case "victoire": 
                    text_title_phase = f"Le joueur {self.game.winner.name} a récupérer la pelle en premier !"
                    to_show = "victory"
                case _: 
                    text_title_phase = "⚠︎ Phase inconnue ⚠︎"
            
            label_title_phase = tk.Label(
                self.frame_right,
                text=text_title_phase,
                font=('', 16, 'bold'),
                bg=self.colors['background'],
                wraplength = sizeW * 0.8
            )
            label_title_phase.place(
                relx=0.5,
                y = y0 + sizeW*0.1,
                width= sizeW * 0.9,
                anchor='center'
            )

            # Action à réaliser (subphase)
            if self.game.phase != "placement": 
                        
                print(self.game.sub_phase)
                match self.game.sub_phase :
                    case "choix_disque":
                        text_title_subphase = f"Joueur {pnb} choisit un jeton :"
                        to_show = "disks"

                    case "choix_pion":
                        text_title_subphase = f"Joueur {pnb} choisit une taupe à déplacer."
                        to_show = "move"
                        if self.game.is_player_blocked() :
                            text_title_subphase = f"Joueur {pnb} ne peut déplacer aucune taupe.\nIl passe son tour."
                            to_show = "blocked"
                            self.game.sub_phase = "choix_disque"

                    case "deplacement": 
                        text_title_subphase = f"Cette taupe se déplace de {player.disks.get_disks()[player.disk_selected][0]} case(s)."
                        to_show = "move"

                    case "rejouer":
                        text_title_subphase = (
                            f"La taupe du joueur {pnb} est sur une case spéciale.\n"
                            "Il peut rejouer un coup."
                        )
                        to_show = "replay"

                    case "passer_tour":
                        if not self.game.has_pawns_on_board():
                            text_title_subphase = (
                                f"Le joueur {pnb} n'a plus de taupe sur le plateau.\n"
                                "Il passe son tour."
                            )
                        else:
                            text_title_subphase = (
                                f"Toutes les taupes du joueur {pnb} sont déjà dans un trou.\n"
                                "Il a le droit de passer son tour."
                            )
                        to_show = "can_pass"

                    case None:
                        text_title_subphase = "" 

                    case _: 
                        text_title_subphase = "⚠︎ Subphase inconnue ⚠︎" 
            
            label_title_subphase = tk.Label(
                self.frame_right,
                text=text_title_subphase,
                font=('', 14),
                bg=self.colors['background'],
                wraplength = sizeW * 0.9,
                justify='left'
            )
            label_title_subphase.place(
                relx=0.5,
                y = y0 + 100,
                width= sizeW * 0.9,
                anchor='center'
            )

            ''' Affichage de to_show '''
            match to_show:
                # Choix du disque 
                case "disks" :
                    # 
                    draw_disks(canvas_right, pnb, sizeW, sizeH)

                # Bouton suivant
                case "blocked" :
                    next_button(canvas_right, "Suivant", self.change_player_and_update,  "e")

                # Affiche le jeton de déplacement
                case "move" :
                    show_current_disk(canvas_right)

                # Joueur choisit si (re)joue ou pas
                case "replay" :
                    next_button(canvas_right, "Rejouer", self.replay_turn_and_update,  "w")
                    next_button(canvas_right, "Passer", self.change_player_and_update,  "e")

                case "can_pass" :
                    if self.game.has_pawns_on_board():
                        next_button(canvas_right, "Jouer", self.play_turn_and_update,  "w")
                    next_button(canvas_right, "Passer", self.change_player_and_update,  "e")

                # Victoire d'un joueur
                case "victory":
                    victory_player(canvas_right)

                # Autres
                case None :
                    to_show = to_show
                case _ : 
                    print("⚠︎ Error : 'to_show' inconnu ⚠︎")

        canvas_right.bind('<Configure>', draw_right)

        ''' Fonctions 'to_show' '''
        def draw_disks(parent, pnb, w, h):
            # Récupération des données sur les disques du joueur
            pcolor = f"player{pnb}"
            cur_player = player
            data = cur_player.disks.get_disks()

            # Condition pour cliquer sur un disque
            can_choose_disk = (
                self.game.phase == "mouvement"
                and self.game.sub_phase in (None, "choix_disque")
                and (
                    self.role == "local"
                    or self.game.current_player == self.local_player_id
                )
            )
            on_click = self._on_disk_click if can_choose_disk else None

            # Affichage des disques
            diametre = 60
            espace_x, espace_y = 85, 90


            for i, (valeur, visible) in enumerate(data):
                column = i % 3
                row = i // 3
                x = w/4 + espace_x * column
                y = h/1.5 + espace_y * row

                # Rend visible un jeton déjà selectionné
                if visible:
                    texte = str(valeur)
                    todo = ''
                else:
                    texte = "?"
                    todo = lambda idx=i: on_click(idx) if on_click else None # cree une fonction avec idx i en parametre et on_click en resultat
                    
                coins = tk.Canvas(parent, width=diametre, height=diametre,bg=parent['bg'], bd=0, highlightthickness=0)
            
                coins.create_oval(
                    0, 
                    0, 
                    diametre, 
                    diametre,
                    fill=self.colors[pcolor], 
                    outline=self.colors['border'], 
                    width=1)

                btn = tk.Button(
                    coins,
                    text=texte,
                    width=2,
                    height=1,
                    bg=self.colors[pcolor],
                    relief='flat', 
                    bd=0,
                    highlightthickness=0,
                    command=todo 
                )
            
                coins.create_window(
                    diametre/2,
                    diametre/2,
                    window=btn
                )  
                parent.create_window(
                    x,
                    y,
                    window = coins
                )  

        def show_current_disk(parent):
            pcolor = f"player{pnb}"
            current_disk = f"{player.disks.get_disks()[player.disk_selected][0]}"
            diameter = 85
            x = 91
            y = 350

            parent.create_oval(
                x, # 91
                y, # 350
                x + diameter, # 191
                y + diameter, # 450
                fill = self.colors[pcolor],
                width = 1
            )

            parent.create_text(
                (diameter)/2 + x, 
                (diameter)/2 + y,
                text = current_disk,
                font = ("", 20)
            )

        def next_button(parent, text, command, position,): 
        # parent, texte à afficher dans le bouton, action à effectuer via le bouton, position gauche ('w') ou droite ('e') dans le canvas
            match position:
                case 'w':
                    x = 0.3
                    color = self.colors['green']
                case 'e':
                    x = 0.6
                    color = self.colors['grey']

            button_next = tk.Button(
                parent, 
                text=text,
                width=4,
                height=2,
                bg=color,
                relief='flat',
                bd=1,
                command=command # Passe à la subphase suivante
                )
            
            button_next.pack()
            button_next.place(
                relx=x,
                rely=0.5
            )

        def victory_player(parent):
            
            joueur = {
                "Player 1": "joueur1.png",
                "Player 2": "joueur2.png",
                "Player 3": "joueur3.png",
                "Player 4": "joueur4.png",
            }
            cwd = os.path.dirname(__file__)
            img_path = os.path.join(cwd, "ressources/pictures/pelle.png")
            img = tk.PhotoImage(file=img_path)
            img = img.subsample(6)
            label = tk.Label(parent, image=img, bg=self.colors['background'])
            label.image = img
            img_joueur_path = os.path.join(cwd, f"ressources/pictures/{joueur[self.game.winner.name]}")
            img_joueur = tk.PhotoImage(file=img_joueur_path)
            img_joueur = img_joueur.subsample(6)
            label_joueur = tk.Label(parent, image=img_joueur, bg=self.colors['background'])
            label_joueur.image = img_joueur
            parent.create_window(parent.winfo_width()/2+50, parent.winfo_height()/2-100, window=label)
            parent.create_window(parent.winfo_width()/2-50, parent.winfo_height()/2-100, window=label_joueur)
            
            btn_quitter = tk.Button(
                parent,
                text="Suivant",
                command=victory_popup,
                bg=self.colors['layer101c'],
                width=10,
                height=2
            )
            
            parent.create_window(
                parent.winfo_width()/2,
                parent.winfo_height()/2,
                window=btn_quitter
            )


        def victory_popup():
            if tk.messagebox.askyesno("Rejouer","Voulez-vous rejouer ?"):
                self.root.destroy()
                import main
                main.main()
            else:
                self.root.destroy()

    
    def _popup_quitter(self):
        popup = tk.Toplevel(self.root)
        popup.title("Quitter")
        popup.geometry("350x150")
        popup.resizable(False, False)
        popup.grab_set()

        tk.Label(
            popup,
            text="Voulez-vous quitter la partie ?",
            font=('', 12),
            bg=self.colors['background'],
        ).pack(pady=15)

        frame_boutons = tk.Frame(popup, bg=self.colors['background'])
        frame_boutons.pack()

        tk.Button(
            frame_boutons, text="Annuler",
            bg=self.colors['grey'], bd=0, relief='flat',
            command=popup.destroy
        ).grid(row=0, column=0, padx=5)

        tk.Button(
            frame_boutons, text="Quitter sans sauvegarder",
            bg=self.colors['red'], bd=0, relief='flat',
            command=self.root.destroy
        ).grid(row=0, column=1, padx=5)

        tk.Button(
            frame_boutons, text="Quitter et sauvegarder",
            bg=self.colors['green'], bd=0, relief='flat',
            command=lambda: print("... sauvegarder ...")
        ).grid(row=0, column=2, padx=5)

    def _redraw_center_pawns(self):
        if self._board_canvas is None:
            return
        self._board_canvas.delete('pawns')
        step_x = self._center_STEP_X
        step_y = self._center_STEP_Y

        if self.game.phase == "mouvement" and self.game.sub_phase == "deplacement":
            joueur_actuel = self.game.players[self.game.current_player]
            pion_selectionne = joueur_actuel.pawn_selected
            if pion_selectionne is not None:
                pion = joueur_actuel.pawns[pion_selectionne]
                nombre_de_pas = joueur_actuel.disks.get_disks()[joueur_actuel.disk_selected][0]
                for ligne, colonne in self.game.get_possible_moves(pion, nombre_de_pas):
                    x = self._center_pad_x + colonne * step_x
                    y = self._center_pad_y + ligne * step_y
                    self._board_canvas.create_oval(
                        x - 15, y - 15, x + 15, y + 15,
                        outline=self.colors['white'],
                        fill='',
                        width=3,
                        tags='pawns'
                    )

        for joueur in self.game.players:
            for pion in joueur.pawns:
                if pion.state != "alive" or pion.position is None:
                    continue
                x = self._center_pad_x + pion.position[1] * step_x
                y = self._center_pad_y + pion.position[0] * step_y
                self._board_canvas.create_oval(
                    x - 10, y - 10, x + 10, y + 10,
                    fill=self.colors[joueur.name.lower().replace(" ", "")],
                    outline=self.colors['border'],
                    tags='pawns',
                )

        self._draw_selected_pawn_circle()

    def _draw_selected_pawn_circle(self) -> None:
        if self._board_canvas is None:
            return
        if self.game.phase != "mouvement":
            return

        current_player = self.game.players[self.game.current_player]
        pawn_index = current_player.pawn_selected
        if pawn_index is None or not (0 <= pawn_index < len(current_player.pawns)):
            return

        pawn = current_player.pawns[pawn_index]
        if pawn.state != "alive" or pawn.position is None:
            return

        x = self._center_pad_x + pawn.position[1] * self._center_STEP_X
        y = self._center_pad_y + pawn.position[0] * self._center_STEP_Y
        outline_color = self._get_selection_outline_color()

        self._board_canvas.create_oval(
            x - 18, y - 18, x + 18, y + 18,
            outline=outline_color,
            width=3,
            tags='pawns',
        )

    def _get_selection_outline_color(self) -> str:  #/couleeur de cercle a changer /
        board_color_key = getattr(self, '_current_board_color', None)
        if board_color_key in ("layer0", "layer0c"):
            return self.colors['red']
        if board_color_key in ("layer1", "layer1c"):
            return self.colors['black']
        if board_color_key in ("layer2", "layer2c"):
            return self.colors['black']
        if board_color_key in ("layer3", "layer3c"):
            return self.colors['white']
        return self.colors['white']

    def _is_disk_shuffle_authority(self) -> bool:
            """Seul l'hote (ou le local) melange les disques."""
            return self.role in ("local", "host")

    def _cell_contains_current_player_pawn(self, row: int, col: int) -> bool:
        current_player = self.game.players[self.game.current_player]
        return any(pawn.position == (row, col) for pawn in current_player.pawns)

    def _on_disk_click(self, idx: int) -> None:
        if self.role == "client":
            if self.game.current_player != self.local_player_id:
                return
            self.network.send_action(
                {"type": "choose_disk", "disk_selected": idx}
            )
            return

        if self.game.try_choose_disk(idx, self.update_ui):
            if self.role == "host":
                self.network.send_data(
                    {"type": "choose_disk", "disk_selected": idx}
                )
    
    def _send_disk_sync_if_needed(self) -> None:
        payload = self.game.consume_disk_sync()
        if payload is not None and self.role == "host":
            self.network.send_data({"type": "sync_disks", **payload})

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
            self.game.bonus_move = False
            self.game.current_player = (
                (self.game.current_player + 1) % len(self.game.players)
            )
            self.game.begin_player_turn()
        elif action_type == "replay_turn":
            self.game.start_bonus_turn()
        elif action_type == "play_turn":
            self.game.sub_phase = "choix_disque"
        elif action_type == "choose_disk":
            self.game.try_choose_disk(msg["disk_selected"], self.update_ui)
        elif action_type == "choose_pawn":
            self.game.try_choose_pawn(msg["row"], msg["col"])
        elif action_type == "move_chosen_pawn_to":
            if self.game.try_move_chosen_pawn_to(
                msg["row"],
                msg["col"],
                shuffle_disks=self._is_disk_shuffle_authority(),
            ):
                self._send_disk_sync_if_needed()
        elif action_type == "sync_disks":
            player_id = msg["player_id"]
            if 0 <= player_id < len(self.game.players):
                self.game.players[player_id].disks.set_disks(msg["disks"])
        self.update_ui()


    # Affichage de l'interface du jeu
    def displayInterface(self):
        self.root.mainloop()