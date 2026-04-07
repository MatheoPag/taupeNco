class Pawn:
    def __init__(self, id: int, color: str) -> None:
        self.id = id
        self.color = color
        self._position = None
        self.on_board = True
        self.moves_history = []
    
    def get_position(self) -> tuple[int, int] | None:
        return self._position
    
    def set_position(self, x: int, y: int) -> None:
        self._position = (x, y)

    def move(self, x: int, y: int) -> None:
        self._position[0] += x
        self._position[1] += y
        self.moves_history.append((x, y))
    

