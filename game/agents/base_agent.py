from typing import List


class BaseAgent:
    
    def __init__(self, name: str):
        self.name = name
        self.current_state = None
        

    def __repr__(self):
        return f"{self.__class__.__name__}(name={self.name})"
    
        
    def messages2str(self, messages: List[str]) -> str:
        """
        Returns a string representation of a list of messages.
        """
        # Naive conversion of list of messages to a string
        messages = "\n".join(messages)

        # Removes all newline characters at the start and end of each message
        messages = messages.strip("\n")

        # Removes all triple newline characters with double
        messages = messages.replace("\n\n\n", "\n\n")

        # Return
        return messages


    def str2border(self, s: str, total_length: int = 80) -> str:
        """
        Returns a string with a border around it.
        """
        return f"{s:-<{total_length-1}}"

        

    def give_state_of_game(self, game_state: str) -> None:
        """
        Sends the current state of the game to the LLM, which will later be
        used to make a decision.
        """
        self.current_state = game_state


    def interrogate(self) -> str:
        """
        Ask the agent to chose an action based on the current state of the game,
        which has been given to it by the `give_state_of_game` method.
        """
        raise NotImplementedError("The method `interrogate` must be implemented by the child class.")
    

    def inform_death(self) -> None:
        """
        Inform the agent that the character has died.
        """
        pass
    
            
    def is_alive(self) -> bool:
        """
        Simple method to check if the character is alive.
        """
        return self.current_state["characters"][self.name]["state"]["alive"]
