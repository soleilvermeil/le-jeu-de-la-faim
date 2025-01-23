# Add the parent directory to the path so we can import the game module
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))


# Importing game module
from src.api import api
from src.agents.personality import PersonalityAgent


# Importing other modules
import random


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
    
    # Define agents names
    AGENT_NAMES = [
        "Alpha",
        "Bravo",
        "Charlie",
        "Delta",
        "Echo",
        "Foxtrot",
        "Golf",
        "Hotel",
        "India",
        "Juliet",
        "Kilo",
        "Lima",
        "Mike",
        "November",
        "Oscar",
        "Papa",
        "Quebec",
        "Romeo",
        "Sierra",
        "Tango",
        "Uniform",
        "Victor",
        "Whiskey",
        "Xray",
        "Yankee",
        "Zulu",
    ]

    # Select a personnality for each agent
    personnalities = {
        name: random.choice(list(PERSONNALITIES.keys()))
        for name in AGENT_NAMES
    }

    # Print the agents
    for name, model in personnalities.items():
        print(f"{name} is {model}")

    # Create agents    
    agents = [
        PersonalityAgent(
            name=name,
            resilience=PERSONNALITIES[model]["resilience"],
            hostility=PERSONNALITIES[model]["hostility"],
        )
        for name, model in personnalities.items()
    ]

    # Run the game
    api(agents, save_txt=True)
