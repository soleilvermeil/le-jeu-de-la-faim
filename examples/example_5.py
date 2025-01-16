from typing import List, Tuple
from pydantic import BaseModel
from enum import Enum
import dotenv
from openai import OpenAI
import glob
from textwrap import dedent


import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from game.interface import main
from game.agents.cmd_agent import CMDAgent
from game.agents.personality_agent import PersonalityAgent


class Host(str, Enum):
    CAESAR_FLICKERMAN = "Caesar Flickerman"
    CLAUDIUS_TEMPLESMITH = "Claudius Templesmith"


class Step(BaseModel):
    host: Host
    emotion: str
    message_en: str
    message_fr: str


class Response(BaseModel):
    steps: List[Step]


if __name__ == '__main__':

    # Get the last game
    file = sorted(glob.glob("logs/*.txt"))[-1]
    blocks: List[str] = []
    with open(file, "r", encoding="utf8") as f:
        lines = f.readlines()
        for line in lines:
            if "Start of" in line or len(blocks) == 0:
                blocks.append("")
            blocks[-1] += line
    print(f"Found {len(blocks)} blocks")
            
    # Get API key from OpenAI
    dotenv.load_dotenv()
    API_KEY = os.environ.get("OPENAI_API_KEY")

    # Define client
    client = OpenAI()

    # Define messages
    messages = []
    messages.append({
        "role": "system",
        "content": dedent("""
            You are Caesar Flickerman and Claudius Templesmith, the TV presenters for the
            Hunger Games. Caesar is eccentric, playful, and dramatic, often interpreting
            tributes' actions with flair and exaggeration. His catchphrase is “I love it, I
            love it!” Claudius, on the other hand, is serious, analytical, and focused on
            the strategic and practical aspects of the game. Together, they provide a mix
            of entertainment, analysis, and commentary.

            When the user provides a brief and synthetic status of the game, your job is to
            expand on it by inventing vivid and engaging details about the tributes, the
            arena, and the events.

            Caesar should focus on the emotional and narrative aspects of the tributes'
            actions, using colorful language and dramatic interpretations.

            Claudius should highlight strategic maneuvers, alliances, and possible future
            consequences, providing a grounded and analytical perspective.

            To enhance the commentary:
            - Add immersive details about the environment, such as terrain, weather, or
            special features of the arena.
            - Highlight dramatic tension, rivalries, or foreshadow alliances and betrayals,
            even if they aren't explicitly mentioned by the user.
            - Use humor, tension, and spectacle to keep the dialogue entertaining and
            dynamic.

            Each response should consist of a dialogue exchange between Caesar and
            Claudius, with each speaking several times. Build off the initial input and
            create a layered, exciting narrative that feels true to the Hunger Games
            universe.
        """)
    })

    # Define a file to write the output
    new_file = os.path.basename(file).replace(".txt", "_commented.txt")
    f = open(os.path.join("logs", new_file), "a", encoding="utf8")

    # Add blocks
    for block in blocks:

        # Print to console
        print(block.split("\n")[0])

        messages.append({
            "role": "user",
            "content": block,
        })
        completion = client.beta.chat.completions.parse(model="gpt-4o", messages=messages, response_format=Response)
        response = completion.choices[0].message.parsed
        
        # Print the block
        print(block, file=f)

        # Print the response
        for step in response.steps:
            message = step.message_en
            message = message.replace("\n", " ")
            print(f"- [{step.host}] ({step.emotion}) {message}", file=f)
        print(file=f)
        
        # Add the response to the messages
        messages.append({
            "role": "assistant",
            "content": completion.choices[0].message.content.replace("\n", " "),
        })
        
