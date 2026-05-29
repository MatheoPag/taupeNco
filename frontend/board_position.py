# Librairie
import tkinter as tk

class Boards:
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
        self.root.title("Taupes&cie - Orientation des plateaux")
        self.root.geometry("800x800")
        self.root.minsize(800, 800)
        self.root.maxsize(800, 800)
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        self.root.tk_setPalette(
            background = self.colors['background'],
            foreground = self.colors['black'],
            activeBackground = self.colors['background'],
            activeForeground = self.colors['black'],
        )

        # Création du dictionnaire pour la configuration du mode de jeu
        self.position_config = {
            'layer0' : 0, 
            'layer1' : 0,
            'layer2' : 0,
            'layer3' : 0
        }

        # Création des pages
        self._build_wigets()


    def _build_wigets(self):

        ''' FOND DE L'INTERFACE '''
        self.frame_main = tk.Frame(self.root, bg=self.colors['background'])
        self.frame_main.grid(row=0, column=0, sticky='nsew')
            # Lignes
        self.frame_main.grid_rowconfigure(0, weight=1)
        self.frame_main.grid_rowconfigure(1, weight=5)
        self.frame_main.grid_rowconfigure(2, weight=1)
            # Colonnes
        self.frame_main.grid_columnconfigure(0, weight=1)

        ''' Titre '''
        label_title = tk.Label(
            self.frame_main,
            text="Orientation des plateaux :",
            font=('', 20),
            bg=self.colors['layer0'],
        )
        label_title.grid(row=0, column=0, columnspan=2, sticky='nsew')

        ''' Plateau à orienter '''
        # Frame des couches
        frame_layers = tk.Frame(self.frame_main, bg='red')
        frame_layers.grid(row=1, column=0, sticky='nsew')

        for j in range(2):
            frame_layers.grid_rowconfigure(j, weight=1)
            frame_layers.grid_columnconfigure(j, weight=1)

        # Couche 0
        frame_layer0 = tk.Frame(frame_layers, bg=self.colors['layer0c'])
        frame_layer0.grid(row=0, column=0, sticky='nsew')
        self.hexa_board(frame_layer0, 0)

        # Couche 1
        frame_layer1 = tk.Frame(frame_layers, bg=self.colors['layer1c'])
        frame_layer1.grid(row=0, column=1, sticky='nsew')

        # Couche 2
        frame_layer2 = tk.Frame(frame_layers, bg=self.colors['layer2c'])
        frame_layer2.grid(row=1, column=0, sticky='nsew')

        # Couche 3
        frame_layer3 = tk.Frame(frame_layers, bg=self.colors['layer3c'])
        frame_layer3.grid(row=1, column=1, sticky='nsew')


        ''' Bouton de validation '''
        # Création d'une frame pour dimensonner le bouton
        frame_button = tk.Frame(self.frame_main, bg=self.colors['layer2'])
        frame_button.grid(row=2, column=0, sticky='nsew')

        for i in range(3):
            frame_button.grid_rowconfigure(i, weight=1)
            frame_button.grid_columnconfigure(i, weight=1)

        # Placement du bouton
        button_start = tk.Button(
            frame_button,
            text="Lancer la partie",
            font=('', 20),
            bg=self.colors['green'],
            bd=0,
            relief='flat',
            command=self.root.destroy
        )
        button_start.grid(row=1, column=1, sticky='nsew', padx=100)



    # Gestion de l'orientation d'un plateau
    def hexa_board(self, frame, layer):
        png = { # Change la couleur du png en fonction de la couche
            0 : "frontend/ressources/pictures/hexa-test.png",
            1 : "frontend/ressources/pictures/hexa-test.png",
            2 : "frontend/ressources/pictures/hexa-test.png",
            3 : "frontend/ressources/pictures/hexa-test.png",
        }

        w, h = 100, 100

        image_board = tk.PhotoImage(file=png[layer]).zoom(1).subsample(10)
        canvas_board = tk.Canvas(frame, width=w, height=h, bg=self.colors['layer1c'], bd=0, highlightthickness=0)
        canvas_board.create_image(w/2, h/2, image=image_board)
        canvas_board.image = image_board
        canvas_board.pack(expand='YES')


    
    # Affichage des pages
    def display(self):
        self.root.mainloop()

        print(self.position_config) # debug
        return self.position_config


if __name__ == "__main__":
    menu = Boards()
    menu.display()   