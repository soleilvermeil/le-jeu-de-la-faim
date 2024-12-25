import random
import copy
import os
import re
from typing import List, Literal
from enum import Enum
from openai import OpenAI              # only for ChatGPT
from pydantic import BaseModel, Field  # only for ChatGPT
import yaml                            # only for ChatGPT logging
import json                            # only for ChatGPT logging
import pandas as pd                    # only for logging
from .core import game
from .core import constants
from .utils import *


# Custom YAML dumper to handle multiline strings
class LiteralDumper(yaml.SafeDumper):
    pass
def str_presenter(dumper, data):
    data = wrap_text(data, width=80)
    if '\n' in data:
        data = replace_all(data, ' \n', '\n')
        return dumper.represent_scalar('tag:yaml.org,2002:str', data, style='|')
    return dumper.represent_scalar('tag:yaml.org,2002:str', data)
LiteralDumper.add_representer(str, str_presenter)


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


def str2border(s: str, total_length: int = 80) -> str:
    """
    Returns a string with a border around it.
    """
    return f"{s:-<{total_length-1}}"


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
    thoughts: str = Field(description="The character's reflections or inner dialogue, providing insight into their thinking process, based on their personality.")
    # story: str = Field(description="The story or narrative that the character is experiencing, from a first-person perspective. Should not exceed one paragraph.")
    # story_fr: str = Field(description="French translation of the field 'story'.")
    action: Action = Field(description="The action being taken.")


class Agent:
    def __init__(self, name: str, model: Literal["random", "personality", "ChatGPT", "cmd"], **kwargs):

        # Save the model and the name
        self.model = model
        self.name = name
        
        if model == "ChatGPT":
            
            # Check arguments in kwargs
            assert "api_key" in kwargs, "API key to OpenAI must be provided."
            assert "system_prompt" in kwargs, "System prompt must be provided."
            assert "verbose" in kwargs, "Verbose must be provided."
            assert isinstance(kwargs["verbose"], bool), "Verbose must be a boolean."

            # Create the client
            self.client = OpenAI(api_key=kwargs["api_key"])

            # Create the discussion
            self.discussion = [{
                "role": "system",
                "content": kwargs["system_prompt"],
            }]

            # Create the parsed response history
            self.parsed_response_history = []

            # Set verbosity
            self.verbose = kwargs["verbose"]

        elif model == "personality":

            # Check arguments in kwargs
            assert "resilience" in kwargs, "Resilience must be provided."
            assert "hostility" in kwargs, "Hostility must be provided."

            # Check if the values are between 0 and 1
            for key in ["resilience", "hostility"]:
                assert 0 <= kwargs[key] <= 1, f"{key} must be between 0 and 1."

            # Save the values
            self.resilience = kwargs["resilience"]
            self.hostility = kwargs["hostility"]

        elif model == "cmd":

            pass

        elif model == "random":

            pass

        else:

            raise ValueError(f"Model {model} not recognized.")

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
        full_message = messages2str(self.current_state["characters"][self.name]["messages"])
        possible_actions = re.findall(r"\((.*?)\)", full_message)[-1].split(", ")

        if self.model == "random":

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

        elif self.model == "ChatGPT":
            
            # Build message to send
            new_user_message = "\n".join([
                # str2border("Public POV (begin)"),
                # messages2str(self.current_state["game"]["messages"]),
                # str2border("Public POV (end)"),
                # str2border("Private POV (begin)"),
                messages2str(self.current_state["characters"][self.name]["messages"]),
                # str2border("Private POV (end)"),
            ])

            payload_to_send = {
                "role": "user",
                "content": new_user_message
            }
            whole_conversation = self.discussion + [payload_to_send]
            
            # Send the current state to the model
            response = self.client.beta.chat.completions.parse(
                model="gpt-4o-mini",
                messages=whole_conversation,
                response_format=Response,
            )
            
            # Update the history
            self.discussion.append(payload_to_send)
            self.discussion.append({
                "role": "assistant",
                "content": response.choices[0].message.content
            })
            self.parsed_response_history.append(response.choices[0].message.parsed)
            
            # Format everything and write it to a file
            if self.verbose:

                # Prepare data
                data = {
                    "system_prompt": self.discussion[0]["content"],
                    "discussion": [],
                }

                for i, d in enumerate(self.discussion):
                    role = d["role"]
                    if role == "user":
                        content = d["content"]
                        data["discussion"].append({"role": role, "content": content})
                    elif role == "assistant":
                        parsed = self.parsed_response_history[(i - 1) // 2]  # TODO: make this more robust
                        data["discussion"].append({"role": role} | json.loads(parsed.json()))

                # Write to file
                os.makedirs("logs", exist_ok=True)
                # with open(os.path.join("logs", f"log_{self.current_state['game']['id']}_{self.name}.json"), "w", encoding="utf8") as f:
                #     json.dump(data, f, indent=4, ensure_ascii=False)
                with open(os.path.join("logs", f"log_{self.current_state['game']['id']}_{self.name}.yaml"), "w", encoding="utf8") as f:
                    yaml.dump(data, Dumper=LiteralDumper, default_flow_style=False, allow_unicode=True, stream=f, sort_keys=False)
            
            # Return
            return response.choices[0].message.parsed.action
        
        elif self.model == "personality":

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

        elif self.model == "cmd":

            # Clear the console
            os.system("cls" if os.name == "nt" else "clear")

            # Print to console the private message
            # print(str2border("Public POV (begin)"))
            # print(messages2str(self.current_state["game"]["messages"]))
            # print(str2border("Public POV (end)"))
            # print(str2border("Private POV (begin)"))
            print(messages2str(self.current_state["characters"][self.name]["messages"]))
            # print(str2border("Private POV (end)"))

            # Ask the user to input an action
            action = smart_input(
                prompt=f"Your action ({', '.join(possible_actions)}): ",
                validator=lambda x: x in possible_actions,
                error_message="Invalid action. Please try again.",
                default=None,
            )

            # Return
            return action

        else:

            # This should never happen
            pass

    def inform_death(self) -> None:

        if self.model == "random":

            pass

        elif self.model == "ChatGPT":

            # Build message to send
            new_user_message = "\n".join([
                # str2border("Public POV (begin)"),
                # messages2str(self.current_state["game"]["messages"]),
                # str2border("Public POV (end)"),
                # str2border("Private POV (begin)"),
                messages2str(self.current_state["characters"][self.name]["messages"]),
                # str2border("Private POV (end)"),
                f"\nYou are dead {self.name}. Shall your name forever be forgotten."
            ])

            # Building a (fake) payload
            death_payload = {
                "role": "user",
                "content": new_user_message
            }
                        
            # Update the history (only the user message)
            self.discussion.append(death_payload)
            
            # Format everything and write it to a file
            if self.verbose:

                # Prepare data
                data = {
                    "system_prompt": self.discussion[0]["content"],
                    "discussion": [],
                }

                for i, d in enumerate(self.discussion):
                    role = d["role"]
                    if role == "user":
                        content = d["content"]
                        data["discussion"].append({"role": role, "content": content})
                    elif role == "assistant":
                        parsed = self.parsed_response_history[(i - 1) // 2]  # TODO: make this more robust
                        data["discussion"].append({"role": role} | json.loads(parsed.json()))

                # Write to file
                os.makedirs("logs", exist_ok=True)
                # with open(os.path.join("logs", f"log_{self.current_state['game']['id']}_{self.name}.json"), "w", encoding="utf8") as f:
                #     json.dump(data, f, indent=4, ensure_ascii=False)
                with open(os.path.join("logs", f"log_{self.current_state['game']['id']}_{self.name}.yaml"), "w", encoding="utf8") as f:
                    yaml.dump(data, Dumper=LiteralDumper, default_flow_style=False, allow_unicode=True, stream=f, sort_keys=False)

        elif self.model == "personality":

            pass

        elif self.model == "cmd":

            # Clear the console
            os.system("cls" if os.name == "nt" else "clear")
            
            # Print to console the private message
            # print(str2border("Public POV (begin)"))
            # print(messages2str(self.current_state["game"]["messages"]))
            # print(str2border("Public POV (end)"))
            # print(str2border("Private POV (begin)"))
            print(messages2str(self.current_state["characters"][self.name]["messages"]))
            # print(str2border("Private POV (end"))

            # Print the death message
            print(f"\nYou are dead, {self.name}. Shall your name forever be forgotten.")
            
    def is_alive(self) -> bool:
        return self.current_state["characters"][self.name]["state"]["alive"]
            

def main(
    agents: List[Agent],
    verbose: bool = False,
    save_txt: bool = False,
    save_tsv: bool = False,
    **kwargs
) -> None:
    
    # Check that all agents are unique
    names = [agent.name for agent in agents]
    assert len(names) == len(unique(names)), "All agents must have unique names."

    # Create the game object
    game_ = game.Game(character_names=[agent.name for agent in agents])

    # Start the game
    game_.start_game()

    # Define the state and the state history
    state = {}
    state_history = []

    while not state or len(state["game"]["state"]["alive_characters"]) > 1:

        # Get the current state of the game
        state = game_.get_state_of_game()

        # Save the state
        state_history.append(copy.deepcopy(state))
        
        # Print the public messages
        if verbose:
            print(str2border(""))
            print(messages2str(state["debug"]["messages"]))
            print(str2border(""))
            
        # Send to all agents the state of the game
        for agent in agents:

            # If character has been dead last turn, skip
            if len(state_history) >= 2 and not state_history[-2]["characters"][agent.name]["state"]["alive"]:
                continue
            
            # Communicate the state of the game to the agent
            agent.give_state_of_game(state)

            # Print the private messages
            # if verbose:
            #     print(str2border(f"{agent.name}'s turn BEGIN"))
            #     print(messages2str(state["characters"][agent.name]["messages"]))
            #     print(str2border(f"{agent.name}'s turn END"))

        # If only a single character is left, exit the loop
        if len(state["game"]["state"]["alive_characters"]) == 1:
            break

        # Ask each agent to make a decision
        for agent in agents:
            
            # Check if still alive. If dead, do only inform about the death
            # if it has not been done already. If still alive, ask for a
            # decision.
            if not state["characters"][agent.name]["state"]["alive"]:
                if len(state_history) >= 2 and state_history[-2]["characters"][agent.name]["state"]["alive"]:
                    agent.inform_death()
                continue
            else:
                action = agent.interrogate()

            # Send the decision to the game
            game_.set_action(agent.name, action)

        # Update the game once all agents have made their decisions
        game_.update_game()

    # Print the winner
    if verbose:
        print("Game over! Winner is " + smart_join(lst=[c.name for c in game_.get_alive_characters()], sep=", ", last_sep=" and ") + "!")

    # Save the game log
    if save_txt:
        os.makedirs("logs", exist_ok=True)
        debug_messages = []
        for state in state_history:
            debug_messages.append(messages2str(state["debug"]["messages"]))
            debug_messages.append("")
        with open(os.path.join("logs", f"log_{game_.id}.txt"), "w", encoding="utf8") as f:
            f.write(messages2str(debug_messages) + "\n")

    # Save the full state history
    if save_tsv:
        os.makedirs("logs", exist_ok=True)
        data = {}
        for state in state_history:
            game_state = state["game"]
            for character in list(state["characters"].keys()):
                character_state = state["characters"][character]
                
                flattened_game_state = flatten_dict({"game": game_state}, list_transform=lambda x: "<list>", str_transform=lambda x: x if "\n" not in x else "<str>")
                flattened_character_state = flatten_dict({"character": character_state}, list_transform=lambda x: "<list>", str_transform=lambda x: x if "\n" not in x else "<str>")
                
                combined_state = {**flattened_game_state, **flattened_character_state}

                if not data:
                    for key in combined_state.keys():
                        data[key] = [combined_state[key]]
                else:
                    for key in combined_state.keys():
                        data[key].append(combined_state[key])
        df = pd.DataFrame(data)
        df.to_csv(os.path.join("logs", f"log_{game_.id}.tsv"), sep="\t", index=False, encoding="utf8")
