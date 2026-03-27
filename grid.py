#  ceci est un test 

def create_hex_grid(size):
    if size % 2 == 0:
        raise ValueError("La taille doit être impaire")

    grid = []
    mid = size // 2

    for y in range(size):
        row = []

        dist = abs(y - mid)

        valid_cells = size - dist

        padding = dist

        total_length = size * 2 - 1

        for x in range(total_length):
            if padding <= x <= total_length - padding - 1 and (x - padding) % 2 == 0:
                row.append(0)
            else:
                row.append(None)

        grid.append(row)

    return grid

def print_grid(grid):
    for row in grid:
        for cell in row:
            if cell is None:
                print("   ", end="")
            else:
                print(" . ", end="")
        print()

size = 9
grid = create_hex_grid(size)