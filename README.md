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

* **`game/`:** Contains the core game logic, including character management, map generation, weapon definitions, and event handling.
* **`interface.py`:** Provides the interface for interacting with the game, managing agents, and running simulations.
* **`utils.py`:** Contains utility functions used throughout the project.
* **`ChatGPT/`:**  (If using ChatGPT) Contains prompt templates and configuration files for interacting with the OpenAI API.
* **`example_*.py`:** Example scripts demonstrating different usage scenarios, namely
  * `example_1-.py` is a minimal example, with agents set to have a random behaviour;
  * `example_2-.py` is an example where agents have each a given `hostility` and `resilience`, giving more unique behaviours;
  * `example_3-.py` introduces to the use of ChatGPT.
