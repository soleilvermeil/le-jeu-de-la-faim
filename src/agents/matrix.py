import random
from typing import Literal
import numpy as np
from .base import BaseAgent
from ..engine import constants
from ..shared import utils


class MatrixAgent(BaseAgent):

    def __init__(
        self,
        name: str,
        matrix: np.ndarray | None = None,
    ):

        # Initialize the parent class
        super().__init__(name)

        # Give all possible actions
        self.actions = [
            "run towards",
            "run away",
            "go north",
            "go south",
            "go east",
            "go west",
            "stay",
            "hunt",
            "gather",
            "rest",
            "hide",
        ]

        # If matrix is provided, check its dimensions
        height = len(self.actions)
        width = 5
        if matrix:
            if matrix.shape != (height, width):
                raise ValueError(f"Matrix should have shape ({height}, {width})")

        # If no matrix is provided, use a random one
        if matrix is None:
            matrix = np.random.rand(height, width)


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

        # Easy access to some quantities
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
            allowed_actions: list = ["run towards", "run away"]
        elif phase == "move":
            allowed_actions: list = ["go north", "go south", "go east", "go west", "stay"]
        elif phase == "act":
            allowed_actions: list = ["hunt", "gather", "rest", "hide"]

        # Compute the input vector
        input_vector: np.ndarray = np.array([
            needs_food_coef,
            needs_water_coef,
            needs_resources_coef,
            is_night_coef,
            has_weapon_coef,
        ])

        # Compute the output vector
        output_vector = self.matrix @ input_vector

        # Get the best action
        allowed_actions_indices = [self.actions.index(action) for action in allowed_actions]
        best_action_index = np.argmax(output_vector[allowed_actions_indices])
        best_action = self.actions[best_action_index]
        return best_action
