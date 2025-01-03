# Le Jeu de la Faim (Hunger Games Simulator)

This repository contains a Python-based simulator for the Hunger Games.  It allows you to create tributes, assign them different AI models (random, rule-based, or ChatGPT-powered), and simulate the events of the games.

## Key Features:

* **Diverse AI Models:** Experiment with different agent behaviors.  Choose from random actions, predefined personalities with rule-based logic, or integrate the power of ChatGPT for more complex decision-making.
* **Detailed Simulation:** The game simulates various aspects of the Hunger Games, including movement, combat, resource gathering, day/night cycles, and random events.
* **Extensible Framework:**  The modular design allows for easy customization and extension. You can add new AI models, events, and game mechanics.
* **Logging and Analysis:** The simulator provides options for logging game events in detail, enabling analysis of agent performance and game dynamics.  Output can be saved in TXT or TSV format.
* **Example Scripts:**  Includes example scripts (`example_1.py`, `example_2.py`, `example_3.py`) demonstrating different configurations and usage scenarios.

## Getting Started:

1. **Prerequisites:** Ensure you have Python 3 installed along with the required libraries (OpenAI, pydantic).  Example installation:  `pip install openai pydantic` (You may need to install additional libraries depending on the chosen AI model).
2. **Configuration:**  Modify the example scripts or create your own to define the tributes, their AI models, and other game parameters.  For ChatGPT integration, you'll set the variable `OPENAI_API_KEY`.
3. **Run the Simulation:** Execute the Python script to start the simulation.  Use the `verbose` flag to print detailed game events to the console.
4. **Analyze the Results:** Examine the generated log files to understand the progression of the game and the performance of different AI strategies.

## Code Structure:

* **`game/`:** Contains all the game logic and core functionality.
  * **`game/core/`:** Contains the core game logic, including character management, map generation, weapon definitions, and event handling.
  * **`game/agents/`:** Contains the different AI models available for agents, including random, rule-based, ChatGPT-powered and user-controllable agents, namely:
    | File | Model | Description |
    | --- | --- | --- |
    | `random_agent.py` | Random Agent | Makes random decisions while trying to maintain vitals above zero. |
    | `personality_agent.py` | Personality Agent | Makes decisions based on given `hostility` and `resilience` values. |
    | `llm_agent.py` | ChatGPT Agent | Uses ChatGPT to make decisions. |
    | `cmd_agent.py` | User-Controlled Agent | Allows the user to control the agent. |
  * `game/interface.py`: Provides the interface for interacting with the game, managing agents, and running simulations.
  * `game/utils.py`: Contains utility functions used throughout the project.
* **`examples/`:** Contains example scripts demonstrating different usage scenarios.
  * `examples/example_1.py` is a minimal example, with agents set to have a random behaviour;
  * `examples/example_2.py` is an example where agents have each a given `hostility` and `resilience`, giving more unique behaviours;
  * `examples/example_3.py` introduces to the use of ChatGPT.
  * `examples/example_4.py` is an example where one agent is controlled by the user.

## Minimal example

```python
# Depending on the code structure, you may need to adjust the import paths. For
# example, this is used inside the `example_*.py` files:
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

# Import the interface
from game.interface import main

# Import an agent class (e.g. RandomAgent)
from game.agents.random_agent import RandomAgent

# Run the main, giving a list of agents as argument
agents = [RandomAgent("Alice"), RandomAgent("Bob"), RandomAgent("Charlie")]
main(agents)
```