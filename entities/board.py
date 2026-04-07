"""
rotation 60 deg :
    Pourquoi 3 axes ?
        en 2D classique -> les axes à 90 deg
        en hexagonal -> 120°
        donc 2 axes -> pas pratique pour représenter les 6 directions
        3 axes -> chaque direction devient simple
    BFS -> Part du centre et explore les voisins, puis voisin de voisin...
    grid_step_cube :
        pour chaque direction on a
            Partie grille (deux premier) : (y, x) -> (y + [0], x + [1])
            Partie cube (le reste) : (q, r, s) -> (q + [2], r + [3], s - [4])

    formule rotation simple : (q, r, s) -> (-r, -s, -q)
"""

class Board:
    def __init__(self, size: int, color: str) -> None:
        self.size = size
        self.grid = self.generate_grid()
        self.color = color
        self.center = (size // 2, size - 1) # (ligne, colonne)
        # X : Troues, S : Case Speciales
        self.__markers = {
            "green": {
                "X": [(0, 6), (0, 10), (2, 14), (3, 1), (3, 5), (3, 11), (4, 8), (5, 5), (5, 11), (6, 10), (6, 14), (7, 3), (8, 6)],
                "S": [],
            },
            "red": {
                "X": [(0, 4), (1, 9), (2, 4), (3, 13)],
                "S": [(1, 11), (4, 0), (4, 10), (8, 12)],
            },
            "yellow": {
                "X": [(1, 9), (2, 2), (2, 14), (8, 8)],
                "S": [(0, 8), (5, 1), (5, 9), (6, 14)],
            },
            "blue": {
                "X": [(4, 8)],
                "S": [(0, 12), (2, 4), (6, 12), (8, 4)],
            },
        }
        self.apply_markers()

    def _build_cube_coord_maps(self) -> tuple[dict[tuple[int, int], tuple[int, int, int]], dict[tuple[int, int, int], tuple[int, int]]]:
        """Construit pos_to_cube et cube_to_pos pour toutes les cases du plateau"""

        # Chaque entrée : (delta_ligne, delta_colonne, delta_q, delta_r, delta_s)
        grid_step_cube = (
            (0, 2, 1, 0, -1),
            (0, -2, -1, 0, 1),
            (-1, -1, 0, -1, 1),
            (-1, 1, 1, -1, 0),
            (1, -1, -1, 1, 0),
            (1, 1, 0, 1, -1),
        )

        template = self.generate_grid()

        # Depuis le centre, on fixe l'origine cubique (0, 0, 0).
        pos_to_cube = {}
        cube_to_pos = {}
        pos_to_cube[(center_row, center_col)] = (0, 0, 0)
        cube_to_pos[(0, 0, 0)] = (center_row, center_col)
        queue = [(center_row, center_col)]
        head = 0

        while head < len(queue):
            ligne, colonne = queue[head]
            head += 1
            cube_q, cube_r, cube_s = pos_to_cube[(ligne, colonne)]
            for delta_ligne, delta_colonne, delta_q, delta_r, delta_s in grid_step_cube:
                voisin_ligne = ligne + delta_ligne
                voisin_colonne = colonne + delta_colonne
                if not (0 <= voisin_ligne < self.size and 0 <= voisin_colonne < len(template[voisin_ligne])):
                    continue
                if template[voisin_ligne][voisin_colonne] is None:
                    continue
                if (voisin_ligne, voisin_colonne) in pos_to_cube:
                    continue
                voisin_q = cube_q + delta_q
                voisin_r = cube_r + delta_r
                voisin_s = cube_s + delta_s
                pos_to_cube[(voisin_ligne, voisin_colonne)] = (voisin_q, voisin_r, voisin_s)
                cube_to_pos[(voisin_q, voisin_r, voisin_s)] = (voisin_ligne, voisin_colonne)
                queue.append((voisin_ligne, voisin_colonne))
        return pos_to_cube, cube_to_pos

    def _rotate_cube_60(self, cube_q: int, cube_r: int, cube_s: int) -> tuple[int, int, int]:
        return -cube_r, -cube_s, -cube_q

    def rotate_markers_60(self) -> None:
        """Recalcule les coordonnees de tous les marqueurs (toutes couleurs) apres +60 deg."""
        pos_to_cube, cube_to_pos = self._build_cube_coord_maps()
        for _color, groups in self.__markers.items():
            for kind in ("X", "S"):
                new_list = []
                for ligne_marqueur, colonne_marqueur in groups[kind]:
                    coords_cubiques = pos_to_cube.get((ligne_marqueur, colonne_marqueur))
                    if coords_cubiques is None:
                        raise ValueError(
                            f"Coordonnee marqueur hors plateau : ({ligne_marqueur}, {colonne_marqueur})"
                        )
                    marqueur_q, marqueur_r, marqueur_s = coords_cubiques
                    apres_rotation_q, apres_rotation_r, apres_rotation_s = self._rotate_cube_60(
                        marqueur_q, marqueur_r, marqueur_s
                    )
                    nouvelle_position = cube_to_pos.get(
                        (apres_rotation_q, apres_rotation_r, apres_rotation_s)
                    )
                    if nouvelle_position is None:
                        raise ValueError(
                            "Rotation 60 deg : pas de case pour le cube "
                            f"{coords_cubiques} -> ({apres_rotation_q}, {apres_rotation_r}, {apres_rotation_s})"
                        )
                    new_list.append(nouvelle_position)
                groups[kind] = new_list

        self.grid = self.generate_grid()
        self.apply_markers()

    def apply_markers(self) -> None:
        """Remplace les 0 aux coordonnees (ligne, colonne) par X ou S selon la couleur du plateau.
        X : Troues, S : Case Speciales"""
        key = self.color.lower() if isinstance(self.color, str) else str(self.color).lower()
        markers = self.__markers.get(key)
        if markers is None:
            return
        for y, x in markers["X"]:
            if 0 <= y < len(self.grid) and 0 <= x < len(self.grid[y]) and self.grid[y][x] == 0:
                self.grid[y][x] = "X"
        for y, x in markers["S"]:
            if 0 <= y < len(self.grid) and 0 <= x < len(self.grid[y]) and self.grid[y][x] == 0:
                self.grid[y][x] = "S"

    def generate_grid(self) -> list[list[int]]:
        if self.size % 2 == 0:
            raise ValueError("La taille doit etre impaire")
        if self.size <= 0:
            raise ValueError("La taille doit etre strictement positive")
        
        temp_grid = []
        mid = self.size // 2
        for y in range(self.size):
            row = []
            dist = abs(y - mid)
            valid_cells = self.size - dist
            padding = dist
            total_length = self.size * 2 - 1
            for x in range(total_length):
                if padding <= x <= total_length - padding - 1 and (x - padding) % 2 == 0:
                    row.append(0)
                else:
                    row.append(None)
            temp_grid.append(row)
        return temp_grid

    def print_grid(self) -> None:
        for i in range(self.size):
            for j in range(len(self.grid[i])):
                if self.grid[i][j] is not None:
                    if self.grid[i][j] == 0:
                        print(str(".").rjust(2), end=" ")
                    else:
                        print(str(self.grid[i][j]).rjust(2), end=" ")
                else:
                    print(" ".rjust(3), end="")
            print()
            print()

class BoardPile:
    def __init__(self, colors:list[str], size: int) -> None:
        self.pile = [Board(size, color) for color in colors]
        self.nb_boards = len(colors)
    
    def get_top(self) -> Board:
        return self.pile[0]
    
    def get_bottom(self) -> Board:
        return self.pile[-1]

    def pop_top(self) -> bool:
        self.pile.pop(0)
        return True if len(self.pile) > 0 else False
    


if __name__ == "__main__":

    
