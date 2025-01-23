# Add the parent directory to the path so we can import the game module
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))


# Importing game module
from src.api import api
from src.agents import RandomAgent


if __name__ == '__main__':

    agents = [RandomAgent(name=str(i)) for i in range(24)]

    api(agents=agents, save_txt=True, save_tsv=True)
