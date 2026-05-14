import copy

class Board:
    def __init__(self, size: int, color, markers: dict[str, list[tuple[int, int]]], orientation: int) -> None:
        if size % 2 == 0:
            raise ValueError("La taille doit etre impaire")
        if size <= 0:
            raise ValueError("La taille doit etre strictement positive")
        self.size = size
        self.radius = size // 2
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
        for kind in ("X", "S"):
            rotated = []
            for q, r in self.markers.get(kind, []):
                new_q, new_r = self._rotate_axial_60(q, r)
                if (new_q, new_r) not in self.grid:
                    raise ValueError(f"Rotation 60 deg : ({q}, {r}) sort du plateau -> ({new_q}, {new_r})")
                rotated.append((new_q, new_r))
            self.markers[kind] = rotated

        self.grid = self._generate_grid()
        self._apply_markers()

    def _apply_markers(self) -> None:
        """Place les marqueurs sur la grille axiale (q, r)."""
        markers = self.markers
        for kind in ("X", "S"):
            for q, r in markers[kind]:
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

    def axial_to_2d(self, q: int, r: int) -> tuple[int, int]:
        """Convertit une coordonnee axiale (q, r) en indices 2D (ligne, colonne).

        Meme convention que la grille Tkinter :
            ligne   = r + radius
            colonne = 2 * q + r + 2 * radius
        """
        ligne = r + self.radius
        colonne = 2 * q + r + 2 * self.radius
        return ligne, colonne

    def from_2d_to_axial(self, ligne: int, colonne: int) -> tuple[int, int]:
        """Convertit des indices 2D (ligne, colonne) en coordonnees axiales (q, r).

        Inverse de axial_to_2d : r = ligne - radius, q = (colonne - ligne - radius) / 2.
        Leve ValueError si les entiers ne tombent pas juste ou si (q, r) est hors plateau.
        """
        n = self.radius
        r = ligne - n
        num = colonne - ligne - n
        if num % 2 != 0:
            raise ValueError(
                f"Coordonnees 2D incoherentes pour la projection hex : (ligne={ligne}, colonne={colonne})"
            )
        q = num // 2
        if (q, r) not in self.grid:
            raise ValueError(
                f"Coordonnees 2D hors hexagone : (ligne={ligne}, colonne={colonne}) -> (q={q}, r={r})"
            )
        return q, r

    def to_2d_grid(self) -> list[list]:
        """Projette la grille axiale (q, r) dans une liste 2D [ligne][colonne].

        Les cases hors hexagone valent None
        Les cases valides gardent leur valeur (0, 'X', 'S').
        A utiliser pour dessiner la grille dans tkinter.
        """
        total_cols = 2 * self.size - 1
        grid_2d = [[None] * total_cols for _ in range(self.size)]
        for (q, r), value in self.grid.items():
            ligne, colonne = self.axial_to_2d(q, r)
            grid_2d[ligne][colonne] = value
        return grid_2d

    def print_grid(self) -> None:
        """Affiche la grille (dev only)"""
        for ligne in self.to_2d_grid():
            cells = []
            for value in ligne:
                if value is None:
                    cells.append("  ")
                elif value == 0:
                    cells.append(" .")
                else:
                    cells.append(str(value).rjust(2))
            print(" ".join(cells))
            print()

class BoardPile:
    def __init__(self, colors:list[tuple[int, str]], size: int, board_orientation: list[int]) -> None:
        self._markers_by_layer: list[dict[str, list[tuple[int, int]]]] = [
            {
                "X": [(1, -4), (3, -4), (4, -2), (-3, -1), (-1, -1), (2, -1),
                    (0, 0), (-2, 1), (1, 1), (0, 2), (2, 2), (-4, 3), (-3, 4)],
                "S": [],
            },
            {
                "X": [(0, -4), (2, -3), (-1, -2), (3, -1)],
                "S": [(3, -3), (-4, 0), (1, 0), (0, 4)],
            },
            {
                "X": [(2, -3), (-2, -2), (4, -2), (-2, 4)],
                "S": [(2, -4), (-4, 1), (0, 1), (2, 2)],
            },
            {
                "X": [(0, 0)],
                "S": [(4, -4), (-1, -2), (1, 2), (-4, 4)],
            },
        ]

        self.pile = []
        for i, color in enumerate(colors):
            layer_id = color[0]
            layer_markers = copy.deepcopy(self._markers_by_layer[layer_id])
            self.pile.append(Board(size, color, markers=layer_markers, orientation=board_orientation[i]))
        self.nb_boards = len(colors)
    
    def get_top(self) -> Board:
        return self.pile[0]
    
    def get_bottom(self) -> Board:
        return self.pile[-1]

    def pop_top(self) -> bool:
        self.pile.pop(0)
        return True if len(self.pile) > 0 else False

    def set_pile(self, pile: list) -> None:
        """Remplace la pile complete de boards (utilise pour le chargement d'une save)."""
        self.pile = pile
        self.nb_boards = len(pile)
    

if __name__ == "__main__":
    board_pile = BoardPile([(1, "Surface"), (2, "Terre arable"), (3, "Sous-sol"), (4, "Roche mère")], 9)
    board_pile.get_top().print_grid()
    print(board_pile.get_top().to_2d_grid())