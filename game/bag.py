from typing import List
from .weapon import Weapon

class Bag:
    def __init__(self):
        self.weapons: List[Weapon] = []
        self.food: int = 0
        self.water: int = 0

    def show(self) -> str:
        result = ""
        result += "Bag:\n"
        result += f"  Weapons: {self.weapons}" + "\n"
        result += f"  Food:    {self.food}" + "\n"
        result += f"  Water:   {self.water}" + "\n"
        return result[:-1]

    def add_weapon(self, weapon: Weapon) -> None:
        assert isinstance(weapon, Weapon), f"Expected a Weapon, but got {type(weapon)}"
        self.weapons.append(weapon)

    def steal(self, stealed_bag: "Bag") -> None:
        self.food += stealed_bag.food
        self.water += stealed_bag.water
        self.weapons += stealed_bag.weapons
        stealed_bag.food = 0
        stealed_bag.water = 0
        stealed_bag.weapons = []
