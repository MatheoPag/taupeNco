# Librairie
import tkinter as tk

class Menu:
    def __init__(self):
        # Palette de couleur
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
        self.root.geometry("360x480")
        self.root.minsize(360, 480)
        self.root.maxsize(360, 480)
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        self.root.config(bg = self.colors['background'])

        # Création du dictionnaire pour la configuration du mode de jeu
        self.game_config = {
            'connexionmode' : None, # local OU multiplayer
            'gamemode' : None, # classic OU custom
            'nbplayer' : tk.IntVar(value=1), # 1, 2, 3 ou 4
            'nbbot' : tk.IntVar(value=2), # 0, 1, 2 ou 3
        }

        # Création des pages
        self._build_pages()


    # Construction des pages
    def _build_pages(self):

        # FENÊTRE D'ACCUEIL
        frame_connexion_mode = tk.Frame(self.root, bg=self.colors['background'])
        frame_connexion_mode.grid(row=0, column=0, sticky='nsew')
        frame_connexion_mode.grid_rowconfigure(0, weight=1)
        frame_connexion_mode.grid_rowconfigure(1, weight=1)
        frame_connexion_mode.grid_rowconfigure(2, weight=1)
        frame_connexion_mode.grid_columnconfigure(0, weight=1)

        label_title = tk.Label(frame_connexion_mode, text="Taupes & compagnie", font=('', 24), bg=self.colors['background'])
        label_title.grid(row=0, column=0, sticky='nsew')

        label_welcome_title = tk.Label(frame_connexion_mode, text="Choisissez un mode de connexion :", font=('', 16), bg=self.colors['background'])
        label_welcome_title.grid(row=1, column=0, sticky='nsew')

        frame_button_connexion = tk.Frame(frame_connexion_mode, bg=self.colors['background'])
        frame_button_connexion.grid(row=2, column=0, sticky='nsew')

        frame_button_local = tk.Frame(frame_button_connexion, bg=self.colors['border'], padx=2, pady=2)
        frame_button_local.pack(padx=20, pady=20, ipady=10, fill='x')
        button_local = tk.Button(frame_button_local, text="Local", font=('', 16), bg=self.colors['grey'], bd=0, relief='flat')
        button_local.pack(fill='both', expand=True)

        frame_button_online = tk.Frame(frame_button_connexion, bg=self.colors['border'], padx=2, pady=2)
        frame_button_online.pack(padx=20, pady=20, ipady=10, fill='x')
        button_online = tk.Button(frame_button_online, text="Multijoueur en ligne", font=('', 16), bg=self.colors['grey'], bd=0, relief='flat')
        button_online.pack(fill='both', expand=True)

        frame_button_quit = tk.Frame(frame_button_connexion, bg=self.colors['border'], padx=2, pady=2)
        frame_button_quit.pack(padx=20, pady=20, ipady=10, fill='x')
        button_quit = tk.Button(frame_button_quit, text="Quitter le jeu", font=('', 16), bg=self.colors['red'], bd=0, relief='flat')
        button_quit.pack(fill='both', expand=True)


        # FENÊTRE DU CHOIX DU MODE DE JEU
        frame_game_mode = tk.Frame(self.root, width=352, height=472, bg=self.colors['background'])
        frame_game_mode.grid(row=0, column=0, sticky='nsew')

        label_title = tk.Label(frame_game_mode, text="Mode local", font=('', 24), bg=self.colors['background'])
        label_title.pack()

        label_player_title = tk.Label(frame_game_mode, text="Nombre de joueur : ", font=('', 16), bg=self.colors['background'])
        label_player_title.pack()

        frame_button_player = tk.Frame(frame_game_mode, bg=self.colors['border'], padx=2, pady=2)
        frame_button_player.pack(padx=20, pady=20)
        frame_button_player.grid_rowconfigure(0, weight=1)
        frame_button_player.grid_columnconfigure(3, weight=1)

        button_player1 = tk.Radiobutton(frame_button_player,text="j1", variable=self.game_config['nbplayer'], value = 1,command=self.max_bot)
        button_player2 = tk.Radiobutton(frame_button_player,text="j2", variable=self.game_config['nbplayer'], value = 2,command=self.max_bot)
        button_player3 = tk.Radiobutton(frame_button_player,text="j3", variable=self.game_config['nbplayer'], value = 3,command=self.max_bot)
        button_player4 = tk.Radiobutton(frame_button_player,text="j4" , variable=self.game_config['nbplayer'], value = 4,command=self.max_bot)
        button_player1.grid(row=0, column=0)
        button_player2.grid(row=0, column=1)
        button_player3.grid(row=0, column=2)
        button_player4.grid(row=0, column=3)

        frame_button_bot = tk.Frame(frame_game_mode, bg=self.colors['border'], padx=2, pady=2)
        frame_button_bot.pack(padx=30, pady=30)
        frame_button_bot.grid_rowconfigure(0, weight=1)
        frame_button_bot.grid_columnconfigure(3, weight=1)

        button_bot1 = tk.Radiobutton(frame_button_bot,text="sans bot", variable=self.game_config['nbbot'], value = 1,command=self.max_bot)
        button_bot2 = tk.Radiobutton(frame_button_bot,text="1bot", variable=self.game_config['nbbot'], value = 2,command=self.max_bot)
        button_bot3 = tk.Radiobutton(frame_button_bot,text="2bot", variable=self.game_config['nbbot'], value = 3,command=self.max_bot)
        button_bot4 = tk.Radiobutton(frame_button_bot,text="3bot" , variable=self.game_config['nbbot'], value = 4,command=self.max_bot)
        button_bot1.grid(row=0, column=0)
        button_bot2.grid(row=0, column=1)
        button_bot3.grid(row=0, column=2)
        button_bot4.grid(row=0, column=3)

        label_gamemode_title = tk.Label(frame_game_mode, text="Mode de jeu : ", font=('', 16), bg=self.colors['background'])
        label_gamemode_title.pack()

        frame_button_normal = tk.Frame(frame_game_mode, bg=self.colors['border'], padx=2, pady=2)
        frame_button_normal.pack(padx=20, pady=20)
        button_normal = tk.Button(frame_button_normal, text="Classique", font=('', 16), bg=self.colors['layer0'], bd=0, relief='flat')
        button_normal.pack()

        frame_button_custom = tk.Frame(frame_game_mode, bg=self.colors['border'], padx=2, pady=2)
        frame_button_custom.pack(padx=20, pady=20)
        button_custom = tk.Button(frame_button_custom, text="Personnalisé", font=('', 16), bg=self.colors['layer0'], bd=0, relief='flat')
        button_custom.pack()

        frame_button_back1 = tk.Frame(frame_game_mode, bg=self.colors['border'], padx=2, pady=2)
        frame_button_back1.pack(padx=20, pady=20)
        button_back1 = tk.Button(frame_button_back1, text="Retour", font=('', 16), bg=self.colors['layer0'], bd=0, relief='flat')
        button_back1.pack()

        # GESTION DE LA SUPERPOSITION DES COUCHES

            # Initialisation sur la page d'acceuil
        frame_connexion_mode.tkraise()

            # Boutons de la page d'accueil
        button_local.config(command=frame_game_mode.tkraise)
        button_quit.config(command=self.root.destroy)

            # Boutons de la page configuration d'une partie
        button_back1.config(command=frame_connexion_mode.tkraise)

    # Évite des parties à plus de 4 'entités' (joueur ou bot)
    def max_bot(self):
        nb_players = self.game_config['nbplayer'].get()

        max_bots = 5 - nb_players
        nb_bots = self.game_config['nbbot'].get()

        if nb_bots > max_bots :
            self.game_config['nbbot'].set(max_bots)

        if nb_players == 1 and self.game_config['nbbot'].get() == 1: # Un joueur seul, joue forcément avec un bot
            self.game_config['nbbot'].set(2)

    # Affichage des pages
    def display(self):
        self.root.mainloop()


if __name__ == "__main__":
    game = Menu()
    game.display()


