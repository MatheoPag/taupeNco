from . import disk
from . import pawn

class Player:
    def __init__(
        self, id: int, name: str, color: str, nb_pawns: int, nb_boards: int = 4
    ) -> None:
        self.id = id
        self.name = name
        self.color = color
        self.last_pawn_moved = -1
        self.pawns = [pawn.Pawn(i, color) for i in range(1, nb_pawns + 1)]
        self.disks = disk.Disks(color, nb_boards)
        self.disk_selected = None
        self.pawn_selected = None


    def set_pawns(self, pawns: list) -> None:
        """Remplace la liste des pions (utilise pour le chargement d'une save)."""
        self.pawns = pawns

    def get_infos(self) -> dict[str, str]:
        return {
            "id": self.id,
            "name": self.name,
            "color": self.color,
            "pawns": [pawn.color for pawn in self.pawns],
            "disks": self.disks.get_disks()
        }