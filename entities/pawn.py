class Pawn:
    def __init__(self, id: int, color: str) -> None:
        self.id = id
        self.color = color
        self.position = (None)
        self.on_board = False
        self.moves_history = []
    
    def get_position(self) -> tuple[int, int] | None:
        return self.position
    
    def set_position(self, x: int, y: int) -> None:
        self.position = (x, y)

    def move(self, x: int, y: int) -> None:
        self.position = (x, y)
        self.moves_history.append((x, y))

    def restore(
        self,
        position: tuple[int, int] | None,
        on_board: bool,
        moves_history: list,
    ) -> None:
        """Ecrase l'etat complet du pion (utilise pour le chargement d'une save)."""
        self.position = tuple(position) if position is not None else None
        self.on_board = on_board
        self.moves_history = [tuple(m) for m in moves_history]
    

