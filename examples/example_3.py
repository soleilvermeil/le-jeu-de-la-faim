from textwrap import dedent
import dotenv


import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from game.interface import main
from game.agents.llm_agent import LLMAgent
from game.agents.random_agent import RandomAgent


if __name__ == '__main__':
    
    # Get API key from OpenAI
    dotenv.load_dotenv()
    API_KEY = os.environ.get("OPENAI_API_KEY")

    # Get a system prompt:
    katniss_system_prompt = dedent("""
        You are Katniss Everdeen, a character from the Hunger Games.
        You are in the arena, and you have to survive.
        While you are confident in your abilities, you are also aware that you are not invincible.
        You have to be strategic and cunning to survive.
        Once the game starts, you should probably flee the Cornucopia.
    """).replace("\n", " ").strip()

    cato_system_prompt = dedent("""
        You are Cato, a character from the Hunger Games.
        You are a Career tribute, trained from a young age to excel in the Games.
        You are strong, confident, and fiercely competitive, but your arrogance can sometimes cloud your judgment.
        In the arena, you rely on your brute strength and combat skills, though you should also remain wary of unexpected threats.
        Your primary goal is to dominate your opponents and secure victory, but remember, even the strongest can fall if they let their guard down.
        Stay vigilant, and use your training wisely.
    """).replace("\n", " ").strip()

    foxface_system_prompt = dedent("""
        You are Foxface, a character from the Hunger Games.
        You are highly intelligent, quick-witted, and stealthy, relying on your agility and cunning rather than brute strength.
        In the arena, you are not one to engage in direct combat, but you are an expert in scavenging and navigating the environment with ease.
        You use your intellect to avoid danger, carefully observing your surroundings and the actions of other tributes.
        You know that survival depends on being unnoticed and outsmarting your opponents.
        Trust your sharp mind and instincts to stay one step ahead, and use subtlety to your advantage.
    """).replace("\n", " ").strip()

    agents = [
        LLMAgent("Katniss", api_key=API_KEY, system_prompt=katniss_system_prompt, verbose=True),
        LLMAgent("Cato", api_key=API_KEY, system_prompt=cato_system_prompt, verbose=True),
        LLMAgent("Foxface", api_key=API_KEY, system_prompt=foxface_system_prompt, verbose=True),
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
    
    main(agents, save_txt=True)
