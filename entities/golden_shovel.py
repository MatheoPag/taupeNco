class GoldenShovel:
    def __init__(self, position: tuple[int, int]) -> None:
        self.position = position
    
    def get_position(self) -> tuple[int, int]:
        return self.position