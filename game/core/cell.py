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
        self.name = name
        self.icon = icon
        self.food_multiplier = food_multiplier
        self.water_multiplier = water_multiplier
        self.visibility_proba = visibility_proba
        self.weapon_proba_multiplier = weapon_proba_multiplier
        self.dangerous_weapon_proba = dangerous_weapon_proba
