import random

class Disks:
    def __init__(self, color: str, nb_boards: int = 4) -> None:
        self.color = color

        DISK_VALUES_BY_BOARDS= {
            3: [0, 1, 1, 2, 2, 3],
            4: [1, 2, 2, 3, 3, 4],
            5: [0, 1, 2, 2, 3, 4],
            6: [0, 1, 2, 2, 3, 4],
        }

        values = DISK_VALUES_BY_BOARDS.get(nb_boards, DISK_VALUES_BY_BOARDS[4])
        self.__disks = [[value, False] for value in values]

    def mix_disks(self) -> None:
        return random.shuffle(self.__disks)

    def get_disks(self) -> list[list[int]]:
        return self.__disks

    def set_disks(self, disks: list[list[int]]) -> None:
        """Remplace la liste des disques (synchro reseau)."""
        self.__disks = [list(d) for d in disks]

    def is_all_disk_visible(self) -> bool:
        for i in range(len(self.__disks)):
            if not self.__disks[i][1]:
                return False
        return True

    def hide_all_disks(self) -> None:
        for i in range(len(self.__disks)):
            self.__disks[i][1] = False

    def show_disk(self, disk: int) -> int | None:
        if self.__disks[disk][1]:
            return None

        self.__disks[disk][1] = True
        return self.__disks[disk][0]
