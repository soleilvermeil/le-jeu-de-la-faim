import os
import re
from .base import BaseAgent
from ..shared import utils


class CMDAgent(BaseAgent):

    def __init__(self, name: str):

        # Initialize the parent class
        super().__init__(name)


    def interrogate(self) -> str:
        """
        Ask the LLM to chose an action based on the current state of the game,
        which has been given to it by the `give_state_of_game` method.
        """

        # Get the possible actions
        full_message = super().messages2str(self.current_state["characters"][self.name]["messages"])
        possible_actions = re.findall(r"\((.*?)\)", full_message)[-1].split(", ")

        # Clear the console
        os.system("cls" if os.name == "nt" else "clear")

        # Print to console the private message
        print(super().messages2str(self.current_state["characters"][self.name]["messages"]))

        # Ask the user to input an action
        action = utils.smart_input(
            prompt=f"Your action ({', '.join(possible_actions)}): ",
            validator=lambda x: x in possible_actions,
            error_message="Invalid action. Please try again.",
            default=None,
        )

        # Return
        return action


    def inform_death(self) -> None:

        # Clear the console
        os.system("cls" if os.name == "nt" else "clear")

        # Print to console the private message
        print(super().messages2str(self.current_state["characters"][self.name]["messages"]))

        # Print the death message
        print(f"\nYou are dead, {self.name}. Shall your name forever be forgotten.")
