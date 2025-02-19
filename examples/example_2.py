# Add the parent directory to the path so we can import the game module
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))


# Importing game module
from src.api import api
from src.agents import PersonalityAgent


# Importing other modules
import random


if __name__ == '__main__':

    # Define numerical values
    HIGH = 0.9
    AVERAGE_HIGH = 0.7
    AVERAGE = 0.5
    AVERAGE_LOW = 0.3
    LOW = 0.1

    # Define personalities
    PERSONNALITIES = {
        "cruel": {
            "resilience": AVERAGE,
            "hostility": HIGH,
            "impulsivity": HIGH,
        },
        "sadistic": {
            "resilience": AVERAGE_LOW,
            "hostility": HIGH,
            "impulsivity": AVERAGE_HIGH,
        },
        "strategic": {
            "resilience": HIGH,
            "hostility": AVERAGE,
            "impulsivity": LOW,
        },
        "noble": {
            "resilience": AVERAGE_HIGH,
            "hostility": LOW,
            "impulsivity": AVERAGE,
        },
        "terrified": {
            "resilience": LOW,
            "hostility": LOW,
            "impulsivity": HIGH,
        },
        "charismatic": {
            "resilience": AVERAGE,
            "hostility": AVERAGE_LOW,
            "impulsivity": AVERAGE_LOW,
        },
        "vengeful": {
            "resilience": HIGH,
            "hostility": HIGH,
            "impulsivity": AVERAGE_HIGH,
        },
        "depressed": {
            "resilience": LOW,
            "hostility": LOW,
            "impulsivity": LOW,
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
