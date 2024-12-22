class Weapon:

    def __init__(self, name: str, damage: int):
        self.name = name
        self.damage = damage


    def __repr__(self) -> str:
        return self.name
