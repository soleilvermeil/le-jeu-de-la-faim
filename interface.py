from typing import List, Literal
import random
import copy
import os
import re
from openai import OpenAI
from pydantic import BaseModel, Field
from enum import Enum
import game
import game.constants
from utils import *


def messages2str(messages: List[str]) -> str:
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


def str2border(s: str, total_length: int = 50) -> str:
    """
    Returns a string with a border around it.
    """
    return f"{s:-<{total_length}}"


class Action(str, Enum):
    RUN_TOWARDS = "run towards"
    RUN_AWAY = "run away"
    HUNT = "hunt"
    GATHER = "gather"
    REST = "rest"
    HIDE = "hide"
    GO_NORTH = "go north"
    GO_SOUTH = "go south"
    GO_EAST = "go east"
    GO_WEST = "go west"
    STAY = "stay"
    

class Response(BaseModel):
    # personal_situation_analysis: str = Field(description="The character's analysis of their personal situation, notably on their immediate needs.")
    # world_situation_analysis: str = Field(description="The character's analysis of the overall game, notably on their opponents.")
    # thoughts: str = Field(description="The character's reflections or inner dialogue, providing insight into their thinking process, based on their personality.")
    story: str = Field(description="The story or narrative that the character is experiencing, from a first-person perspective.")
    story_fr: str = Field(description="French translation of the field 'story'.")
    action: Action = Field(description="The action being taken.")


class Agent:
    def __init__(self, name: str, model: Literal["random", "ChatGPT", "cmd"] | Dict[str, float]):
        self.model = model
        self.name = name
        self.dna = [random.random() for _ in range(100)]
        
        if model == "ChatGPT":
            self.client = OpenAI()
            system_prompt = open(os.path.join("ChatGPT", "system.txt")).read()
            system_prompt = system_prompt.strip()
            
            personnality = random.choice(game.constants.PERSONNALITIES)
            system_prompt += "\n\n"
            system_prompt += f"You are {name}, a tribute in the Hunger Games. You are {personnality[0]}. {personnality[1]}"
            
            self.history = [{
                "role": "system",
                "content": system_prompt,
            }]


    def give_state_of_game(self, game_state: str) -> None:
        """
        Sends the current state of the game to the LLM, which will later be
        used to make a decision.
        """
        self.current_state = game_state


    def interrogate(self) -> str:
        """
        Ask the LLM to chose an action based on the current state of the game,
        which has been given to it by the `give_state_of_game` method.
        """

        # Get the possible actions
        full_message = messages2str(self.current_state["players"][self.name]["private_messages"])

        # Start by getting the text in parentheses
        possible_actions_bulk = re.findall(r"\((.*?)\)", full_message)[-1]
        
        # Split by `, `
        possible_actions = possible_actions_bulk.split(", ")

        if self.model.startswith("random"):

            # Chose first round's action
            if self.current_state["game"]["day"] == 0:
                return random.choices(["run towards", "run away"], weights=[1, 1])[0]
            
            # Chose movement if phase is "move"
            if self.current_state["game"]["phase"] == "move":
                
                if random_bool(0.5):
                    return random.choice(["go north", "go south", "go east", "go west"])
                else:
                    return "stay"

            # Critical behaviour if hungry or thirsty
            hunger = self.current_state["players"][self.name]["state"]["hunger"]
            thirst = self.current_state["players"][self.name]["state"]["thirst"]
            if hunger <= game.constants.MAX_HUNGER // 2 or thirst <= game.constants.MAX_THIRST // 2:
                return "gather"

            # Critical behaviour if sleepy
            energy = self.current_state["players"][self.name]["state"]["energy"]
            mental = self.current_state["players"][self.name]["state"]["mental"]
            if energy <= 1 and self.current_state["game"]["time"] == "night":
                return "rest"
            
            # If at least one opponent spotted, hunt or hide
            if self.current_state["players"][self.name]["state"]["current_spotted_players"]:
                return random.choice(["hunt", "hide"])

            # Default behaviour if everything is fine
            return random.choice(["hunt", "hide", "gather"])


        elif self.model == "ChatGPT":
            
            # Build message to send
            message_to_send = (
                str2border("Public POV (begin)") + "\n" + messages2str(self.current_state["game"]["public_messages"]) + "\n" + str2border("Public POV (end)") + "\n" + 
                str2border("Private POV (begin)") + "\n" + messages2str(self.current_state["players"][self.name]["private_messages"]) + "\n" + str2border("Private POV (end)") + "\n"
            )

            final_message_to_send = {
                "role": "user",
                "content": message_to_send
            }
            whole_conversation = self.history + [final_message_to_send]
            
            # Send the current state to the model
            response = self.client.beta.chat.completions.parse(
                model="gpt-4o-mini",
                messages=whole_conversation,
                # response_format={
                #     "type": "json_schema",
                #     "json_schema": self.schema
                # }
                response_format=Response,
            )
            
            # Update the history
            self.history.append(final_message_to_send)
            self.history.append({
                "role": "assistant",
                "content": response.choices[0].message.content
            })
            
            # Write the response to a file
            os.makedirs("logs", exist_ok=True)
            with open(os.path.join("logs", f"log_{self.current_state['game']['id']}_{self.name}.txt"), "w", encoding="utf8") as f:
                for i, h in enumerate(self.history):
                    if i > 0:
                        f.write("-" * 50 + "\n")
                    f.write(h["role"] + "\n")
                    f.write(h["content"] + "\n")
            
            # Return
            return response.choices[0].message.parsed.action


        elif self.model == "cmd":

            # Print to console the private message
            print(messages2str(self.current_state["players"][self.name]["private_messages"]))

            action = ""

            while action not in possible_actions:

                # Ask the user to input an action
                action = input(f"What do you want to do? ({possible_actions})\n")

            # Return
            return action

        else:

            raise ValueError(f"Model {self.model} not recognized.")
            
    def is_alive(self) -> bool:
        return self.current_state["players"][self.name]["state"]["alive"]
            

def main(agents: List[Agent], verbose: bool = False) -> None:

    # Create the game object
    game_ = game.Game(character_names=[agent.name for agent in agents])

    # Start the game
    game_.start_game()

    # Define the state and the state history
    state = {}
    state_history = []

    while not state or len(state["game"]["alive_characters"]) > 1:

        # Get the current state of the game
        state = game_.get_state_of_game()

        # Save the state
        state_history.append(copy.deepcopy(state))
        
        # Print the public messages
        if verbose:
            print(str2border("PUBLIC BEGIN"))
            print(messages2str(state["game"]["public_messages"]))
            print(str2border("PUBLIC END"))
            
        # Send to all agents the state of the game
        for agent in agents:

            # If player has been dead last turn, skip
            if len(state_history) >= 2 and not state_history[-2]["players"][agent.name]["state"]["alive"]:
                continue
            
            # Communicate the state of the game to the agent
            agent.give_state_of_game(state)

            # Print the private messages
            if verbose:
                print(str2border(f"{agent.name}'s turn BEGIN"))
                print(messages2str(state["players"][agent.name]["private_messages"]))
                print(str2border(f"{agent.name}'s turn END"))

        # If only a single player is left, exit the loop
        if len(state["game"]["alive_characters"]) == 1:
            break

        # Ask each agent to make a decision
        for agent in agents:
            
            # Check if still alive
            if not state["players"][agent.name]["state"]["alive"]:
                continue

            # Ask the agent to make a decision if the player is still alive
            action = agent.interrogate()

            # Send the decision to the game
            game_.set_action(agent.name, action)

        # Update the game once all agents have made their decisions
        game_.update_game()

    # Print the winner
    if verbose:
        print("Game over! Winner is " + smart_join(lst=[c.name for c in game_.get_alive_characters()], sep=", ", last_sep=" and ") + "!")

    # Save the game log
    debug_messages = []
    for state in state_history:
        debug_messages.append(messages2str(state["debug"]))
        debug_messages.append("")
    os.makedirs("logs", exist_ok=True)
    with open(os.path.join("logs", f"log_{game_.id}.txt"), "w", encoding="utf8") as f:
        f.write(messages2str(debug_messages) + "\n")
