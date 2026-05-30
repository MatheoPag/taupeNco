from . import board
from . import golden_shovel
from . import player
import random 
# 192.168.1.76

class Game: 
    def __init__(self, 
                nb_players: int, 
                nb_bots: int, 
                nb_boards: int,
                board_orientation: list[int]) -> None:
        self.board_size = 9
        self.pawns_per_player_per_board = {
            3 : {2 : 9, 3 : 6, 4 : 5},
            4 : {2 : 10, 3 : 7, 4 : 6},
            5 : {2 : 19, 3 : 13, 4 : 10},
            6 : {2 : 16, 3 : 11, 4 : 8},
        }
        self.player_colors = [
                "Terre",
                "Pierre",
                "Surface",
                "Terre arable",
            ]
        self.nb_human_players = nb_players
        self.nb_bots = nb_bots
        self.current_player = random.randint(0, nb_players + nb_bots - 1)
        players = (
            [
                {"name": f"Player {i+1}", "color": self.player_colors[i]}
                for i in range(nb_players)
            ]
            + [
                {"name": f"Bot", "color": self.player_colors[i + nb_players]}
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
                self.pawns_per_player_per_board[nb_boards][len(players)]
            ) for i in range(len(players))]
        self.boards = board.BoardPile(self.board_size, board_orientation, nb_boards)
        self.golden_shovel = golden_shovel.GoldenShovel(self.boards.get_bottom().center)
        self.phase = "placement"
        self.sub_phase = None
        self.bonus_move = False
        self.legal_moves = None
        self._pending_disk_sync = None
        self._board_descended = False
        self.winner = None

        for p in self.players:
            p.disks.mix_disks()

    def is_bot(self, player_id: int | None = None) -> bool:
        if player_id is None:
            player_id = self.current_player
        return player_id >= self.nb_human_players

    def _two_player_last_board(self) -> bool:
        """Regles speciales centre / chemins pointilles (2 joueurs, roche mere)."""
        return len(self.players) == 2 and len(self.boards.pile) == 1

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
        if phase == "placement":
            pawn.state = "alive"
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
            self.begin_player_turn()
        return True

    def try_choose_disk(self, disk_selected: int, update_ui) -> bool:
        """Phase mouvement : choix du disque."""
        if self.phase != "mouvement":
            return False
        if self.sub_phase is None:
            self.sub_phase = "choix_disque"
        if self.sub_phase == "passer_tour":
            return False
        if not self.has_pawns_on_board():
            return False
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
        if self.sub_phase in ("choix_pion", "deplacement"):
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

    def is_player_blocked(self) -> bool:
        cur = self.players[self.current_player]
        pawn_blocked = 0
        for i in range(len(cur.pawns)):
            if len(self.possible_moves(i, cur.disk_selected)) == 0:
                pawn_blocked += 1
        if pawn_blocked == len(cur.pawns):
            return True

    def has_pawns_on_board(self) -> bool:
        """True si le joueur courant a au moins un pion non elimine."""
        cur = self.players[self.current_player]
        return any(p.state != "dead" for p in cur.pawns)

    def is_all_pawns_in_holes(self) -> bool:
        """True si toutes les taupes posees du joueur courant sont sur un trou (X)."""
        cur = self.players[self.current_player]
        board = self.boards.get_top()
        placed = [p for p in cur.pawns if p.position is not None]
        if not placed:
            return False
        for pawn in placed:
            row, col = pawn.position
            q, r = board.from_2d_to_axial(row, col)
            if board.grid.get((q, r)) != "X":
                return False
        return True

    def are_all_holes_filled(self) -> bool:
        """True si chaque trou (X) du plateau courant contient un pion."""
        board = self.boards.get_top()
        holes = [(q, r) for (q, r), value in board.grid.items() if value == "X"]
        if not holes:
            return False
        for q, r in holes:
            row, col = board.axial_to_2d(q, r)
            if not self.cell_occupied_by_pawn(row, col):
                return False
        return True

    def get_center_cell(self) -> tuple[int, int]:
        """Case centrale du plateau courant, en coordonnees 2D."""
        board = self.boards.get_top()
        return board.axial_to_2d(*board.center)

    def get_player_at_center(self):
        """Joueur possedant un pion vivant au centre du dernier plateau."""
        if len(self.boards.pile) != 1:
            return None
        center_row, center_col = self.get_center_cell()
        for player in self.players:
            for pawn in player.pawns:
                if (
                    pawn.state == "alive"
                    and pawn.position == (center_row, center_col)
                ):
                    return player
        return None

    def check_victory(self) -> bool:
        """True si un joueur occupe le centre du dernier plateau."""
        if self.phase == "victoire":
            return True
        winner = self.get_player_at_center()
        if winner is None:
            return False
        print(f"{winner.name} a gagne.")
        self.winner = winner
        self.phase = "victoire"
        self.sub_phase = None
        return True

    def consume_board_descent(self) -> bool:
        """True une fois apres un pop_top, puis remet le flag a False."""
        if not self._board_descended:
            return False
        self._board_descended = False
        return True

    def check_board_descent(self) -> None:
        """Verifie si tous les trous sont remplis et declenche la descente de plateau."""
        if not self.are_all_holes_filled():
            return
        if len(self.boards.pile) == 1:
            self.check_victory()
            return
        top = self.boards.get_top()
        print(
            f"Tous les trous du plateau {top.name} sont remplis : "
            "descente au plateau inferieur."
        )

        for player in self.players:
            for pawn in player.pawns:
                if pawn.position is None:
                    continue
                row, col = pawn.position
                q, r = top.from_2d_to_axial(row, col)
                if not top.grid.get((q, r)) == "X":
                    pawn.state = "dead"
                    pawn.position = None

        self.boards.pop_top()
        self._board_descended = True

    def begin_player_turn(self) -> None:
        """Debut de tour : choix disque ou proposition de passer si ineligible."""
        if not self.has_pawns_on_board() or self.is_all_pawns_in_holes():
            self.sub_phase = "passer_tour"
        else:
            self.sub_phase = "choix_disque"

    def start_bonus_turn(self) -> None:
        """Second deplacement apres une case speciale (interdit de finir sur S)."""
        self.bonus_move = True
        self.begin_player_turn()


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
            if self.bonus_move and board.grid.get((q2, r2)) == "S":
                continue
            if (
                self._two_player_last_board()
                and board.uses_dotted_path_to_center(q1, r1, q2, r2)
            ):
                continue
            cases_possibles.append((row, col))
        return cases_possibles


    def get_possible_moves(self, pawn, n: int) -> list[tuple[int, int]]:
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
                self.legal_moves = None
                q2, r2 = board.from_2d_to_axial(row, col)
                if board.grid.get((q2, r2)) == "S":
                    print(f"Case speciale : {cur.name} rejoue.")
                    self.sub_phase = "rejouer"
                else:
                    self.bonus_move = False
                    self.current_player = (
                        (self.current_player + 1) % len(self.players)
                    )
                    self.begin_player_turn()


                if cur.disks.is_all_disk_visible():
                    cur.disks.hide_all_disks()
                    if shuffle_disks:
                        cur.disks.mix_disks()
                        self._pending_disk_sync = {
                            "player_id": cur.id,
                            "disks": cur.disks.get_disks(),
                        }
                self.check_board_descent()
                if self.phase != "victoire":
                    self.check_victory()
                return True
            print("le deplacement n'est pas valide car la case est \
                occupee par un autre pion")
        return False
