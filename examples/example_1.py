# Add the parent directory to the path so we can import the game module
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))


# Importing game module
from game.agents.random_agent import RandomAgent
from game.interface import main


if __name__ == '__main__':
    
    agents = [
        RandomAgent("Alpha"),
        RandomAgent("Bravo"),
        RandomAgent("Charlie"),
        RandomAgent("Delta"),
        RandomAgent("Echo"),
        RandomAgent("Foxtrot"),
        RandomAgent("Golf"),
        RandomAgent("Hotel"),
        RandomAgent("India"),
        RandomAgent("Juliet"),
        RandomAgent("Kilo"),
        RandomAgent("Lima"),
        RandomAgent("Mike"),
        RandomAgent("November"),
        RandomAgent("Oscar"),
        RandomAgent("Papa"),
        RandomAgent("Quebec"),
        RandomAgent("Romeo"),
        RandomAgent("Sierra"),
        RandomAgent("Tango"),
        RandomAgent("Uniform"),
        RandomAgent("Victor"),
        RandomAgent("Whiskey"),
        RandomAgent("Xray"),
        RandomAgent("Yankee"),
        RandomAgent("Zulu"),
    ]
    
    main(agents, verbose=True)
