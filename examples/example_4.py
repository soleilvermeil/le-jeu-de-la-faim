from textwrap import dedent
import dotenv


import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from game.interface import Agent, main


if __name__ == '__main__':
    
    # Get API key from OpenAI
    dotenv.load_dotenv()
    API_KEY = os.environ.get("OPENAI_API_KEY")
    print(API_KEY)

    # Get a system prompt:
    system_prompt = dedent("""
        You are Katniss Everdeen, a character from the Hunger Games.
        You are in the arena, and you have to survive.
        While you are confident in your abilities, you are also aware that you are not invincible.
        You have to be strategic and cunning to survive.
    """).replace("\n", " ").strip()

    agents = [
        Agent("Katniss", "ChatGPT", api_key=API_KEY, system_prompt=system_prompt),
        Agent("Alpha", "random"),
        Agent("Bravo", "random"),
        Agent("Charlie", "random"),
        Agent("Delta", "random"),
        Agent("Echo", "random"),
        Agent("Foxtrot", "random"),
        Agent("Golf", "random"),
        Agent("Hotel", "random"),
        Agent("India", "random"),
        Agent("Juliet", "random"),
        Agent("Kilo", "random"),
        Agent("Lima", "random"),
        Agent("Mike", "random"),
        Agent("November", "random"),
        Agent("Oscar", "random"),
        Agent("Papa", "random"),
        Agent("Quebec", "random"),
        Agent("Romeo", "random"),
        Agent("Sierra", "random"),
        Agent("Tango", "random"),
        Agent("Uniform", "random"),
        Agent("Victor", "random"),
        Agent("Whiskey", "random"),
        Agent("Xray", "random"),
        Agent("Yankee", "random"),
        Agent("Zulu", "random"),
    ]
    
    main(agents, save_txt=True)
