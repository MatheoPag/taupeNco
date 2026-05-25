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
        self.pawns_per_player = {2 : 2, 3 : 7, 4 : 6} # 2 normal -> 10, on a mis 2 pour le dev
        self.colors = [
                (0, "Surface"),
                (1, "Terre arable"),
                (2, "Sous-sol"),
                (3, "Roche mère"),
            ]
        self.nb_human_players = nb_players
        self.nb_bots = nb_bots
        self.current_player = random.randint(0, nb_players + nb_bots - 1)
        players = (
            [
                {"name": f"Player {i+1}", "color": self.colors[i]}
                for i in range(nb_players)
            ]
            + [
                {"name": f"Bot", "color": self.colors[i + nb_players]}
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
        self.legal_moves = None
        self._pending_disk_sync = None

        for p in self.players:
            p.disks.mix_disks()

    def is_bot(self, player_id: int | None = None) -> bool:
        if player_id is None:
            player_id = self.current_player
        return player_id >= self.nb_human_players

    def get_players_disks_state(self) -> list[list[list[int]]]:
        """Etat des disques de chaque joueur (pour la synchro reseau)."""
        return [p.disks.get_disks() for p in self.players]

    def apply_players_disks_state(self, players_disks: list[list[list[int]]]) -> None:
        """Applique l'etat des disques recu de l'hote."""
        for player, disks in zip(self.players, players_disks):
            player.disks.set_disks(disks)

    def consume_disk_sync(self) -> dict | None:
        """Retourne et efface la synchro disques en attente (apres mix hote)."""
        payload = self._pending_disk_sync
        self._pending_disk_sync = None
        return payload


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
        """Verifie si (row, col) est une case cible valide selon la phase."""
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
                            pawn, 
                            row: int, 
                            col: int, 
                            phase: str) -> bool:
        """
        Valide la case pour la phase donnee et deplace le pion. 
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
        - puis coup si legal.
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
            self.sub_phase = "choix_disque" # modifié par Tristan
        return True

    def try_choose_disk(self, disk_selected: int, update_ui) -> bool:
        """Phase mouvement : choix du disque."""
        if self.phase != "mouvement":
            return False
        if self.sub_phase is None:
            self.sub_phase = "choix_disque"
        if self.sub_phase == "choix_disque":
            print("choix du disque")
            self.legal_moves = None
            cur_player = self.players[self.current_player] 
            cur_player.disk_selected = disk_selected
            disk = cur_player.disks.get_disks()[disk_selected]
            disk[1] = True
            print(f"disque selectionne : {disk}")
            self.sub_phase = "choix_pion"
            update_ui()


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
                print("Le pion selectionne n'appartient pas au joueur courant.")
                return False
            current_player.pawn_selected = pawn_found[1]
            self.legal_moves = self.possible_moves(
                pawn_found[1], current_player.disk_selected
            )
            self.sub_phase = "deplacement"
            return True

        return False

    def possible_moves(self, pawn_index, disk_index: int) -> list[tuple[int, int]]:
        pawn = self.players[self.current_player].pawns[pawn_index]
        n = self.players[self.current_player].disks.get_disks()[disk_index][0]

        if pawn.position is None:
            return []
        board = self.boards.get_top()
        q1, r1 = board.from_2d_to_axial(pawn.position[0], pawn.position[1])
        cases_possibles = []

        for (q2, r2) in board.grid:
            row, col = board.axial_to_2d(q2, r2)
            dist = board.hex_distance(q1, r1, q2, r2)
            if dist != n:
                continue
            if not board.is_straight_line(q1, r1, q2, r2):
                continue
            chemin_bloque = False
            for pq, pr in board.line_path(q1, r1, q2, r2):
                pl, pc = board.axial_to_2d(pq, pr)
                if self.cell_occupied_by_pawn(pl, pc):
                    chemin_bloque = True
                    break
            if chemin_bloque:
                continue
            if not self.is_legal_target_cell(row, col, "mouvement"):
                continue
            cases_possibles.append((row, col))
        return cases_possibles


    def try_move_chosen_pawn_to(
        self, row: int, col: int, shuffle_disks: bool = True
    ) -> bool:
        """Phase mouvement : deplace le pion designe du joueur courant.

        shuffle_disks : False sur les clients (l'hote melange et diffuse).
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
                print("le pion selectionne n'est pas valide")
                return False
            pawn = cur.pawns[cur.pawn_selected]
            if pawn.position is None:
                print("le pion n'est pas sur le plateau")
                return False

            if cur.disk_selected is None:
                print("le disque selectionne n'est pas valide")
                return False

            if (row, col) not in self.possible_moves(
                cur.pawn_selected, cur.disk_selected
            ):
                print("le deplacement n'est pas valide")
                return False

            board = self.boards.get_top()
            if self.try_move_pawn_to_cell(pawn, row, col, "mouvement"):
                self.sub_phase = "choix_disque"
                self.legal_moves = None
                q2, r2 = board.from_2d_to_axial(row, col)
                if board.grid.get((q2, r2)) == "S":
                    print(f"Case speciale : {cur.name} rejoue.")
                else:
                    self.current_player = (
                        (self.current_player + 1) % len(self.players)
                    )

                if cur.disks.is_all_disk_visible():
                    cur.disks.hide_all_disks()
                    if shuffle_disks:
                        cur.disks.mix_disks()
                        self._pending_disk_sync = {
                            "player_id": cur.id,
                            "disks": cur.disks.get_disks(),
                        }
                return True
            print("le deplacement n'est pas valide car la case est \
                occupee par un autre pion")
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