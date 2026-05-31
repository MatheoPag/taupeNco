import copy

class Board:
    def __init__(self, 
                size: int, 
                color: str | tuple[int, str], 
                markers: dict[str, list[tuple[int, int]]], 
                orientation: int) -> None:
        if size % 2 == 0:
            raise ValueError("La taille doit etre impaire")
        if size <= 0:
            raise ValueError("La taille doit etre strictement positive")
        self.size = size
        self.radius = size // 2


        LAYER_UI_INDEX = {
            "Pierre": 101,
            "Terre": 102,
            "Surface": 0,
            "Terre arable": 1,
            "Sous-sol": 2,
            "Roche mère": 3,
        }

        if isinstance(color, str):
            self.name = color
            self.color_int = LAYER_UI_INDEX[color]
        else:
            self.color_int = color[0]
            self.name = color[1]
        self.grid = self._generate_grid()
        self.center = (0, 0)
        self.markers = markers
        self._apply_markers()
        
        for i in range(orientation):
            self.rotate_60()

    def _rotate_axial_60(self, q: int, r: int) -> tuple[int, int]:
        """Rotation de +60 deg en plan hexagonal.
        s = -q - r
        (q, r, s) -> (-r, -s, -q)
        """
        s = -q - r
        new_q, new_r = -r, -s
        return new_q, new_r

    def rotate_60(self) -> None:
        """Recalcule les coordonnees des marqueurs du plateau apres +60 deg."""
        for kind in ("X", "S", "J"):
            rotated = []
            for q, r in self.markers.get(kind, []):
                new_q, new_r = self._rotate_axial_60(q, r)
                if (new_q, new_r) not in self.grid:
                    raise ValueError(f"Rotation 60 deg : ({q}, {r}) \
                    sort du plateau -> ({new_q}, {new_r})")
                rotated.append((new_q, new_r))
            self.markers[kind] = rotated

        self.grid = self._generate_grid()
        self._apply_markers()

    def _apply_markers(self) -> None:
        """Place les marqueurs sur la grille axiale (q, r)."""
        markers = self.markers
        for kind in ("X", "S", "J"):
            for q, r in markers.get(kind, []):
                if (q, r) not in self.grid:
                    raise ValueError(
                        f"Marqueur {kind} hors plateau : (q={q}, r={r})"
                    )
                if self.grid[(q, r)] == 0:
                    self.grid[(q, r)] = kind

    def set_grid(self, grid: dict[tuple[int, int], int]) -> None:
        """Ecrase la grille (utilise pour le chargement d'une save)."""
        self.grid = grid

    def _generate_grid(self) -> dict[tuple[int, int], int]:
        """Genere l'ensemble des cases du plateau en coordonnees axiales (q, r).

        On creer un hexagone de rayon N = size // 2, cad toutes les
        coordonnees cubiques (q, r, s) avec q + r + s = 0 et |q|, |r|, |s| <= N.
        Le centre du plateau est (q, r) = (0, 0).
        s n'est jamais stocke, il sera recalcule (s = -q - r) pour la rotation
        """
        grid = {}
        for q in range(-self.radius, self.radius + 1):
            r_min = max(-self.radius, -q - self.radius)
            r_max = min(self.radius, -q + self.radius)
            for r in range(r_min, r_max + 1):
                grid[(q, r)] = 0
        return grid

    def hex_delta(self, q1: int, r1: int, q2: int, r2: int) -> tuple[int, int, int]:
        """Retourne (dq, dr, ds) entre deux cases axiales."""
        dq, dr = q2 - q1, r2 - r1
        return dq, dr, -(dq + dr)

    def is_straight_line(self, q1: int, r1: int, q2: int, r2: int) -> bool:
        """Vrai si (q1,r1)->(q2,r2) est une ligne droite hex (une des 6 directions)."""
        if (q1, r1) == (q2, r2):
            return False
        dq, dr, ds = self.hex_delta(q1, r1, q2, r2)
        return dq == 0 or dr == 0 or ds == 0

    def hex_distance(self, q1: int, r1: int, q2: int, r2: int) -> int:
        dq, dr, ds = self.hex_delta(q1, r1, q2, r2)
        return max(abs(dq), abs(dr), abs(ds))

    def axial_to_2d(self, q: int, r: int) -> tuple[int, int]:
        """Convertit une coordonnee axiale (q, r) en indices 2D (ligne, colonne).

        Meme convention que la grille Tkinter :
            ligne   = r + radius
            colonne = 2 * q + r + 2 * radius
        """
        ligne = r + self.radius
        colonne = 2 * q + r + 2 * self.radius
        return ligne, colonne

    def line_path(self, q1: int, r1: int, q2: int, r2: int) -> list[tuple[int, int]]:
        """Liste des cases axiales entre (q1,r1) et (q2,r2) exclus, en ligne droite."""
        dq, dr, ds = self.hex_delta(q1, r1, q2, r2)
        n = max(abs(dq), abs(dr), abs(ds))
        step_q, step_r = dq // n, dr // n
        return [(q1 + i * step_q, r1 + i * step_r) for i in range(1, n)]
    
    def from_2d_to_axial(self, ligne: int, colonne: int) -> tuple[int, int]:
        """Convertit des indices 2D (ligne, colonne) en coordonnees axiales (q, r).

        Inverse de axial_to_2d : r = ligne - radius, q = (colonne - ligne - radius) / 2.
        ValueError si les entiers ne tombent pas juste ou si (q, r) est hors plateau.
        """
        n = self.radius
        r = ligne - n
        num = colonne - ligne - n
        if num % 2 != 0:
            raise ValueError(
                f"Coordonnees 2D incoherentes pour la projection hex : \
                (ligne={ligne}, colonne={colonne})"
            )
        q = num // 2
        if (q, r) not in self.grid:
            raise ValueError(
                f"Coordonnees 2D hors hexagone : \
                (ligne={ligne}, colonne={colonne}) -> (q={q}, r={r})"
            )
        return q, r

    def to_2d_grid(self) -> list[list]:
        """Projette la grille axiale (q, r) dans une liste 2D [ligne][colonne].

        Les cases hors hexagone valent None
        Les cases valides gardent leur valeur (0, 'X', 'S', 'J').
        A utiliser pour dessiner la grille dans tkinter.
        """
        total_cols = 2 * self.size - 1
        grid_2d = [[None] * total_cols for _ in range(self.size)]
        for (q, r), value in self.grid.items():
            ligne, colonne = self.axial_to_2d(q, r)
            grid_2d[ligne][colonne] = value
        return grid_2d

    def is_dotted_direction_from_center(self, q: int, r: int) -> bool:
        """True si (q, r) est aligne avec le centre via un chemin pointille (J)."""
        if (q, r) == self.center:
            return False
        if not self.is_straight_line(*self.center, q, r):
            return False
        steps = self.line_path(*self.center, q, r)
        first = steps[0] if steps else (q, r)
        return self.grid.get(first) == "J"

    def uses_dotted_path_to_center(
        self, q1: int, r1: int, q2: int, r2: int
    ) -> bool:
        """True si l'arrivee au centre passe par un chemin pointille (J)."""
        if (q2, r2) != self.center:
            return False
        if self.grid.get((q1, r1)) == "J":
            return True
        for cell in self.line_path(q1, r1, q2, r2):
            if self.grid.get(cell) == "J":
                return True
        return False

class BoardPile:
    def __init__(self, 
                size: int,
                board_orientation: list[int], 
                nb_boards: int) -> None:
        self._markers_by_layer = {
            "Pierre" : {
                "X": [
                        (2, -4), (3, -4),
                        (-1, -3), (0, -3), (2, -3),
                        (-1, -2), (0, -2), (2, -2),
                        (-3, -1), (0, -1), (1, -1), (3, -1),
                        (-4, 0), (-2, 0), (-1, 0), (0, 0), (1, 0), (3, 0),
                        (2, 1),
                        (-4, 2), (-1, 2), (1, 2),
                        (-4, 3), (-2, 3), (1, 3),
                        (-1, 4)
                ],
                "S": [],
            },
            "Terre" : {
                "X": [
                        (4, -4),
                        (1, -3), (3, -3), (4, -3),
                        (-2, -2), (1, -2),
                        (4, -1),
                        (-3, 0), (2, 0), (4, 0),
                        (-1, 1), (0, 1),
                        (-3, 2), (-2, 2),
                        (-3, 3), (-1, 3), (0, 3),
                        (-2, 4)
                    ],
                "S": [
                        (0, -4),
                        (-3, 1), (1, 1),
                        (-4, 4)
                    ],
                "J": [],
            },
            "Surface" : {
                "X": [(1, -4), (3, -4), (4, -2), (-3, -1), (-1, -1), (2, -1),
                    (0, 0), (-2, 1), (1, 1), (0, 2), (2, 2), (-4, 3), (-3, 4)],
                "S": [(0, -4), (4, -1), (-4, 1), (0, 4)],
                "J": [],
            },
            "Terre arable" : {
                "X": [(0, -4), (2, -3), (-1, -2), (3, -1), 
                        (-4, 4), (0, 3), (-2, 3), (-3, 1)],
                "S": [(3, -3), (-4, 0), (1, 0), (0, 4)],
                "J": [],
            },
            "Sous-sol" : {
                "X": [(1, -2), (-4, 0), (4, 0), (-2, 4)],
                "S": [(2, -4), (-4, 1), (0, 1), (2, 2)],
                "J": [],
            },
            "Roche mère" : {
                "X": [(0, 0)],
                "S": [(4, -4), (-1, -2), (1, 2), (-4, 4)],
                "J": [(0, -1), (1, 0), (-1, 1)]
            },
        }

        self.pile = []

        LAYER_ORDER = [
            "Pierre",
            "Terre",
            "Surface",
            "Terre arable",
            "Sous-sol",
            "Roche mère",
        ]

        start = len(LAYER_ORDER) - nb_boards
        for offset, layer_name in enumerate(LAYER_ORDER[start:]):
            layer_markers = copy.deepcopy(self._markers_by_layer[layer_name])
            if offset == 0:
                layer_markers["S"] = []
            layer_index = start + offset
            orientation = (
                board_orientation[layer_index]
                if layer_index < len(board_orientation)
                else 0
            )
            self.pile.append(
                Board(
                    size=size,
                    color=layer_name,
                    markers=layer_markers,
                    orientation=orientation,
                )
            )
        self.nb_boards = nb_boards
        
    def get_top(self) -> Board:
        return self.pile[0]
    
    def get_bottom(self) -> Board:
        return self.pile[-1]

    def pop_top(self) -> bool:
        self.pile.pop(0)
        return True if len(self.pile) > 0 else False

    def get_size(self) -> int:
        return len(self.pile)

    def set_pile(self, pile: list) -> None:
        """
        Remplace la pile complete de boards
        utilise pour le chargement d'une save
        """
        self.pile = pile
        self.nb_boards = len(pile)
    