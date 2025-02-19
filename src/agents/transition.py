import random
from typing import Literal
from .base import BaseAgent
from ..engine import constants
from ..shared import utils
from math import ln, exp

class TransitionAgent(BaseAgent):

    def __init__(
        self,
        name: str,
        resilience_begin: float,
        resilience_halflife: float,
        resilience_end: float,
        hostility_begin: float,
        hostility_halflife: float,
        hostility_end: float,
    ):

        # Initialize the parent class
        super().__init__(name)

        # Save the personality-specific values
        self.resilience_begin = resilience_begin
        self.resilience_halflife = resilience_halflife
        self.resilience_end = resilience_end
        self.hostility_begin = hostility_begin
        self.hostility_halflife = hostility_halflife
        self.hostility_end = hostility_end


    def resilience(self, t: int | float) -> float:
        return self.resilience_end + (self.resilience_begin - self.resilience_end) * exp(-t / self.resilience_halflife * ln(2))


    def hostility(self, t: int | float) -> float:
        return self.hostility_end + (self.hostility_begin - self.hostility_end) * exp(-t / self.hostility_halflife * ln(2))


    def __get_directions(
        self, which: Literal["towards", "away"]
    ) -> list[Literal["go north", "go south", "go east", "go west"]]:
        """
        Get the directions that move towards or away from the cornucopia.
        """
        # Get the current position of the character
        x = self.current_state["characters"][self.name]["state"]["x"]
        y = self.current_state["characters"][self.name]["state"]["y"]

        # Get actions that move towards or away from the cornucopia
        current_distance_to_cornucopia = abs(x) + abs(y)
        directions_towards_cornucopia = []
        directions_away_from_cornucopia = []
        for (dx, dy, action) in [(0, 1, "go north"), (0, -1, "go south"), (1, 0, "go east"), (-1, 0, "go west")]:
            new_distance_to_cornucopia = abs(x + dx) + abs(y + dy)
            if new_distance_to_cornucopia < current_distance_to_cornucopia:
                directions_towards_cornucopia.append(action)
            elif new_distance_to_cornucopia > current_distance_to_cornucopia:
                directions_away_from_cornucopia.append(action)

        # If empty, add "stay" to the list
        if not directions_towards_cornucopia:
            directions_towards_cornucopia = ["stay"]
        if not directions_away_from_cornucopia:
            directions_away_from_cornucopia = ["stay"]

        # Return
        if which == "towards":
            return directions_towards_cornucopia
        elif which == "away":
            return directions_away_from_cornucopia
        else:
            raise ValueError(f"Unknown value for `which`: {which}")


    def __aggregate_factors(self, proportional_to: list[float], antiproportional_to: list[float]) -> float:
        """
        Aggregate factors and computes a value that should be proportional to
        the sum of the factors in `proportional_to` and antiproportional to the
        sum of the factors in `antiproportional_to`. All factors should be in
        the range [0, 1].
        """
        return utils.map_range(
            sum(proportional_to) - sum(antiproportional_to),
            -len(antiproportional_to),
            len(proportional_to),
            0,
            1,
        )


    def interrogate(self) -> str:

        # Easy access to the personality values
        resilience = self.resilience()
        hostility = self.hostility()
        day = self.current_state["game"]["state"]["day"]
        time = self.current_state["game"]["state"]["time"]
        phase = self.current_state["game"]["state"]["phase"]

        # Compute some useful coefficients
        needs_food_coef = utils.map_range(self.current_state["characters"][self.name]["state"]["hunger"], 0, constants.MAX_HUNGER, 1, 0)
        needs_water_coef = utils.map_range(self.current_state["characters"][self.name]["state"]["thirst"], 0, constants.MAX_THIRST, 1, 0)
        needs_resources_coef = max(needs_food_coef, needs_water_coef)
        is_night_coef = 1 if time == "night" else 0
        has_weapon_coef = 1 if self.current_state["characters"][self.name]["state"]["bag_weapons_count"] > 0 else 0

        if day == 0:
            run_towards_weight = self.__aggregate_factors([hostility, resilience], [])
            run_away_weight = self.__aggregate_factors([resilience], [hostility])
            return random.choices(
                ["run towards", "run away"],
                weights=[run_towards_weight, run_away_weight],
            )[0]

        elif phase == "move":
            move_towards_weight = self.__aggregate_factors([hostility, resilience, needs_resources_coef], [has_weapon_coef])
            move_away_weight = self.__aggregate_factors([resilience, has_weapon_coef, needs_resources_coef], [hostility])
            return random.choices(
                [
                    random.choice(self.__get_directions("towards")),
                    random.choice(self.__get_directions("away")),
                ],
                weights=[move_towards_weight, move_away_weight],
            )[0]

        elif phase == "act":
            hunt_weight = self.__aggregate_factors([hostility, has_weapon_coef], [needs_resources_coef])
            gather_weight = self.__aggregate_factors([resilience, needs_resources_coef], [is_night_coef])
            rest_weight = self.__aggregate_factors([is_night_coef], []) * 0.5
            hide_weight = self.__aggregate_factors([resilience], [has_weapon_coef, hostility]) * 0.5
            return random.choices(
                ["hunt", "gather", "rest", "hide"],
                weights=[hunt_weight, gather_weight, rest_weight, hide_weight],
            )[0]
