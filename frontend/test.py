"""Affichage de test des 4 plateaux du mode classique.

Lance avec : python -m frontend.test
depuis la racine du projet.
"""
import tkinter as tk

from entities.board import BoardPile

ROWS = 9
COLS = 17

COLORS = {
    'background': '#EDECED',
    'border': '#2C2E33',
    'layer0': '#4E7F6E',
    'layer0c': '#8DCAAA',
    'layer1': '#B85553',
    'layer1c': '#E8958A',
    'layer2': '#C99430',
    'layer2c': '#F0CC6E',
    'layer3': '#3F6E9E',
    'layer3c': '#8CB9DC',
}

# Couleur des trous = couche située en dessous (comme dans ui.py)
HOLE_COLOR_BY_LAYER = {
    0: 'layer1',
    1: 'layer2',
    2: 'layer3',
    3: 'layer3',
}

BOARD_LAYOUT = [
    (0, 0, 0, 'Surface'),
    (0, 1, 1, 'Terre arable'),
    (1, 0, 2, 'Sous-sol'),
    (1, 1, 3, 'Roche mère'),
]


def _layer_style(color_int: int) -> tuple[str, str, str]:
    main = f'layer{color_int}'
    light = f'layer{color_int}c'
    hole = HOLE_COLOR_BY_LAYER.get(color_int, 'layer3')
    return main, light, hole


def draw_board(canvas: tk.Canvas, board, colors: dict) -> None:
    """Dessine un plateau hexagonal (cases, trous, spéciales, chemins J)."""
    canvas.delete('all')
    w = canvas.winfo_width()
    h = canvas.winfo_height()
    if w <= 1 or h <= 1:
        return

    color_int = board.color_int if board.color_int < 100 else 0
    color, color_c, hole_color = _layer_style(color_int)

    cx = w // 2
    cy = h // 2
    r = min(w, h) // 2 - 8
    step_x = int(r * 1.8 / (COLS - 1))
    step_y = int(r * 0.9 / (ROWS - 1)) * 1.7
    pad_x = cx - ((COLS - 1) * step_x) // 2
    pad_y = cy - ((ROWS - 1) * step_y) // 2

    canvas.create_oval(
        cx - r, cy - r, cx + r, cy + r,
        fill=colors[color],
        outline=colors['border'],
        width=1,
    )

    grid = board.to_2d_grid()

    for i in range(ROWS):
        for j in range(COLS):
            if grid[i][j] is None:
                continue
            x = pad_x + j * step_x
            y = pad_y + i * step_y

            if j + 2 < COLS and grid[i][j + 2] is not None:
                x2 = pad_x + (j + 2) * step_x
                canvas.create_line(
                    x, y, x2, y,
                    fill=colors[color_c],
                    width=1,
                )
            if i + 1 < ROWS and j - 1 >= 0 and grid[i + 1][j - 1] is not None:
                x2 = pad_x + (j - 1) * step_x
                y2 = pad_y + (i + 1) * step_y
                canvas.create_line(
                    x, y, x2, y2,
                    fill=colors[color_c],
                    width=1,
                )
            if (
                i + 1 < ROWS
                and j + 1 < COLS
                and grid[i + 1][j + 1] is not None
            ):
                x2 = pad_x + (j + 1) * step_x
                y2 = pad_y + (i + 1) * step_y
                canvas.create_line(
                    x, y, x2, y2,
                    fill=colors[color_c],
                    width=1,
                )

    for row in range(ROWS):
        for col in range(COLS):
            if grid[row][col] is None:
                continue
            x = pad_x + col * step_x
            y = pad_y + row * step_y
            if grid[row][col] == 0:
                canvas.create_oval(
                    x - 5, y - 5, x + 5, y + 5,
                    fill=colors[color_c],
                    outline='',
                )

    center_row, center_col = board.axial_to_2d(*board.center)
    center_x = pad_x + center_col * step_x
    center_y = pad_y + center_row * step_y

    for q, r in board.markers.get('J', []):
        row, col = board.axial_to_2d(q, r)
        x = pad_x + col * step_x
        y = pad_y + row * step_y
        canvas.create_line(
            x, y, center_x, center_y,
            fill=colors['border'],
            width=2,
            dash=(6, 4),
        )
        canvas.create_oval(
            x - 6, y - 6, x + 6, y + 6,
            fill=colors[color_c],
            outline=colors['border'],
            width=2,
        )

    for row in range(ROWS):
        for col in range(COLS):
            if grid[row][col] is None:
                continue
            x = pad_x + col * step_x
            y = pad_y + row * step_y
            if grid[row][col] == 'X':
                canvas.create_oval(
                    x - 20, y - 20, x + 20, y + 20,
                    fill=colors[hole_color],
                    outline=colors['border'],
                )
            elif grid[row][col] == 'S':
                canvas.create_oval(
                    x - 13, y - 13, x + 13, y + 13,
                    fill=colors[color_c],
                    outline=colors['border'],
                    width=1,
                )

    canvas.create_oval(
        center_x - 7, center_y - 7, center_x + 7, center_y + 7,
        fill=colors['border'],
        outline='',
    )


class ClassicBoardsPreview:
    def __init__(self, board_orientation: list[int] | None = None):
        if board_orientation is None:
            board_orientation = [0, 0, 0, 0, 0, 0]

        self.pile = BoardPile(size=9, board_orientation=board_orientation, nb_boards=4)
        self.boards = list(self.pile.pile)

        self.root = tk.Tk()
        self.root.title('Test — Plateaux mode classique')
        self.root.geometry('900x950')
        self.root.minsize(900, 950)
        self.root.configure(bg=COLORS['background'])

        title = tk.Label(
            self.root,
            text='Mode classique — 4 plateaux (orientation par défaut)',
            font=('', 16),
            bg=COLORS['background'],
        )
        title.pack(pady=(12, 4))

        legend = tk.Label(
            self.root,
            text='● case libre   ◯ trou   ◉ case spéciale   - - chemin pointillé (J)',
            font=('', 11),
            bg=COLORS['background'],
        )
        legend.pack(pady=(0, 8))

        grid_frame = tk.Frame(self.root, bg=COLORS['background'])
        grid_frame.pack(fill='both', expand=True, padx=16, pady=8)
        for r in range(2):
            grid_frame.grid_rowconfigure(r, weight=1)
        for c in range(2):
            grid_frame.grid_columnconfigure(c, weight=1)

        self._canvases: list[tk.Canvas] = []
        for grid_row, grid_col, pile_index, label in BOARD_LAYOUT:
            cell = tk.Frame(grid_frame, bg=COLORS['background'])
            cell.grid(row=grid_row, column=grid_col, sticky='nsew', padx=8, pady=8)
            cell.grid_rowconfigure(0, weight=0)
            cell.grid_rowconfigure(1, weight=1)
            cell.grid_columnconfigure(0, weight=1)

            tk.Label(
                cell,
                text=label,
                font=('', 14),
                bg=COLORS['background'],
            ).grid(row=0, column=0, sticky='ew', pady=(0, 4))

            canvas = tk.Canvas(
                cell,
                bg=COLORS['background'],
                highlightthickness=0,
            )
            canvas.grid(row=1, column=0, sticky='nsew')
            board = self.boards[pile_index]
            canvas.bind(
                '<Configure>',
                lambda e, b=board, c=canvas: draw_board(c, b, COLORS),
            )
            self._canvases.append(canvas)

    def run(self) -> None:
        self.root.mainloop()


def main() -> None:
    ClassicBoardsPreview().run()


if __name__ == '__main__':
    main()
