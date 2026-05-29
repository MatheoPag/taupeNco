# Librairie
import tkinter as tk
from tkinter import messagebox
import pygame
from system.server import get_local_ip
from frontend.board_position import Boards

class Menu:
    def __init__(self):
        # Palette de couleur
        self.colors = {
            # Main
            'background' : '#EDECED',
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
        self.root.geometry("360x480")
        self.root.minsize(360, 480)
        self.root.maxsize(360, 480)
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        self.root.tk_setPalette(
            background = self.colors['background'],
            foreground = self.colors['black'],
            activeBackground = self.colors['background'],
            activeForeground = self.colors['black'],
        )
        self.root.config(cursor='trek')

        # Création du dictionnaire pour la configuration du mode de jeu
        self.game_config = {
            'connexionmode' : None, # local OU multiplayer
            'gamemode' : None, # classic, solobot OU custom
            'nbboard' : tk.IntVar(value=3), # mode perso : 3 à 6 plateaux
            'nbplayer' : tk.IntVar(value=3), # 2, 3 ou 4
            'iphost' : None, # Adresse IP de l'host d'une partie
            'iptarget' : tk.StringVar(value="127.0.0.1"), # Adresse IP pour rejoindre l'host
            'board_orientation' : [0, 0, 0, 0, 0, 0],
        }
        self._pending_gamemode = None
        self._pending_nbboard = None
        self._board_position_return_frame = None

        # Lancement de la musique du menu
        #self.play_music()

        # Création des pages
        self._build_pages()
    
    # Musique du menu
    def play_music(self):
        song = pygame.mixer.music
        song.init()
        song.load("frontend/ressources/musics/Overture_Super-Mario-Galaxy.mp3")
        song.play(-1)


    # Construction des pages
    def _build_pages(self):

        # FENÊTRE D'ACCUEIL
        frame_connexion_mode = tk.Frame(self.root, bg=self.colors['background'])
        frame_connexion_mode.grid(row=0, column=0, sticky='nsew')
        frame_connexion_mode.grid_rowconfigure(0, weight=1)
        frame_connexion_mode.grid_rowconfigure(1, weight=1)
        frame_connexion_mode.grid_rowconfigure(2, weight=3)
        frame_connexion_mode.grid_columnconfigure(0, weight=1)
        
            # Titre    
        label_title = tk.Label(
            frame_connexion_mode,
            text="Taupes & compagnie",
            font=('', 24),
            bg=self.colors['background'],
        )
        label_title.grid(row=0, column=0, sticky='nsew')

            # Sous-titre
        label_sub_title = tk.Label(
            frame_connexion_mode,
            text="Choisissez un mode de jeu :",
            font=('', 16),
            bg=self.colors['background'],
        )
        label_sub_title.grid(row=1, column=0, sticky='nsew')

            # Frame des boutons
        frame_buttons = tk.Frame(
            frame_connexion_mode, bg=self.colors['background']
        )
        frame_buttons.grid(row=2, column=0, sticky='nsew')

            # 1 - Mode ordinateur
        frame_button_bot = tk.Frame(
            frame_buttons, bg=self.colors['border'], padx=2, pady=2
        )
        frame_button_bot.pack(padx=50, pady=0, ipady=5, fill='x', expand=True)
        button_bot = tk.Button(
            frame_button_bot,
            text="Solo",
            font=('', 16),
            bg=self.colors['grey'],
            bd=0,
            relief='flat',
        )
        button_bot.pack(fill='both', expand=True)

            # 2 - Mode local
        frame_button_local = tk.Frame(
            frame_buttons, bg=self.colors['border'], padx=2, pady=2
        )
        frame_button_local.pack(padx=50, pady=0, ipady=5, fill='x', expand=True)
        button_local = tk.Button(
            frame_button_local,
            text="Multijoueur local",
            font=('', 16),
            bg=self.colors['grey'],
            bd=0,
            relief='flat',
        )
        button_local.pack(fill='both', expand=True)

        

            # 3 - Mode en ligne
        frame_button_online = tk.Frame(
            frame_buttons, bg=self.colors['border'], padx=2, pady=2
        )
        frame_button_online.pack(padx=50, pady=0, ipady=5, fill='x', expand=True)
        button_online = tk.Button(
            frame_button_online,
            text="Multijoueur en ligne",
            font=('', 16),
            bg=self.colors['grey'],
            bd=0,
            relief='flat',
        )
        button_online.pack(fill='both', expand=True)

            # 4 - Quitter le jeu
        frame_button_quit = tk.Frame(
            frame_buttons, bg=self.colors['border'], padx=2, pady=2
        )
        frame_button_quit.pack(padx=70, pady=0, fill='x', expand=True)
        button_quit = tk.Button(
            frame_button_quit,
            text="Quitter le jeu",
            font=('', 16),
            bg=self.colors['red'],
            bd=0,
            relief='flat',
            cursor='pirate'
        )
        button_quit.pack(fill='both', expand=True)


        # FENÊTRE DU CHOIX DU MODE DE JEU (local)
        (
            self.frame_local_mode,
            button_classic,
            button_custom,
            button_back1,
        ) = self._build_game_mode_page("Mode local", show_player_count=True)

        # FENÊTRE DU CHOIX DU MODE DE JEU (solo)
        (
            self.frame_solo_mode,
            button_solo_classic,
            button_solo_custom,
            button_back_solo,
        ) = self._build_game_mode_page("Mode solo", show_player_count=False)

        # FENÊTRE DU CHOIX DU MODE DE JEU (multijoueur en ligne)
        (
            self.frame_multiplayer_game_mode,
            button_multi_classic,
            button_multi_custom,
            button_back_multi_config,
        ) = self._build_game_mode_page("Multijoueur en ligne", show_player_count=True)

        # FENÊTRE ORIENTATION DES PLATEAUX
        self.frame_board_position = tk.Frame(self.root, bg=self.colors['background'])
        self.frame_board_position.grid(row=0, column=0, sticky='nsew')
        self.frame_board_position.grid_rowconfigure(0, weight=1)
        self.frame_board_position.grid_columnconfigure(0, weight=1)

        Boards(
            parent=self.frame_board_position,
            on_finish=self._finish_board_position,
        )

        frame_button_back_board = tk.Frame(
            self.frame_board_position, bg=self.colors['border'], padx=2, pady=2
        )
        frame_button_back_board.grid(row=1, column=0, sticky='ew', padx=20, pady=10)
        button_back_board = tk.Button(
            frame_button_back_board,
            text="Retour",
            font=('', 16),
            bg=self.colors['layer0'],
            bd=0,
            relief='flat',
            command=self._leave_board_position,
        )
        button_back_board.pack()
        
        # FENÊTRE MULTIJOUEUR
        frame_multiplayer_mode = tk.Frame(self.root, bg=self.colors['background'])
        frame_multiplayer_mode.grid(row=0, column=0, sticky='nsew')
        frame_multiplayer_mode.grid_rowconfigure(0, weight=1)
        frame_multiplayer_mode.grid_rowconfigure(1, weight=1)
        frame_multiplayer_mode.grid_rowconfigure(2, weight=1)
        frame_multiplayer_mode.grid_columnconfigure(0, weight=1)

        label_title = tk.Label(
            frame_multiplayer_mode,
            text="Multijoueur en ligne",
            font=('', 24),
            bg=self.colors['background'],
        )
        label_title.grid(row=0, column=0, sticky='nsew')

        label_join = tk.Label(
            frame_multiplayer_mode,
            text="ID d'une partie (host) :",
            font=('', 16),
            bg=self.colors['background'],
        )
        label_join.grid(row=1, column=0, sticky='nsew')
        
        self.entry_ip = tk.Entry(
            frame_multiplayer_mode,
            font=('', 12),
            textvariable=self.game_config['iptarget'],
        )
        self.entry_ip.grid(row=3, column=0, sticky='nsew') 
        
        frame_button_join = tk.Frame(
            frame_multiplayer_mode, bg=self.colors['border'], padx=2, pady=2
        )
        frame_button_join.grid(row=4, column=0, sticky='nsew')
        button_join = tk.Button(
            frame_button_join,
            text="Rejoindre une partie",
            font=('', 16),
            bg=self.colors['layer0'],
            bd=0,
            relief='flat',
            command=self.join_online_game,
        )
        button_join.pack()
        
        frame_button_create = tk.Frame(
            frame_multiplayer_mode, bg=self.colors['border'], padx=2, pady=2
        )
        frame_button_create.grid(row=5, column=0, sticky='nsew')
        button_create = tk.Button(
            frame_button_create ,
            text="Créer une partie",
            font=('', 16),
            bg=self.colors['layer0'],
            bd=0,
            relief='flat',
            command=lambda: self.frame_multiplayer_game_mode.tkraise(),
        )
        button_create.pack()
        
        frame_button_back2 = tk.Frame(
            frame_multiplayer_mode, bg=self.colors['border'], padx=2, pady=2
        )
        frame_button_back2.grid(row=6, column=0, sticky='nsew')
        button_back2 = tk.Button(
            frame_button_back2,
            text="Retour",
            font=('', 16),
            bg=self.colors['layer0'],
            bd=0,
            relief='flat',
        )
        button_back2.pack()


        # GESTION DE LA SUPERPOSITION DES COUCHES
            # Initialisation sur la page d'acceuil
        frame_connexion_mode.tkraise()

            # Boutons de la page d'accueil
        button_bot.config(command=lambda: self.set_connexion_solo(self.frame_solo_mode))
        button_local.config(command=lambda : self.set_connexion_local(self.frame_local_mode))
        button_online.config(
            command=lambda : self.set_connexion_multiplayer(frame_multiplayer_mode)
        )
        button_quit.config(command=self.root.destroy)
        
            # Boutons de la page configuration d'une partie (local)
        button_classic.config(command=self.create_local_classic)
        button_custom.config(command=self.create_local_custom)
        button_back1.config(command=lambda: frame_connexion_mode.tkraise())

            # Boutons de la page configuration d'une partie (solo)
        button_solo_classic.config(command=self.create_solo_classic)
        button_solo_custom.config(command=self.create_solo_custom)
        button_back_solo.config(command=lambda: frame_connexion_mode.tkraise())

            # Boutons de la page configuration d'une partie (multijoueur en ligne)
        button_multi_classic.config(command=self.create_multiplayer_classic)
        button_multi_custom.config(command=self.create_multiplayer_custom)
        button_back_multi_config.config(
            command=lambda: frame_multiplayer_mode.tkraise()
        )
        
            # Boutons de la page multijoueur (lobby)
        button_back2.config(command=lambda: frame_connexion_mode.tkraise())


    def _build_game_mode_page(self, title_text, show_player_count=True):
        """Construit une page de choix du mode de jeu (classique/personnalisé)."""
        frame = tk.Frame(self.root, width=352, height=472, bg=self.colors['background'])
        frame.grid(row=0, column=0, sticky='nsew')

        label_title = tk.Label(
            frame, text=title_text, font=('', 24), bg=self.colors['background']
        )
        label_title.pack()

        if show_player_count:
            label_player_title = tk.Label(
                frame,
                text="Nombre de joueur : ",
                font=('', 16),
                bg=self.colors['background'],
            )
            label_player_title.pack()

            frame_button_player = tk.Frame(frame, bg=self.colors['border'], padx=2, pady=2)
            frame_button_player.pack(padx=20, pady=20)
            frame_button_player.grid_rowconfigure(0, weight=1)
            frame_button_player.grid_columnconfigure(2, weight=1)

            button_player2 = tk.Radiobutton(
                frame_button_player,
                text="j2",
                variable=self.game_config['nbplayer'],
                value=2
            )
            button_player3 = tk.Radiobutton(
                frame_button_player,
                text="j3",
                variable=self.game_config['nbplayer'],
                value=3
            )
            button_player4 = tk.Radiobutton(
                frame_button_player,
                text="j4",
                variable=self.game_config['nbplayer'],
                value=4
            )
            button_player2.grid(row=0, column=0)
            button_player3.grid(row=0, column=1)
            button_player4.grid(row=0, column=2)

        label_gamemode_title = tk.Label(
            frame,
            text="Mode de jeu : ",
            font=('', 16),
            bg=self.colors['background'],
        )
        label_gamemode_title.pack()

        frame_button_classic = tk.Frame(frame, bg=self.colors['border'], padx=2, pady=2)
        frame_button_classic.pack(padx=20, pady=20)
        button_classic = tk.Button(
            frame_button_classic,
            text="Classique",
            font=('', 16),
            bg=self.colors['layer0'],
            bd=0,
            relief='flat',
        )
        button_classic.pack()

        # Choix du nombre de plateaux en mode custom
        label_gamemode_custom = tk.Label(
            frame,
            text="Nombre de plateaux\n(uniquement en personnalisé) : ",
            font=('', 16),
            bg=self.colors['background'],
        )
        label_gamemode_custom.pack()

        frame_button_board = tk.Frame(frame, bg=self.colors['border'], padx=2, pady=2)
        frame_button_board.pack(padx=20, pady=20)
        frame_button_board.grid_rowconfigure(0, weight=1)
        frame_button_board.grid_columnconfigure(3, weight=1)

        button_board3 = tk.Radiobutton(
            frame_button_board,
            text="3",
            variable=self.game_config['nbboard'],
            value=3
        )
        button_board4 = tk.Radiobutton(
            frame_button_board,
            text="4",
            variable=self.game_config['nbboard'],
            value=4
        )
        button_board5 = tk.Radiobutton(
            frame_button_board,
            text="5",
            variable=self.game_config['nbboard'],
            value=5
        )
        button_board6 = tk.Radiobutton(
            frame_button_board,
            text="6",
            variable=self.game_config['nbboard'],
            value=6
        )
        button_board3.grid(row=0, column=0)
        button_board4.grid(row=0, column=1)
        button_board5.grid(row=0, column=2)
        button_board6.grid(row=0, column=3)

        frame_button_custom = tk.Frame(frame, bg=self.colors['border'], padx=2, pady=2)
        frame_button_custom.pack(padx=20, pady=20)
        button_custom = tk.Button(
            frame_button_custom,
            text="Personnalisé",
            font=('', 16),
            bg=self.colors['layer0'],
            bd=0,
            relief='flat',
        )
        button_custom.pack()

        frame_button_back = tk.Frame(frame, bg=self.colors['border'], padx=2, pady=2)
        frame_button_back.pack(padx=20, pady=20)
        button_back = tk.Button(
            frame_button_back,
            text="Retour",
            font=('', 16),
            bg=self.colors['layer0'],
            bd=0,
            relief='flat',
        )
        button_back.pack()

        return frame, button_classic, button_custom, button_back

    
    # Ajuste la configuration de la partie en fonction du type de jeu 
    def set_connexion_local(self, frame):
        frame.tkraise()
        self.game_config['connexionmode']='local'

    def set_connexion_solo(self, frame):
        frame.tkraise()
        self.game_config['connexionmode'] = 'local'

    def set_connexion_multiplayer(self, frame):
        frame.tkraise()
        self.game_config['connexionmode']='multiplayer'

    def set_connexion_none(self, frame):
        frame.tkraise()
        self.game_config['connexionmode']='None'


    def _start_game(self, gamemode, nbboard, board_orientation=None):
        """Configure la partie et ferme le menu pour lancer le jeu."""
        if board_orientation is None:
            board_orientation = [0, 0, 0, 0, 0, 0]
        if gamemode == 'solobot':
            self.game_config['nbplayer'] = 1
        else:
            nbplayer = self.game_config['nbplayer']
            self.game_config['nbplayer'] = (
                nbplayer.get() if hasattr(nbplayer, 'get') else nbplayer
            )
        self.game_config['board_orientation'] = board_orientation
        self.game_config['gamemode'] = gamemode
        self.game_config['nbboard'] = nbboard
        if self.game_config['connexionmode'] == 'multiplayer':
            self.game_config['iphost'] = get_local_ip()
            self.game_config['iptarget'] = 'None'
        else:
            self.game_config['iphost'] = 'None'
            self.game_config['iptarget'] = 'None'
        self.root.destroy()

    def _show_board_position(self, return_frame, gamemode, nbboard):
        """Affiche la page d'orientation des plateaux avant de lancer la partie."""
        self._board_position_return_frame = return_frame
        self._pending_gamemode = gamemode
        self._pending_nbboard = nbboard
        self.root.geometry("800x800")
        self.root.minsize(800, 800)
        self.root.maxsize(800, 800)
        self.frame_board_position.tkraise()

    def _leave_board_position(self):
        self.root.geometry("360x480")
        self.root.minsize(360, 480)
        self.root.maxsize(360, 480)
        if self._board_position_return_frame is not None:
            self._board_position_return_frame.tkraise()

    def _finish_board_position(self, orientations):
        if self._pending_nbboard == 4 and len(orientations) == 4:
            orientations = [0, 0] + list(orientations)
        self._start_game(self._pending_gamemode, self._pending_nbboard, orientations)


    # CONFIG LOCAL 
        # Renvoi la configuration de la partie (locale)
    def create_local_classic(self):
        self._show_board_position(self.frame_local_mode, 'classic', 4)

    def create_local_custom(self):
        self._start_game('custom', self.game_config['nbboard'].get())

    def create_solo_classic(self):
        self._show_board_position(self.frame_solo_mode, 'solobot', 4)

    def create_solo_custom(self):
        self._start_game('solobot', self.game_config['nbboard'].get())

    # CONFIG MULTIJOUEUR (hôte)
    def create_multiplayer_classic(self):
        self._show_board_position(self.frame_multiplayer_game_mode, 'classic', 4)

    def create_multiplayer_custom(self):
        self._start_game('custom', self.game_config['nbboard'].get())


    # CONFIG ONLINE
        # Vérifie la conformité de l'adresse IP
    def check_ip(self, ip):
        parts = ip.split('.')
        
        if len(parts) != 4:
            return False
        
        try:
            p1 = int(parts[0])
            p2 = int(parts[1])
            p3 = int(parts[2])
            p4 = int(parts[3])
        except:
            return False

        if p1 == 1 and p2 == 1 and p3 == 1 and p4 == 1:
            return False
        
        if not (1 <= p1 <= 255):
            return False
        if not (0 <= p2 <= 255):
            return False
        if not (0 <= p3 <= 255):
            return False
        if not (1 <= p4 <= 254):
            return False
        return True

    
    # Si l'adresser IP est valide, elle est stockée dans game_config
    def join_online_game(self):
        ip = self.entry_ip.get()

        if self.check_ip(ip):
            self.game_config['gamemode'] = None
            self.game_config['nbplayer'] = None
            self.game_config['iphost'] = 'None'
            self.game_config['iptarget'] = ip
            self.root.destroy()
        else:
            messagebox.showwarning("Erreur", "L'adresse IP n'est pas conforme. Veuillez entrer l'adresse au bon format. (ex: 192.168.1.76)")


    # Affichage des pages
    def display(self):
        self.root.mainloop()

        return self.game_config


if __name__ == "__main__":
    menu = Menu()
    menu.display()