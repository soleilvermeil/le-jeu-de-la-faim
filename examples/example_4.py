from typing import List, Tuple


import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from game.interface import Agent, main


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

    tributes = {
        ( 1,   "male"): {"name": "Marvel", "personality": PERSONNALITIES["ruthless/cold-blooded"]},
        ( 1, "female"): {"name": "Glimmer", "personality": PERSONNALITIES["manipulative/charismatic"]},
        ( 2,   "male"): {"name": "Cato", "personality": PERSONNALITIES["ruthless/cold-blooded"]},
        ( 2, "female"): {"name": "Clove", "personality": PERSONNALITIES["strategic/cunning"]},
        ( 3,   "male"): {"name": None, "personality": PERSONNALITIES["strategic/cunning"]},
        ( 3, "female"): {"name": None, "personality": PERSONNALITIES["terrified/timid"]},
        ( 4,   "male"): {"name": None, "personality": PERSONNALITIES["ruthless/cold-blooded"]},
        ( 4, "female"): {"name": None, "personality": PERSONNALITIES["ruthless/cold-blooded"]},
        ( 5,   "male"): {"name": None, "personality": PERSONNALITIES["unhinged/vengeful"]},
        ( 5, "female"): {"name": "Foxface", "personality": PERSONNALITIES["strategic/cunning"]},
        ( 6,   "male"): {"name": None, "personality": PERSONNALITIES["terrified/timid"]},
        ( 6, "female"): {"name": None, "personality": PERSONNALITIES["terrified/timid"]},
        ( 7,   "male"): {"name": None, "personality": PERSONNALITIES["noble/heroic"]},
        ( 7, "female"): {"name": None, "personality": PERSONNALITIES["terrified/timid"]},
        ( 8,   "male"): {"name": None, "personality": PERSONNALITIES["terrified/timid"]},
        ( 8, "female"): {"name": None, "personality": PERSONNALITIES["noble/heroic"]},
        ( 9,   "male"): {"name": None, "personality": PERSONNALITIES["terrified/timid"]},
        ( 9, "female"): {"name": None, "personality": PERSONNALITIES["terrified/timid"]},
        (10,   "male"): {"name": None, "personality": PERSONNALITIES["noble/heroic"]},
        (10, "female"): {"name": None, "personality": PERSONNALITIES["terrified/timid"]},
        (11,   "male"): {"name": "Thresh", "personality": PERSONNALITIES["noble/heroic"]},
        (11, "female"): {"name": "Rue", "personality": PERSONNALITIES["noble/heroic"]},
        (12,   "male"): {"name": "Peeta Mellark", "personality": PERSONNALITIES["manipulative/charismatic"]},
        (12, "female"): {"name": "Katniss Everdeen", "personality": PERSONNALITIES["noble/heroic"]},
    }

    while True:
        name = input("Enter your name: ")
        if name:
            break
    while True:
        district = input("Enter your district number (1-12): ")
        if district.isdigit() and 1 <= int(district) <= 12:
            district = int(district)
            break
    while True:
        gender = input("Are you male or female? (m/f): ")
        if gender in ["m", "f"]:
            gender = {"m": "male", "f": "female"}[gender]
            break

    agents = []
    for key, value in tributes.items():

        name_ = value["name"]
        district_ = key[0]
        gender_ = key[1]

        if district_ == district and gender_ == gender:
            print("You are a {gender} tribute from District {district}.".format(gender=gender_, district=district_))
            agents.append(Agent(
                name=name,
                model="cmd",
            ))
        else:
            if name_ is None:
                name_ = "District {district} {gender}".format(gender=gender_, district=district_)
            agents.append(Agent(
                name=name_,
                model="personality",
                hostility=value["personality"]["hostility"],
                resilience=value["personality"]["resilience"],
            ))
            
    main(agents, verbose=False)
