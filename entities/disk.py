import random

class Disks:
    def __init__(self, color: str) -> None:
        self.color = color
        self.__disks = [
                [1, False],
                [2, False],
                [2, False],
                [3, False],
                [3, False],
                [4, False],
            ]

    def mix_disks(self) -> None:
        return random.shuffle(self.__disks)
    
    def get_disks(self) -> list[list[int]]:
        return self.__disks

    def set_disks(self, disks: list[list[int]]) -> None:
        """Remplace la liste des disques (synchro reseau)."""
        self.__disks = [list(d) for d in disks]
    
    def is_all_disk_visible(self) -> bool:
        for i in range(len(self.__disks)):
            if self.__disks[i][1] == False:
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
    
