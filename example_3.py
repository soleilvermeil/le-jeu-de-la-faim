from interface import Agent, main
import random
import shutil
try:
    from tqdm import tqdm
except ImportError:
    tqdm = lambda x: x


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
    
    AGENTS_PER_PERSONNALITY = 4

    # Define agents
    agents = []
    for personnality in PERSONNALITIES:
        for i in range(AGENTS_PER_PERSONNALITY):
            name = f"{personnality}_{i}"
            agents.append(Agent(name=name, model=PERSONNALITIES[personnality]))

    # Delete the logs folder
    try:
        shutil.rmtree("logs", ignore_errors=True)
    except OSError:
        pass

    # Run the game
    for i in tqdm(range(1000)):
        main(agents, save_tsv=True)
