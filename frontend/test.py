# Librairie
import tkinter as tk

class Interface:
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
        frame_main = tk.Frame(self.root, bg=self.colors['background'])
        frame_main.grid(row=0, column=0, sticky='nsew')
        frame_main.grid_rowconfigure(0, weight=1)
        frame_main.grid_columnconfigure(0, weight=1)
        frame_main.grid_columnconfigure(1, weight=2)
        frame_main.grid_columnconfigure(2, weight=1)


        ''' GAUCHE : Infos sur le statut des joueurs '''
        frame_left = tk.Frame(frame_main, bg="#A3E6AE")
        frame_left.grid(row=0, column=0, sticky='nsew')


        ''' CENTRE : Plateau de jeu '''
        frame_center = tk.Frame(frame_main, bg="#A7EEEB")
        frame_center.grid(row=0, column=1, sticky='nsew')
        self.center(frame_center)


        ''' DROITE : Infos sur la partie en cours '''
        frame_right = tk.Frame(frame_main, bg="#A3C9E6")
        frame_right.grid(row=0, column=2, sticky='nsew')
        
        

        player = (2, [["Jeton 1", True], ["Jeton 2", False], ["Jeton 3", True],
                            ["Jeton 4", False], ["Jeton 5", True], ["Jeton 6", False]])
        self.right(frame_right, player)
        
    # WIDGET PARTIE CENTRE
    def center(self, frame):
        canvas_circle = tk.Canvas(frame, bg=self.colors['background'], highlightthickness=0)
        canvas_circle.pack(fill='both', expand=True)
        
        def draw(event):
            canvas_circle.delete('all')
            w = event.width 
            h = event.height

            cx = w // 2 # NE PAS TOUCHER
            cy = h // 2 - 70 # NE PAS TOUCHER
            r = min(w, h) // 2.5  # NE PAS TOUCHER
            canvas_circle.create_oval(cx - r, cy - r, cx + r, cy + r, outline=self.colors['border'], width=1)

        canvas_circle.bind('<Configure>', draw)

        rows = 9
        columns = 17

        STEP_X = 50
        STEP_Y = 50

        PAD = 40
        canvas_w = (columns - 1) * STEP_X + 2 * PAD
        canvas_h = (rows - 1) * STEP_Y + 2 * PAD

        canvas = tk.Canvas(canvas_circle, width=canvas_w, height=canvas_h, bg=self.colors['background'], highlightthickness=0)
        canvas.place(relx=0.5, rely=0.5, anchor='center')

        # Grille de test : toutes les cases à "Case" (non None)
        grid = [[None,   None,   None,   None,   "Case", None,   "Case", None,   "Case", None,   "Case", None,   "Case", None,   None,   None,   None  ],  # r=0
                [None,   None,   None,   "Case", None,   None, None,   "Case", None,   "Case", None,   "Case", None,   "Case", None,   None,   None  ],  # r=1
                [None,   None,   "Case", None,   "Hole", None,   "Case", None,   "Special", None,   "Case", None,   "Case", None,   "Case", None,   None  ],  # r=2
                [None,   "Case", None,   "Case", None,   "Case", None,   None, None,   "Case", None,   "Case", None,   "Case", None,   "Case", None  ],  # r=3
                ["Special", None,   "Case", None,   "Case", None,   "Hole", None,   "Case", None, None, None,   "Special", None,   "Case", None,   "Case"],  # r=4
                [None,   "Case", None,   "Case", None,   "Case", None,   "Case", None,   "Case", None,   "Case", None,   "Case", None,   "Case", None  ],  # r=5
                [None,   None,   "Special", None,   "Case", None,   "Case", None,   "Case", None,   "Case", None,   "Case", None,   "Case", None,   None  ],  # r=6
                [None,   None,   None,   None, None,   "Case", None,   "Case", None,   "Hole", None,   "Case", None,   "Case", None,   None,   None  ],  # r=7
                [None,   None,   None,   None,   "Case", None,   "Case", None,   "Case", None,   "Case", None,   "Case", None,   None,   None,   None  ],  # r=8
            ]

        # 1ère couche : plateau (case, trous, cases spéciales)
        for r in range(rows):
            for c in range(columns):
                if grid[r][c] != None:
                    x = PAD + c * STEP_X
                    y = PAD + r * STEP_Y

                    match grid[r][c]:
                        case "Case":
                            r_node, size = 5,  self.colors['layer0']
                        case "Hole":
                            r_node, size = 20, self.colors['layer1']
                        case "Special":
                            r_node, size = 13,  self.colors['layer0']
                        case "J1":
                            r_node, size = 10,  self.colors['player1']
                        case "J2":
                            r_node, size = 10,  self.colors['player2']
                        case "J3":
                            r_node, size = 10,  self.colors['player3']
                        case "J4":
                            r_node, size = 10,  self.colors['player4']
                        case _:
                            r_node, size = 5,  self.colors['border']

                    canvas.create_oval(x - r_node, y - r_node, x + r_node, y + r_node, fill=size, outline='')

    # WIDGET PARTIE DROITE
    def right(self, frame, player):
        canvas_right = tk.Canvas(frame, highlightthickness=0,width=0,height=0)
        canvas_right.pack(fill='both', expand=True)

        name, disks = player
        label_round = tk.Label(frame, text=f"Au joueur {name}", bg=self.colors['white'], fg=self.colors['black'],anchor = "n" )

        def draw_right(event):
            
            canvas_right.delete('all')
            w = event.width 
            h = event.height
            
            size = min(w, h) * 0.6
            x0 = (w - size) / 2
            y0 = (h - size) / 2
            x1 = x0 + size
            y1 = y0 + size

            canvas_right.create_rectangle(x0, y0, x1, y1, fill=self.colors['white'], outline=self.colors['border'], width=3)
            label_round.place(x=w/2, y=h/2-40, anchor='center', width=size * 0.8, height=size * 0.35)
            label_round.lift()
            
            
            cx = w // 2 # NE PAS TOUCHER
            cy = h // 2 - 70 # NE PAS TOUCHER
            r = min(w, h) // 20  # NE PAS TOUCHER
            
            
            canvas_pions = tk.Canvas(canvas_right, highlightthickness=0, bg=self.colors['white'])
            canvas_right.create_window(cx, cy, window=canvas_pions, width=size * 0.7, height=size * 0.3)

            
        canvas_right.bind('<Configure>', draw_right)


    # Récupère la coordonnée du widget parent
    def get_click(self, event):
        x = event.x
        y = event.y

        # debug
        print(x)
        print(y)


    # Affichage de l'interface du jeu
    def displayInterface(self):
        self.root.mainloop()


if __name__=="__main__":
    ui = Interface()
    ui.displayInterface()