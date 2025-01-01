from .base_agent import BaseAgent
import random
from ..core import constants
from ..utils import map_range
from rich.traceback import install
install()


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


    def interrogate(self) -> str:
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
                    map_range(hostility - resilience, -1, 1, 0, 1),
                    map_range(hostility - resilience, -1, 1, 1, 0)
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
                map_range(hostility - resilience, -1, 1, 1, 0),
                map_range(hostility - resilience, -1, 1, 0, 1)
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
                    1.0 * map_range(hostility, 0, 1, 0, 1),
                    1.0 * map_range(resilience, 0, 1, 0, 1) * max(map_range(hunger, 0, constants.MAX_HUNGER, 1, 0), map_range(thirst, 0, constants.MAX_THIRST, 1, 0)),
                    0.5 * map_range(resilience, 0, 1, 1, 0) * map_range(energy, 0, constants.MAX_ENERGY, 1, 0),
                    0.5 * map_range(hostility - resilience, -1, 1, 1, 0),
                ]
            )[0]
