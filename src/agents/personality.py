import random
from typing import Literal
from .base import BaseAgent
from ..engine import constants
from ..shared import utils


class PersonalityAgent(BaseAgent):

    def __init__(
        self,
        name: str,
        hostility: float,
        resilience: float,
    ):

        # Initialize the parent class
        super().__init__(name)

        # Save the personality-specific values
        self.resilience = resilience
        self.hostility = hostility


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


    def interrogate_deprecated(self) -> str:
        """
        Ask the LLM to chose an action based on the current state of the game,
        which has been given to it by the `give_state_of_game` method.
        """

        # Easy access to the resilience and hostility
        resilience = self.resilience
        hostility = self.hostility

        if self.current_state["game"]["state"]["day"] == 0:

            # Characters are more likely to run towards the cornucopia if
            # they are more hostile and less resilient
            return random.choices(
                ["run towards", "run away"],
                weights=[
                    utils.map_range(hostility - resilience, -1, 1, 0, 1),
                    utils.map_range(resilience - hostility, -1, 1, 0, 1),
                ]
            )[0]

        elif self.current_state["game"]["state"]["phase"] == "move":

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

            # If no direction allows to move closer or further from the
            # cornucopia, also consider staying in place
            if not directions_towards_cornucopia:
                directions_towards_cornucopia = ["stay"]
            if not directions_away_from_cornucopia:
                directions_away_from_cornucopia = ["stay"]

            # Characters are more likely to move towards the cornucopia if
            # they are more hostile and less resilient
            return random.choices([
                random.choice(directions_away_from_cornucopia),
                random.choice(directions_towards_cornucopia),
            ], weights=[
                utils.map_range(hostility - resilience, -1, 1, 1, 0),
                utils.map_range(hostility - resilience, -1, 1, 0, 1)
            ])[0]

        else:

            # Get the current state of the character
            hunger = self.current_state["characters"][self.name]["state"]["hunger"]
            thirst = self.current_state["characters"][self.name]["state"]["thirst"]
            energy = self.current_state["characters"][self.name]["state"]["energy"]

            # Chose actiopn
            return random.choices(
                ["hunt", "gather", "rest", "hide"],
                weights=[
                    1.0 * utils.map_range(hostility, 0, 1, 0, 1),
                    1.0 * utils.map_range(resilience, 0, 1, 0, 1) * max(utils.map_range(hunger, 0, constants.MAX_HUNGER, 1, 0), utils.map_range(thirst, 0, constants.MAX_THIRST, 1, 0)),
                    0.5 * utils.map_range(resilience, 0, 1, 1, 0) * utils.map_range(energy, 0, constants.MAX_ENERGY, 1, 0),
                    0.5 * utils.map_range(hostility - resilience, -1, 1, 1, 0),
                ]
            )[0]


    def interrogate(self) -> str:

        """
        Ask the LLM to chose an action based on the current state of the game,
        which has been given to it by the `give_state_of_game` method.
        """

        # Easy access to the resilience and hostility
        resilience = self.resilience
        hostility = self.hostility
        has_weapon = self.current_state["characters"][self.name]["state"]["bag_weapons_count"] > 0

        if self.current_state["game"]["state"]["day"] == 0:

            # Characters are more likely to run towards the cornucopia if
            # they are more hostile and less resilient
            return random.choices(
                ["run towards", "run away"],
                weights=[
                    utils.map_range(hostility - resilience, -1, 1, 0, 1),
                    utils.map_range(resilience - hostility, -1, 1, 0, 1),
                ]
            )[0]

        elif self.current_state["game"]["state"]["phase"] == "move":

            # If no weapon, characters are more likely to move towards the
            # cornucopia if they are more hostile and less resilient. If they
            # have a weapon, characters are more likely to move towards the
            # cornucopia if they are less resilient (ignoring hostility).
            if not has_weapon:
                return random.choices([
                    random.choice(self.__get_directions("towards")),
                    random.choice(self.__get_directions("away")),
                ], weights=[
                    utils.map_range(hostility - resilience, -1, 1, 0, 1),
                    utils.map_range(resilience - hostility, -1, 1, 0, 1),
                ])[0]
            else:
                return random.choices([
                    random.choice(self.__get_directions("towards")),
                    random.choice(self.__get_directions("away")),
                ], weights=[
                    utils.map_range(resilience, 0, 1, 0, 1),
                    utils.map_range(resilience, 0, 1, 1, 0),
                ])[0]

        elif self.current_state["game"]["state"]["phase"] == "act":

            # Critical behavior: gather if hungry or thirsty
            # ----------------------------------------------

            # Characters with high resilience are more likely to gather early
            # on. In other terms, their hunger and thirst thresholds are
            # higher.
            hunger_threshold = utils.map_range(resilience, 0, 1, 0.25, 0.75) * constants.MAX_HUNGER
            thirst_threshold = utils.map_range(resilience, 0, 1, 0.25, 0.75) * constants.MAX_THIRST
            if self.current_state["characters"][self.name]["state"]["hunger"] < hunger_threshold:
                return "gather"
            elif self.current_state["characters"][self.name]["state"]["thirst"] < thirst_threshold:
                return "gather"

            # If not critical, do other possible actions randomly
            # ---------------------------------------------------

            # Characters are more likely to hunt if they have a weapon and are
            # more hostile.
            # Range = [0, 2]
            hunt_factor = utils.map_range(hostility, 0, 1, 0.0, 1.0)
            if has_weapon:
                hunt_factor *= 2

            # Characters are more likely to rest if they are more resilient,
            # if they have low energy, and if it is during night.
            # Range = [0, 1]
            rest_factor = utils.map_range(resilience, 0, 1, 0.0, 1.0)
            if self.current_state["game"]["state"]["time"] == "day":
                rest_factor *= 0.5
            energy = self.current_state["characters"][self.name]["state"]["energy"]
            rest_factor *= (constants.MAX_ENERGY - energy) / constants.MAX_ENERGY

            # Characters are more likely to hide if they are less hostile and
            # more resilient.
            # Range = [0, 1]
            hide_factor = utils.map_range(hostility - resilience, -1, 1, 0.0, 1.0)

            # Randomly chose an action if all factors are non-zero
            if hunt_factor + rest_factor + hide_factor == 0:
                return random.choice(["hunt", "rest", "hide"])
            else:
                return random.choices(
                    ["hunt", "rest", "hide"],
                    weights=[hunt_factor, rest_factor, hide_factor]
                )[0]
