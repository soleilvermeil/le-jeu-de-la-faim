from .base_agent import BaseAgent
import random
from ..utils import random_bool
from ..core import constants


class RandomAgent(BaseAgent):
    
    def __init__(self, name: str):

        # Initialize the parent class
        super().__init__(name)


    def interrogate(self) -> str:
        """
        Ask the LLM to chose an action based on the current state of the game,
        which has been given to it by the `give_state_of_game` method.
        """

        # Chose first round's action
        if self.current_state["game"]["state"]["day"] == 0:
            return random.choices(["run towards", "run away"], weights=[1, 1])[0]
        
        # Chose movement if phase is "move"
        if self.current_state["game"]["state"]["phase"] == "move":
            
            if random_bool(0.5):
                return random.choice(["go north", "go south", "go east", "go west"])
            else:
                return "stay"

        # Critical behaviour if hungry or thirsty
        hunger = self.current_state["characters"][self.name]["state"]["hunger"]
        thirst = self.current_state["characters"][self.name]["state"]["thirst"]
        if random_bool(1 - ((hunger - 1) // constants.MAX_HUNGER)) or random_bool(1 - ((thirst - 1) // constants.MAX_THIRST)):
            return "gather"

        # Critical behaviour if sleepy
        energy = self.current_state["characters"][self.name]["state"]["energy"]
        mental = self.current_state["characters"][self.name]["state"]["mental"]
        if self.current_state["game"]["state"]["time"] == "night" and random_bool(1 - ((energy - 1) // constants.MAX_ENERGY)):
            return "rest"
        
        # If at least one opponent spotted, hunt or hide
        if self.current_state["characters"][self.name]["state"]["current_spotted_characters"]:
            return random.choice(["hunt", "hide"])

        # Default behaviour if everything is fine
        return random.choice(["hunt", "hide", "gather"])
