from . import board
from . import golden_shovel
from . import player
import random 
# 192.168.1.76

class Game: 
    def __init__(self, 
                nb_players: int, 
                nb_bots: int, 
                board_orientation: list[int]) -> None:
        self.board_size = 9
        self.pawns_per_player = {2 : 2, 3 : 7, 4 : 6}
        self.colors = [
                (0, "Surface"),
                (1, "Terre arable"),
                (2, "Sous-sol"),
                (3, "Roche mère"),
            ]
        self.current_player = random.randint(0, nb_players + nb_bots - 1)
        players = (
            [
                {"name": f"Player {i+1}", "color": self.colors[i]}
                for i in range(nb_players)
            ]
            + [
                {"name": f"Bot {i+1}", "color": self.colors[i + nb_players]}
                for i in range(nb_bots)
            ]
        )
        self.disk_selected = None
        self.pawn_selected = None
        self.players = [
            player.Player(
                i, 
                players[i]["name"], 
                players[i]["color"], 
                self.pawns_per_player[len(players)]
            ) for i in range(len(players))]
        self.boards = board.BoardPile(self.colors, self.board_size, board_orientation)
        self.golden_shovel = golden_shovel.GoldenShovel(self.boards.get_bottom().center)
        self.phase = "placement"
        self.sub_phase = None

    def set_golden_shovel(self, shovel) -> None:
        """Remplace la golden shovel (utilise pour le chargement d'une save)."""
        self.golden_shovel = shovel

    def check_placement(self, players):
        for p in players:
            for pawn in p.pawns:
                if pawn.position is None:
                    return False
        return True

    def cell_occupied_by_pawn(self, row, col):
        for p in self.players:
            for pawn in p.pawns:
                pos = pawn.position
                if not isinstance(pos, tuple) or len(pos) != 2:
                    continue
                pr, pc = pos
                if pr is None or pc is None:
                    continue
                if pr == row and pc == col:
                    return True
        return False

    def is_legal_target_cell(self, row: int, col: int, phase: str) -> bool:
        """Vérifie si (row, col) est une case cible valide selon la phase."""
        if phase not in ("placement", "mouvement"):
            return False

        grid = self.boards.get_top().to_2d_grid()
        if not grid or not (0 <= row < len(grid) and 0 <= col < len(grid[0])):
            return False

        cell = grid[row][col]
        if cell is None:
            return False

        if self.cell_occupied_by_pawn(row, col):
            return False

        if phase == "placement" and cell == "X":
            return False

        return True

    def try_move_pawn_to_cell(self, 
                            pawn: player.Pawn, 
                            row: int, 
                            col: int, 
                            phase: str) -> bool:
        """
        Valide la case pour la phase donnée et déplace le pion. 
        Pas de changement de joueur ni de phase.
        """
        if not self.is_legal_target_cell(row, col, phase):
            return False
        pawn.move(row, col)
        return True

    def try_place_current_pawn(self, row: int, col: int) -> bool:
        """
        Placement : 
        - choix automatique du prochain pion du joueur courant,
        - puis coup si légal.
        """
        if self.phase != "placement":
            return False

        current = self.players[self.current_player]
        last = current.last_pawn_moved
        if last + 1 >= len(current.pawns):
            return False

        pawn = current.pawns[last + 1]
        if not self.try_move_pawn_to_cell(pawn, row, col, "placement"):
            return False

        current.last_pawn_moved = (last + 1) % len(current.pawns)
        self.current_player = (self.current_player + 1) % len(self.players)

        if self.check_placement(self.players):
            self.phase = "mouvement"
        return True

    def try_choose_disk(self, disk_selected: int) -> bool:
        """Phase mouvement : choix du disque."""
        if self.phase != "mouvement":
            return False
        if self.sub_phase is None:
            self.sub_phase = "choix_disque"
        if self.sub_phase == "choix_disque":
            print("choix du disque")
            self.players[self.current_player].disk_selected = disk_selected
            disk = self.players[self.current_player].disks.get_disks()[disk_selected]
            disk[1] = True
            print(f"disque selectionné : {disk}")
            self.sub_phase = "choix_pion"
            return True
        return False

    def try_choose_pawn(self, row: int, col: int) -> bool:
        """Phase mouvement : choix du pion."""
        if self.phase != "mouvement":
            return False
        if self.sub_phase is None:
            self.sub_phase = "choix_disque"
            return False
        if self.sub_phase == "choix_pion":
            print("choix du pion")
            current_player = self.players[self.current_player]
            player_pawns = current_player.pawns
            pawn_found = None
            for idx, pawn in enumerate(player_pawns):
                if pawn.position is not None:
                    if pawn.position[0] == row and pawn.position[1] == col:
                        pawn_found = (pawn, idx)
                        break
            if not pawn_found:
                print("Le pion sélectionné n'appartient pas au joueur courant.")
                return False
            # On sélectionne ce pion pour le déplacement
            current_player.pawn_selected = pawn_found[1]
 
            self.sub_phase = "deplacement"
            return True

        return False

    def try_move_chosen_pawn_to(self, row: int, col: int) -> bool:
        """Phase mouvement : déplace le pion désigné du joueur courant.

        (passage de tour à ajouter plus tard).
        """
        if self.phase != "mouvement":
            return False
        if self.sub_phase is None:
            self.sub_phase = "choix_disque"
            return False
        if self.sub_phase == "deplacement":
            print("deplacement")
            cur = self.players[self.current_player]

            if (
                cur.pawn_selected is None
                or not (0 <= cur.pawn_selected < len(cur.pawns))
            ):
                print("le pion selectionné n'est pas valide")
                return False
            pawn = cur.pawns[cur.pawn_selected]
            if pawn.position is None:
                print("le pion n'est pas sur le plateau")
                return False
            
            if cur.disk_selected is None:
                print("le disque selectionné n'est pas valide")
                return False
            required_moves = cur.disks.get_disks()[cur.disk_selected][0]
            
            board = self.boards.get_top()
            try :
                q1, r1 = board.from_2d_to_axial(pawn.position[0], pawn.position[1])
                q2, r2 = board.from_2d_to_axial(row, col)
            except ValueError:
                print("le deplacement n'est pas valide \
                car les coordonnées sont hors du plateau")
                return False
            if not board.is_straight_line(q1, r1, q2, r2):
                print("le deplacement n'est pas en ligne droite car les \
                    coordonnées ne sont pas en ligne droite")
                return False
            if required_moves != board.hex_distance(q1, r1, q2, r2):
                print("le deplacement n'est pas valide car le nombre de pas \
                est incorrect")
                return False
            for pq, pr in board.line_path(q1, r1, q2, r2):
                pl, pc = board.axial_to_2d(pq, pr)
                if self.cell_occupied_by_pawn(pl, pc):
                    return False
            if self.try_move_pawn_to_cell(pawn, row, col, "mouvement"):
                self.sub_phase = "choix_disque"
                # Regle : atterrir sur une case speciale fait rejouer
                if board.grid.get((q2, r2)) == "S":
                    print(f"Case speciale : {cur.name} rejoue.")
                else:
                    self.current_player = (self.current_player + 1) % len(self.players)
                return True
            else:
                print("le deplacement n'est pas valide car la case est \
                occupée par un autre pion")
        return False

if __name__ == "__main__":
    game = Game(
            [
                {"name": "John", "color": "green"}, 
                {"name": "Jane", "color": "red"}, 
                {"name": "Jim", "color": "yellow"}, 
                {"name": "Jill", "color": "blue"}
            ]
        )