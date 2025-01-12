from typing import List, Dict, Tuple, Literal
import datetime
import random
import itertools
import json
from ..utils import *
from .constants import *
from .character import Character
from .map import Map
from .weapon import Weapon


class Game:

    def __init__(self, character_names: List[str]):

        self.id = datetime.datetime.now().strftime("%Y%m%d%H%M%S%f")
        self.__characters = [Character(name) for name in character_names]
        self.day: int = 0
        self.time: Literal["day", "night"] = "day"
        self.__announced_dead_characters: List[Character] = []
        self.public_messages: List[str] = []
        self.debug_messages: List[str] = []
        self.private_messages: Dict[str, List[str]] = {name: [] for name in character_names}
        self.map_ = Map(radius=TERRAIN_RADIUS)
        self.phase: Literal["move", "act"] = "move"

        # Fill the game field for every character
        for character in self.__characters:
            character.set_game(self)

        
    def get_alive_characters(self) -> List[Character]:
        return [character for character in self.__characters if character.alive]
    

    def get_dead_characters(self) -> List[Character]:
        """
        Get ALL dead characters, including those that have not been announced
        dead yet.
        """
        return [character for character in self.__characters if not character.alive]
    

    def get_all_characters(self) -> List[Character]:
        return self.__characters


    def save_message(
        self,
        message: str,
        channel: str,
        anti_channels: str = [],
        emphasis: bool = False,
        fmt: Dict[str, str] = {}
    ) -> None:
        
        # Load 'sentences.json'
        sentences = json.load(open("game/core/sentences.json", "r", encoding="utf8"))

        # Check if there is a key equal to the message. If so, return a random
        # sentence from the list of sentences
        if message in sentences:
            message = random.choice(sentences[message] + [message])

        # Format the message
        message = message.format(**fmt)

        # If emphasis, put newline before and after
        if emphasis:
            message = "\n" + message + "\n"

        # If the message is debug, send to the debug messages
        if channel == "debug":
            self.debug_messages.append(message)

        # If the message is public, send to the public messages
        if channel == "public":
            self.public_messages.append(message)

        # If the message is something else, check if the channel is the name
        # of a character, and store it if so
        if channel in [c.name for c in self.__characters]:
            self.private_messages[channel].append(message)


    def start_game(self):
        
        # Print the welcome message
        for channel in ["public", "debug"] + [c.name for c in self.__characters]:
            self.save_message(
                "🎉🎉 Welcome to the Hunger Games! 🎉🎉\n🎉🎉 {tributes} brave tributes stand ready, poised before the Cornucopia filled with weapons, where survival and strategy collide. 🎉🎉\n🎉🎉 In mere seconds, the Hunger Games will begin! 🎉🎉\n🎉🎉 May the odds be ever in your favor! 🎉🎉",
                fmt={"tributes": len(self.__characters)},
                channel=channel,
            )

    def get_state_of_game(self) -> Dict[str, str]:

        # Ask the character what they want to do now
        for character in self.__characters:
            if not character.alive:
                continue
            
            # If the character is the only one alive, announce the victory
            # instead of asking for an action
            if len(self.get_alive_characters()) == 1 and character.alive:
                self.save_message("🎉🎉 You have won the Hunger Games! 🎉🎉", channel=character.name, emphasis=True)
                self.save_message(
                    "🎉🎉 {character} has won the Hunger Games! 🎉🎉",
                    fmt={"character": character.name},
                    channel="public",
                    emphasis=True,
                    anti_channels=[character.name],
                )
                self.save_message(
                    "🎉🎉 {character} has won the Hunger Games! 🎉🎉",
                    fmt={"character": character.name},
                    channel="debug",
                    emphasis=True,
                )
                continue

            # If the day is 0, ask the character to choose between running
            # towards the cornucopia or running away from it
            if self.day == 0:
                self.save_message(
                    "{character}, do you want to risk going to the cornucopia, or to play it safe by running away from it? (run towards, run away)",
                    fmt={"character": character.name},
                    channel=character.name,
                    emphasis=True,
                )
            elif self.phase == "move":
                map_ = self.map_.draw(discovered_cells=character.visited_cells, current_position=character.position)
                self.save_message(
                    "{character}, you are currently at {coords}\n{map}\nWhere do you want to go? (go north, go south, go east, go west, stay)",
                    fmt={"character": character.name, "coords": coords(character.position), "map": map_},
                    channel=character.name,
                    emphasis=True)
            elif self.phase == "act":
                food = character.bag.food if character.bag.food > 0 else "no"
                water = character.bag.water if character.bag.water > 0 else "no"
                weapon = character.get_best_weapon() if len(character.bag.weapons) > 0 else Weapon(name="no weapon", damage=1)
                self.save_message(
                    "{character}, you have currently {food} food, {water} water, and are wielding {weapon}. What do you want to do? (hunt, gather, rest, hide)",
                    fmt={"character": character.name, "food": food, "water": water, "weapon": weapon.name},
                    channel=character.name,
                    emphasis=True,
                )

        # Build state
        state = {
            "game": {
                "id": self.id,
                "state": {
                    "day": self.day,
                    "time": self.time,
                    "phase": self.phase,
                    "alive_characters": [c.name for c in self.get_alive_characters()],
                    "dead_characters": [c.name for c in self.get_dead_characters()],
                },
                "messages": self.public_messages,
            },
            "characters": {
                c.name: {
                    "name": c.name,
                    "state": c.to_dict(),
                    "messages": self.private_messages[c.name]
                } for c in self.__characters
            },
            "debug": {
                "messages": self.debug_messages,
            }
        }

        # Reset messages
        self.public_messages = []
        self.debug_messages = []
        for name in self.private_messages:
            self.private_messages[name] = []

        # Return state
        return state


    def set_action(self, name: str, action: str):
        for character in self.__characters:
            if character.name == name:
                character.act(action)
                break


    def update_game(self):
        
        # Resolve the first turn
        if self.day == 0:
            # Show time (manually)
            for channel in ["public", "debug"] + [c.name for c in self.__characters]:
                self.save_message("🩸🩸 The bloodbath has begun", channel=channel, emphasis=True)

            # Resolve the first turn
            self.__resolve_first_turn()

            # Pass time manually
            self.day = 1

        # Resolve the mouvements
        elif self.phase == "move":

            # Show time
            self.__show_time_and_day()

            # Resolve movements
            self.__resolve_movements()

            # Update the game phase
            self.phase = "act"
        
        # Resolve the actions
        elif self.phase == "act":

            # Show time
            self.__show_time_and_day()
            
            if self.time == "night" and random_bool(EVENT_PROBABILITY):
                
                # Resolve hazard
                hazard_region = self.__get_lowest_hype_region()

                if hazard_region is not None:
                    characters_in_hazard_region = self.__get_characters_in_region(region=hazard_region)
                    characters_outside_hazard_region = [c for c in self.get_alive_characters() if c not in characters_in_hazard_region]
                    self.__resolve_actions(characters_subset=characters_outside_hazard_region)
                    self.__resolve_hazard(hazard_region=hazard_region)
                else:
                    self.__resolve_actions()

            else:

                # Resolve actions
                self.__resolve_actions()

            # Pass time
            self.__pass_time()

            # Update the game phase
            self.phase = "move"

        # Show random tip
        for channel in ["public"] + [c.name for c in self.__characters]:
            self.save_message(
                "📝📝 {tip}",
                fmt={"tip": random.choice(TIPS)},
                channel=channel,
                emphasis=True,
            )


    def __get_characters_in_cell(self, position: Tuple[int, int]) -> List[Character]:
        characters = [character for character in self.__characters if (character.position == position and character.alive)]
        random.shuffle(characters)
        return characters
    

    def __resolve_first_turn(self):
        """
        The first turn of the game will be resolved differently. Characters will
        have to choose between trying to get a weapon or running away from the
        cornucopia. All characters that chose to run towards it will eventually
        get a weapon, or be killed.
        """

        # Some characters are able to flee as planned
        fleeing_characters = [character for character in self.__characters if character.get_action() == "run away" and random_bool(FLEE_PROBABILITY)]
        random.shuffle(fleeing_characters)

        # Some characters will not be able to flee
        trapped_characters = [character for character in self.__characters if character.get_action() == "run away" and character not in fleeing_characters]
        random.shuffle(trapped_characters)

        # Some characters will fight
        fighting_characters = [character for character in self.__characters if character.get_action() == "run towards"]
        random.shuffle(fighting_characters)

        for character in fighting_characters:
            if not character.alive:
                continue

            # Give a weapon to the character
            weapon_tuple: tuple = random.choice(WEAPONS)
            weapon: Weapon = Weapon(name=weapon_tuple[0], damage=weapon_tuple[1])
            character.bag.add_weapon(weapon)
            self.save_message(
                "🔪➕ You found {weapon}",
                fmt={"weapon": weapon.name},
                channel=character.name,
            )
            self.save_message(
                "🔪➕ {character} found a weapon",
                fmt={"character": character.name},
                channel="public",
                anti_channels=[character.name],
            )
            self.save_message(
                "🔪➕ {character} found {weapon}",
                fmt={"character": character.name, "weapon": weapon.name},
                channel="debug",
            )

            # Make characters kill each other
            potential_victims = [other for other in self.__characters if other != character and other.alive and other.get_action() == "run towards"]
            if len(potential_victims) > 0:
                victim = random.choice(potential_victims)
                victim.alive = False
                victim.statistics["cause_of_death"] = "killed"
                self.save_message(
                    "🔪💀 You managed to slain {attacked}",
                    fmt={"attacked": victim.name},
                    channel=character.name,
                )
                self.save_message(
                    "🔪💀 You have been slained by {attacker}",
                    fmt={"attacker": character.name},
                    channel=victim.name,
                )
                self.save_message(
                    "🔪💀 {attacker} slained {attacked}",
                    fmt={"attacker": character.name, "attacked": victim.name},
                    channel="public",
                    anti_channels=[character.name, victim.name],
                )
                self.save_message(
                    "🔪💀 {attacker} slained {attacked}",
                    fmt={"attacker": character.name, "attacked": victim.name},
                    channel="debug",
                )
                for channel in [c.name for c in self.get_alive_characters() if c != victim]:
                    self.save_message("💀💀 A tribute has fallen", channel=channel)

                character.change_hype(HYPE_WHEN_KILLING)

        # Some characters that try to escape are hurt
        for attacked in trapped_characters:
            potential_attackers: List[Character] = [c for c in fighting_characters if c.alive]
            if len(potential_attackers) == 0:
                break
            attacker: Character = random.choice(potential_attackers)
            self.save_message(
                "🔪🤕 You have been hurt by {attacker} during your escape",
                fmt={"attacker": attacker.name},
                channel=attacked.name,
            )
            self.save_message(
                "🔪🤕 {attacked} was hurt during their escape",
                fmt={"attacked": attacked.name},
                channel="public",
                anti_channels=[attacked.name],
            )
            self.save_message(
                "🔪🤕 {attacker} hurt {attacked} during their escape",
                fmt={"attacker": attacker.name, "attacked": attacked.name},
                channel="debug",
            )
            attacker.attack(attacked)

        # All characters that try to escape are able to flee
        for character in fleeing_characters + trapped_characters:
            if not character.alive:
                continue
            self.save_message(
                "💨🌳 You fled far into the forest",
                channel=character.name,
            )
            self.save_message(
                "💨🌳 {character} fled far into the forest",
                fmt={"character": character.name},
                channel="public",
                anti_channels=[character.name],
            )
            self.save_message(
                "💨🌳 {character} fled far into the forest",
                fmt={"character": character.name},
                channel="debug",
            )
            character.move(random.choice(["go north", "go south", "go west", "go east"]))
        

    def __resolve_movements(self):
        """
        Every character moves according to their choice of action. When a character
        just moved on a cell, they are informed about the characters already on
        that cell, that didn't move.
        """
        moving_characters = [character for character in self.__characters if character.get_action() in ["go north", "go south", "go west", "go east"]]
        static_characters = [character for character in self.__characters if character.get_action() == "stay"]

        # Move the characters
        for character in moving_characters:
            if not character.alive:
                continue
            character.move(character.get_action())

        # Inform the characters about the static characters
        for character in moving_characters:
            current_position = character.position
            characters_in_same_cell = self.__get_characters_in_cell(current_position)
            static_characters_in_same_cell = [character for character in characters_in_same_cell if character in static_characters]
            if len(static_characters_in_same_cell) > 0:
                character.current_spotted_characters = len(static_characters_in_same_cell)
                self.save_message(
                    "👀👀 You spotted {characters} nearby",
                    fmt={"characters": smart_join([p.name for p in static_characters_in_same_cell], sep=", ", last_sep=" and ")},
                    channel=character.name,
                )
                self.save_message(
                    "👀👀 {character} spoted {characters} nearby",
                    fmt={"characters": smart_join([p.name for p in static_characters_in_same_cell], sep=", ", last_sep=" and "), "character": character.name},
                    channel="debug",
                )


    def __get_cells_in_region(self, region: Literal["north", "south", "east", "west"]) -> List[Tuple[int, int]]:
        
        # Get all cells
        all_cells: List[Tuple[int, int]] = list(itertools.product(range(-TERRAIN_RADIUS, TERRAIN_RADIUS + 1), repeat=2))

        # Filter cells based on region and return
        if region == "north":
            return [c for c in all_cells if c[1] > 0]
        elif region == "south":
            return [c for c in all_cells if c[1] < 0]
        elif region == "east":
            return [c for c in all_cells if c[0] < 0]
        elif region == "west":
            return [c for c in all_cells if c[0] > 0]
        else:
            raise ValueError("Region must be one of 'north', 'south', 'east', 'west'")


    def __get_characters_in_region(self, region: Literal["north", "south", "east", "west"]) -> List[Character]:

        # Get cells in region
        cells_in_region = self.__get_cells_in_region(region=region)

        # Filter characters based on cells and return
        characters_in_region = [
            c for c in self.__characters
            if c.alive and c.position in cells_in_region
        ]
        return characters_in_region


    def __get_lowest_hype_region(self) -> Literal["north", "south", "east", "west"] | None:
        
        # Define weight for each region
        region_weights: Dict[str, float] = {
            "north": 0,
            "south": 0,
            "east": 0,
            "west": 0,
        }

        for region in ["north", "south", "east", "west"]:

            # Get infos useful for later
            characters_in_region = self.__get_characters_in_region(region=region)
            total_characters_in_region = len(characters_in_region)
            sum_of_hypes = sum([c.hype for c in characters_in_region])

            # Never take a hazard zone were all characters are in
            if total_characters_in_region == len(self.get_alive_characters()):
                average_hype = sum_of_hypes / total_characters_in_region
                zone_weight = 0

            # Usual case
            elif total_characters_in_region > 0 and sum_of_hypes > 0:
                average_hype = sum_of_hypes / total_characters_in_region
                zone_weight = 1 / average_hype

            # If no hype, the weight is the number of characters in the zone (which is usually a low enough number for the weight to be very high)
            elif total_characters_in_region > 0:
                average_hype = sum_of_hypes / total_characters_in_region
                zone_weight = total_characters_in_region

            # If no character, set everything to 0
            else:
                average_hype = 0
                zone_weight = 0
                
            region_weights[region] = zone_weight
            self.save_message(
                "🔥🔥 Region {region} has {total_characters_in_hazard_zone} characters with an average hype of {average_hype:.2f} (weight = {zone_weight:.2f})",
                fmt={
                    "region": region,
                    "total_characters_in_hazard_zone": total_characters_in_region,
                    "average_hype": average_hype,
                    "zone_weight": zone_weight,
                },
                channel="debug",
            )
        
        # Abort if no valid hazard zone is found
        if sum(list(region_weights.values())) == 0:
            self.save_message(
                "🔥🔥 No valid hazard zone found",
                channel="debug",
            )
            return None
        
        # Return a random region based on the weights
        chosen_region = random.choices(
            list(region_weights.keys()),
            list(region_weights.values()),
        )[0]
        self.save_message(
            "🔥🔥 Chosen hazard zone: {chosen_region}",
            fmt={"chosen_region": chosen_region},
            channel="debug",
        )
        return chosen_region


    def __resolve_actions(self, characters_subset: List[Character] | None = None) -> None:
        """
        Once every character has chosen an action, the game will make them happen.
        Hunt actions are high priority and will be resolved first. Characters that
        are attacked will not be able to act.
        """

        cells = list(itertools.product(range(-TERRAIN_RADIUS, TERRAIN_RADIUS + 1), repeat=2))
        random.shuffle(cells)
        for x, y in cells:

            # Get all characters in the cell
            characters = self.__get_characters_in_cell((x, y))

            # If using a subset, filter the characters
            if characters_subset is not None:
                characters = [c for c in characters if c in characters_subset]

            # Define random battles, useful for later
            hunting_characters = [character for character in characters if character.get_action() == "hunt"]
            attacks: Dict[Character, Character] = {}
            for attacker in hunting_characters:
                    potential_victims = [c for c in characters if c != attacker and c.get_action() != "hide"]
                    if len(potential_victims) > 0:
                        attacked = random.choice(potential_victims)
                        attacks[attacker] = attacked
                    else:
                        self.save_message(
                            "🔪❌ You found nobody nearby",
                            channel=attacker.name,
                        )
                        self.save_message(
                            "🔪❌ {attacker} found no one to attack",
                            fmt={"attacker": attacker.name},
                            channel="debug",
                        )


            # Start with non hunting characters
            non_hunting_characters = [character for character in characters if character.get_action() != "hunt"]
            for character in non_hunting_characters:

                # Gather
                if character.get_action() == "gather":
                    character.gather()

                # Hide
                if character.get_action() == "hide":
                    character.hide()

                # Rest (if not attacked)
                if character.get_action() == "rest" and character not in attacks.values():
                    character.rest()

            # End with hunts: resolve attacks
            for attacker, attacked in attacks.items():

                # Check that both characters are still alive
                if attacker.alive and attacked.alive:

                    # Check for probability of success
                    success_proba = HUNT_SUCCESS_PROBABILITY
                    if self.time == "night":
                        success_proba *= NIGHT_PROBABILITY_FACTOR

                    # Attack if everything is fine
                    if random_bool(success_proba):
                        attacker.attack(attacked)

                    # If the attack failed
                    else:
                        self.save_message(
                            "🔪❌ You tried to attack {attacked}, but they escaped your assault",
                            fmt={"attacked": attacked.name},
                            channel=attacker.name,
                        )
                        self.save_message(
                            "🔪❌ {attacker} tried to attack you, but you barely escaped",
                            fmt={"attacker": attacker.name},
                            channel=attacked.name,
                        )
                        self.save_message(
                            "🔪❌ {attacker} tried to attack {attacked}, but they escaped",
                            fmt={"attacker": attacker.name, "attacked": attacked.name},
                            channel="debug",
                        )
                
                # If one of the characters is dead during the resolve, skip.
                # More precisely: if the attacked died (and thus if the
                # attacker is still alive), simply state that nobody was found.
                elif attacker.alive:
                    self.save_message(
                        "🔪❌ You found nobody nearby",
                        channel=attacker.name,
                    )
                    self.save_message(
                        "🔪❌ {attacker} wanted to attack {attacked}, but they died in the meantime",
                        fmt={"attacker": attacker.name, "attacked": attacked.name},
                        channel="debug",
                    )
                
                # If the attacker died, simply skip.
                else:
                    pass

            # If character had originally chosen to rest but was attacked, they
            # will not be able to rest
            for attacked in characters:
                if attacked.get_action() == "rest" and attacked in attacks.values() and attacked.alive:
                    self.save_message(
                        "🛌🔪 Because of the assault, you couldn't get a wink of sleep",
                        channel=attacked.name,
                    )
                    self.save_message(
                        "🛌🔪 {attacked} couldn't rest because of the assault",
                        fmt={"attacked": attacked.name},
                        channel="debug",
                    )
    
    
    def __resolve_hazard(self, hazard_region: Literal["north", "south", "east", "west"]) -> None:
        """
        During the game, events can happen. Approximately half of the terrain
        will be dangerous at night, and characters randomly move. The ones who
        do not move out of the dangerous zone will be killed. Note that the
        event will focus regions where tributes have the lowest average hype.
        """
        
        characters_in_hazard_region = self.__get_characters_in_region(region=hazard_region)

        for character in characters_in_hazard_region:
            self.save_message("🔥🔥 A deadly event is occuring", channel=character.name)
        self.save_message("🔥🔥 Deadly zone is occuring {hazard_region}", fmt={"hazard_region": hazard_region}, channel="debug")
        # TODO: put the following back
        # self.save_message(f"🔥🔥 {len(characters_in_hazard_zone)} trapped characters: {', '.join([c.name for c in total_characters_in_hazard_zone])}", channel="debug")

        # Each character moves in a random direction (TODO: the character can chose)
        for character in characters_in_hazard_region:
            potential_directions = []
            if character.position[0] > -TERRAIN_RADIUS:
                potential_directions.append("go west")
            if character.position[0] < TERRAIN_RADIUS:
                potential_directions.append("go east")
            if character.position[1] > -TERRAIN_RADIUS:
                potential_directions.append("go south")
            if character.position[1] < TERRAIN_RADIUS:
                potential_directions.append("go north")
            direction = random.choice(potential_directions)
            self.save_message(
                "🔥🔥 You tried fleeing to the {direction}",
                fmt={"direction": direction.replace("go ", "")},
                channel=character.name,
            )
            self.save_message(
                "🔥🔥 {character} tried fleeing to the {direction}",
                fmt={"character": character.name, "direction": direction.replace("go ", "")},
                channel="debug",
            )
            character.move(direction, silent=True)

        # Kill characters that are still in the hazard zone
        for character in characters_in_hazard_region:
            if character.position in self.__get_characters_in_region(hazard_region):
                character.alive = False
                character.statistics["cause_of_death"] = "hazard"
                self.save_message(
                    "💀🔥 You did not manage to escape the danger",
                    channel=character.name,
                )
                self.save_message(
                    "💀💀 {character} died",
                    fmt={"character": character.name},
                    channel="public",
                    anti_channels=[character.name]
                )
                self.save_message(
                    "💀🔥 {character} did not manage to escape the danger",
                    fmt={"character": character.name},
                    channel="debug"
                )
                for channel in [c.name for c in self.__characters if c != character]:
                    self.save_message(
                        "💀💀 A tribute has fallen",
                        channel=channel,
                    )
            else:
                if random_bool(1-EVENT_FLEE_PROBABILITY):
                    character.alive = False
                    character.statistics["cause_of_death"] = "hazard"
                    self.save_message(
                        "💀🔥 You stumbled trying to escape the danger",
                        channel=character.name,
                    )
                    self.save_message(
                        "💀💀 {character} died",
                        fmt={"character": character.name},
                        channel="public",
                        anti_channels=[character.name],
                    )
                    self.save_message(
                        "💀🔥 {character} stumbled trying to escape the danger",
                        fmt={"character": character.name},
                        channel="debug",
                    )
                else:
                    self.save_message(
                        "🔥✅ You barely escaped the hazard zone",
                        channel=character.name,
                    )
                    self.save_message(
                        "🔥✅ {character} barely escaped the hazard zone",
                        fmt={"character": character.name},
                        channel="debug",
                    )
    
    
    def __show_time_and_day(self) -> str:

        if self.phase == "move":
            prefix = "Start of "
        else:
            prefix = ""
        if self.time == "day":
            for channel in ["public", "debug"] + [c.name for c in self.__characters]:
                self.save_message(
                    "🌞🌞 {prefix}Day {day}",
                    fmt={"prefix": prefix, "day": self.day},
                    channel=channel,
                    emphasis=True,
                )
        else:
            for channel in ["public", "debug"] + [c.name for c in self.__characters]:
                self.save_message(
                    "🌙🌙 {prefix}Night {day}",
                    fmt={"prefix": prefix, "day": self.day},
                    channel=channel,
                    emphasis=True,
                )


    def __pass_time(self):
        """
        The game will advance time by one unit and make characters evolve.
        """
        # Save message of the time change
        if len(self.public_messages) == 1:
            self.save_message("All is calm... too calm...", channel="public")
        if self.time == "day":
            for channel in ["public", "debug"] + [c.name for c in self.__characters]:
                self.save_message("🌞🌙 The sun sets...", channel=channel, emphasis=True)
        else:
            for channel in ["public", "debug"] + [c.name for c in self.__characters]:
                self.save_message("🌙🌞 The sun rises...", channel=channel, emphasis=True)
            self.day += 1

        # Make characters evolve
        for character in self.get_alive_characters():
            character.evolve(self.time)

        if self.time == "day":
            self.time = "night"
        else:
            self.time = "day"

        # Announce deaths (only at end of day)
        if self.time == "night":
            new_deaths = [character for character in self.__characters if not character.alive and character not in self.__announced_dead_characters]
            for channel in ["public", "debug"] + [c.name for c in self.__characters]:
                if len(new_deaths) > 0:
                    self.save_message("💀🫡 The fallen:", channel=channel, emphasis=True)
                    for character in new_deaths:
                        self.save_message(
                            "- {character}",
                            fmt={"character": character.name},
                            channel=channel,
                        )
                        self.__announced_dead_characters.append(character)

            # Announce the remaining tributes
            for channel in ["public", "debug"] + [c.name for c in self.__characters]:
                if channel == "debug":
                    self.save_message("⚔️⚔️ The standing:", channel="debug", emphasis=True)
                    for character in self.get_alive_characters():
                        self.save_message(
                            "- {character}",
                            fmt={"character": character.name},
                            channel="debug",
                        )
                else:
                    self.save_message(
                        "⚔️⚔️ {number} tributes remain standing",
                        fmt={"number": len(self.get_alive_characters())},
                        channel=channel,
                        emphasis=True,
                    )
