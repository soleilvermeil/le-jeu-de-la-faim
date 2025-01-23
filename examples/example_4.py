# Add the parent directory to the path so we can import the game module
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))


# Importing game module
from src.api import api
from src.agents.cmd import CMDAgent, PersonalityAgent
from src.shared import utils


# Importing other modules
from typing import List, Tuple


if __name__ == '__main__':

    # Define numerical values
    HIGH = 0.8
    UNSPECIFIED = 0.5
    LOW = 0.2

    # Define personalities
    PERSONNALITIES = {
        "ruthless/cold-blooded": {
            "resilience": UNSPECIFIED,
            "hostility": HIGH,
        },
        "strategic/cunning": {
            "resilience": HIGH,
            "hostility": UNSPECIFIED,
        },
        "noble/heroic": {
            "resilience": UNSPECIFIED,
            "hostility": LOW,
        },
        "terrified/timid": {
            "resilience": HIGH,
            "hostility": LOW,
        },
        "manipulative/charismatic": {
            "resilience": UNSPECIFIED,
            "hostility": UNSPECIFIED,
        },
        "unhinged/vengeful": {
            "resilience": HIGH,
            "hostility": HIGH,
        }
    }

    # Define tributes
    tributes = {
        ( 1,   "male"): {"name": "Marvel", "personality": PERSONNALITIES["ruthless/cold-blooded"]},
        ( 1, "female"): {"name": "Glimmer", "personality": PERSONNALITIES["manipulative/charismatic"]},
        ( 2,   "male"): {"name": "Cato", "personality": PERSONNALITIES["ruthless/cold-blooded"]},
        ( 2, "female"): {"name": "Clove", "personality": PERSONNALITIES["strategic/cunning"]},
        ( 3,   "male"): {"name": None, "personality": PERSONNALITIES["strategic/cunning"]},
        ( 3, "female"): {"name": None, "personality": PERSONNALITIES["terrified/timid"]},
        ( 4,   "male"): {"name": None, "personality": PERSONNALITIES["ruthless/cold-blooded"]},
        ( 4, "female"): {"name": None, "personality": PERSONNALITIES["ruthless/cold-blooded"]},
        ( 5,   "male"): {"name": None, "personality": PERSONNALITIES["unhinged/vengeful"]},
        ( 5, "female"): {"name": "Foxface", "personality": PERSONNALITIES["strategic/cunning"]},
        ( 6,   "male"): {"name": None, "personality": PERSONNALITIES["terrified/timid"]},
        ( 6, "female"): {"name": None, "personality": PERSONNALITIES["terrified/timid"]},
        ( 7,   "male"): {"name": None, "personality": PERSONNALITIES["noble/heroic"]},
        ( 7, "female"): {"name": None, "personality": PERSONNALITIES["terrified/timid"]},
        ( 8,   "male"): {"name": None, "personality": PERSONNALITIES["terrified/timid"]},
        ( 8, "female"): {"name": None, "personality": PERSONNALITIES["noble/heroic"]},
        ( 9,   "male"): {"name": None, "personality": PERSONNALITIES["terrified/timid"]},
        ( 9, "female"): {"name": None, "personality": PERSONNALITIES["terrified/timid"]},
        (10,   "male"): {"name": None, "personality": PERSONNALITIES["noble/heroic"]},
        (10, "female"): {"name": None, "personality": PERSONNALITIES["terrified/timid"]},
        (11,   "male"): {"name": "Thresh", "personality": PERSONNALITIES["noble/heroic"]},
        (11, "female"): {"name": "Rue", "personality": PERSONNALITIES["noble/heroic"]},
        (12,   "male"): {"name": "Peeta", "personality": PERSONNALITIES["manipulative/charismatic"]},
        (12, "female"): {"name": "Katniss", "personality": PERSONNALITIES["noble/heroic"]},
    }

    # Get user input
    name = utils.smart_input(
        prompt="Enter your name: ",
        validator=lambda x: x,
        error_message="Invalid name. Please try again.",
        default="Katniss",
    )
    district = int(utils.smart_input(
        prompt="Enter your district number (1-12): ",
        validator=lambda x: x.isdigit() and 1 <= int(x) <= 12,
        error_message="Invalid district number. Please enter a number between 1 and 12.",
        default=12,
    ))
    gender = {"m": "male", "f": "female"}[utils.Anysmart_input(
        prompt="Are you male or female? (m/f): ",
        validator=lambda x: x in ["m", "f"],
        error_message="Invalid gender. Please enter 'm' or 'f'.",
        default="f",
    )]

    # Create agents
    agents = []
    for key, value in tributes.items():

        # Get values
        name_ = value["name"]
        district_ = key[0]
        gender_ = key[1]

        # If the agent is equal to the user's input, replace it with the user
        if district_ == district and gender_ == gender:
            agents.append(CMDAgent(name=name))

        # Otherwise, create the agent with the predefined values
        else:
            if name_ is None:
                name_ = "District {district} {gender}".format(gender=gender_, district=district_)
            agents.append(PersonalityAgent(
                name=name_,
                hostility=value["personality"]["hostility"],
                resilience=value["personality"]["resilience"],
            ))

    # Start the game
    api(agents, verbose=False)
