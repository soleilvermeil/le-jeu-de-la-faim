class Cell:

    def __init__(
        self, name: str,
        icon: str,
        food_multiplier: int = 1,
        water_multiplier: int = 1,
        visibility_proba: int = 0.5,
        weapon_proba_multiplier: int = 1,
        dangerous_weapon_proba: int = 0,
    ):
        """
        Create a new cell.

        Parameters
        ----------
        name : str
            The name of the cell.
        icon : str
            The icon of the cell, usually an emoji.
        food_multiplier : int
            If food is found in the cell, the amount of food found is
            multiplied by this value.
        water_multiplier : int
            If water is found in the cell, the amount of water found is
            multiplied by this value.
        weapon_proba_multiplier : int
            The probability of finding a weapon (instead of food or water) is
            multiplied by this value.
        dangerous_weapon_proba : int
            If a weapon is found, the probability of that weapon being
            dangerous.
        """
        self.name = name
        self.icon = icon
        self.food_multiplier = food_multiplier
        self.water_multiplier = water_multiplier
        self.visibility_proba = visibility_proba
        self.weapon_proba_multiplier = weapon_proba_multiplier
        self.dangerous_weapon_proba = dangerous_weapon_proba
