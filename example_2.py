from interface import Agent, main
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
        Agent(name=name, model=PERSONNALITIES[model])
        for name, model in personnalities.items()
    ]

    # Run the game
    main(agents, save_txt=True)
