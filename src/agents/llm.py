import os
import json
import yaml
from openai import OpenAI
from pydantic import BaseModel, Field
from enum import Enum
from .base import BaseAgent
from ..shared import utils


# Custom YAML dumper to handle multiline strings
class LiteralDumper(yaml.SafeDumper):
    pass
def str_presenter(dumper, data):
    data = utils.wrap_text(data, width=80)
    if '\n' in data:
        data = utils.replace_all(data, ' \n', '\n')
        return dumper.represent_scalar('tag:yaml.org,2002:str', data, style='|')
    return dumper.represent_scalar('tag:yaml.org,2002:str', data)
LiteralDumper.add_representer(str, str_presenter)


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


class LLMAgent(BaseAgent):

    def __init__(
        self,
        name: str,
        api_key: str,
        system_prompt: str,
        verbose: bool,
    ):

        # Initialize the parent class
        super().__init__(name)

        # Create the client
        self.client = OpenAI(api_key=api_key)

        # Create the discussion
        self.discussion = [{
            "role": "system",
            "content": system_prompt,
        }]

        # Create the parsed response history
        self.parsed_response_history = []

        # Set verbosity
        self.verbose = verbose


    def interrogate(self) -> str:
        """
        Ask the agent to chose an action based on the current state of the game,
        which has been given to it by the `give_state_of_game` method.
        """

        # Build message to send
        new_user_message = "\n".join([
            # str2border("Public POV (begin)"),
            # super().messages2str(self.current_state["game"]["messages"]),
            # str2border("Public POV (end)"),
            # str2border("Private POV (begin)"),
            super().messages2str(self.current_state["characters"][self.name]["messages"]),
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


    def inform_death(self) -> None:

        # Build message to send
        new_user_message = "\n".join([
            # str2border("Public POV (begin)"),
            # super().messages2str(self.current_state["game"]["messages"]),
            # str2border("Public POV (end)"),
            # str2border("Private POV (begin)"),
            super().messages2str(self.current_state["characters"][self.name]["messages"]),
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
