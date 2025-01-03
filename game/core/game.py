from typing import List, Dict, Tuple, Literal
import datetime
import random
import itertools
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
        emphasis: bool = False
    ) -> None:

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
            self.save_message("🎉🎉 Welcome to the Hunger Games! 🎉🎉\n🎉🎉 {tributes} brave tributes stand ready, poised before the Cornucopia filled with weapons, where survival and strategy collide. 🎉🎉\n🎉🎉 In mere seconds, the Hunger Games will begin! 🎉🎉\n🎉🎉 May the odds be ever in your favor! 🎉🎉".format(tributes=len(self.__characters)), channel=channel)

    def get_state_of_game(self) -> Dict[str, str]:

        # Ask the character what they want to do now
        for character in self.__characters:
            if not character.alive:
                continue
            
            # If the character is the only one alive, announce the victory
            # instead of asking for an action
            if len(self.get_alive_characters()) == 1 and character.alive:
                self.save_message("🎉🎉 You have won the Hunger Games! 🎉🎉 ", channel=character.name, emphasis=True)
                self.save_message("🎉🎉 {character} has won the Hunger Games! 🎉🎉 ".format(character=character.name), channel="public", emphasis=True, anti_channels=[character.name])
                self.save_message("🎉🎉 {character} has won the Hunger Games! 🎉🎉 ".format(character=character.name), channel="debug", emphasis=True)
                continue

            # If the day is 0, ask the character to choose between running
            # towards the cornucopia or running away from it
            if self.day == 0:
                self.save_message("{character}, do you want to risk going to the cornucopia, or to play it safe by running away from it? (run towards, run away) ".format(character=character.name), channel=character.name, emphasis=True)
            elif self.phase == "move":
                map_ = self.map_.draw(discovered_cells=character.visited_cells, current_position=character.position)
                self.save_message("{character}, you are currently at {coords}\n{map}\nWhere do you want to go? (go north, go south, go east, go west, stay) ".format(character=character.name, coords=coords(character.position), map=self.map_.draw(discovered_cells=character.visited_cells, current_position=character.position)), channel=character.name, emphasis=True)
            elif self.phase == "act":
                food = character.bag.food if character.bag.food > 0 else "no"
                water = character.bag.water if character.bag.water > 0 else "no"
                weapon = character.get_best_weapon() if len(character.bag.weapons) > 0 else Weapon(name="no weapon", damage=1)
                self.save_message("{character}, you have currently {food} food, {water} water, and are wielding {weapon}. What do you want to do? (hunt, gather, rest, hide) ".format(character=character.name, food=food, water=water, weapon=weapon.name), channel=character.name, emphasis=True)

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
                self.save_message("🩸🩸 The bloodbath has begun ", channel=channel, emphasis=True)

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
                
                # Resolve random event
                status = self.__resolve_random_event()
                
                # If the event was aborted, resolve actions instead
                if status == "aborted":
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
            self.save_message("📝📝 {tip} ".format(tip=random.choice(TIPS)), channel=channel, emphasis=True)


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
            self.save_message("🔪➕ You found {weapon} ".format(weapon=weapon.name), channel=character.name)
            self.save_message("🔪➕ {character} found a weapon ".format(character=character.name), channel="public", anti_channels=[character.name])

            # Make characters kill each other
            potential_victims = [other for other in self.__characters if other != character and other.alive and other.get_action() == "run towards"]
            if len(potential_victims) > 0:
                victim = random.choice(potential_victims)
                victim.alive = False
                victim.statistics["cause_of_death"] = "killed"
                self.save_message("🔪💀 You managed to slain {attacked_character} ".format(attacked_character=victim.name), channel=character.name)
                self.save_message("🔪💀 You have been slained by {attacking_character} ".format(attacking_character=character.name), channel=victim.name)
                self.save_message("🔪💀 {attacking_character} slained {attacked_character}".format(attacking_character=character.name, attacked_character=victim.name), channel="public", anti_channels=[character.name, victim.name])
                self.save_message("🔪💀 {attacking_character} slained {attacked_character}".format(attacking_character=character.name, attacked_character=victim.name), channel="debug")
                for channel in [c.name for c in self.get_alive_characters() if c != victim]:
                    self.save_message("💀💀 A tribute has fallen", channel=channel)

                character.change_hype(HYPE_WHEN_KILLING)

        # Some characters that try to escape are hurt
        for character in trapped_characters:
            potential_attackers = [c for c in fighting_characters if c.alive]
            if len(potential_attackers) == 0:
                break
            attacker = random.choice(potential_attackers)
            self.save_message(f"🔪🤕 You have been hurt by {attacker} during your escape", channel=character.name)
            self.save_message(f"🔪🤕 {character.name} was hurt during their escape", channel="public", anti_channels=[character.name])
            self.save_message(f"🔪🤕 {attacker.name} hurt {character.name} during their escape", channel="debug")
            attacker.attack(character)

        # All characters that try to escape are able to flee
        for character in fleeing_characters + trapped_characters:
            if not character.alive:
                continue
            self.save_message(f"💨🌳 You fled far into the forest", channel=character.name)
            self.save_message(f"💨🌳 {character.name} fled far into the forest", channel="public", anti_channels=[character.name])
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
                self.save_message("👀👀 You spotted {characters} nearby".format(characters=smart_join([p.name for p in static_characters_in_same_cell], sep=", ", last_sep=" and ")), channel=character.name)
                self.save_message("👀👀 {character} spoted {characters} nearby".format(character=character.name, characters=smart_join([p.name for p in static_characters_in_same_cell], sep=", ", last_sep=" and ")), channel="debug")


    def __resolve_actions(self):
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

            # Define random battles, useful for later
            hunting_characters = [character for character in characters if character.get_action() == "hunt"]
            attacks: Dict[Character, Character] = {}
            for character in hunting_characters:
                    potential_victims = [c for c in characters if c != character and c.get_action() != "hide"]
                    if len(potential_victims) > 0:
                        attacked = random.choice(potential_victims)
                        attacks[character] = attacked
                    else:
                        self.save_message(f"🔪❌ You found nobody nearby", channel=character.name)
                        self.save_message(f"🔪❌ {character.name} found no one to attack", channel="debug")


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
                        self.save_message(f"🔪❌ You tried to attack {attacked.name}, but they escaped your assault", channel=attacker.name)
                        self.save_message(f"🔪❌ {attacker.name} tried to attack you, but you barely escaped", channel=attacked.name)
                        self.save_message(f"🔪❌ {attacker.name} tried to attack {attacked.name}, but they escaped", channel="debug")
                
                # If one of the characters is dead during the resolve, skip.
                # More precisely: if the attacked died (and thus if the
                # attacker is still alive), simply state that nobody was found.
                elif attacker.alive:
                    self.save_message(f"🔪❌ You found nobody nearby", channel=attacker.name)
                    self.save_message(f"🔪❌ {attacker.name} wanted to attack {attacked.name}, but they died in the meantime", channel="debug")
                
                # If the attacker died, simply skip.
                else:
                    pass

            # If character had originally chosen to rest but was attacked, they
            # will not be able to rest
            for character in characters:
                if character.get_action() == "rest" and character in attacks.values() and character.alive:
                    self.save_message(f"🛌🔪 Because of the assault, you couldn't get a wink of sleep", channel=character.name)
                    self.save_message(f"🛌🔪 {character.name} couldn't rest because of the assault", channel="debug")
    
    
    def __resolve_random_event(self) -> Literal["success", "aborted"]:
        """
        During the game, events can happen. Approximately half of the terrain
        will be dangerous at night, and characters randomly move. The ones who
        do not move out of the dangerous zone will be killed. Note that the
        event will focus regions where tributes have the lowest average hype.
        
        Returns a string indicating if the random event did indeed occur, or if
        it was aborted. If aborted, a normal turn should be performed.
        """
        # Get count of alive characters
        total_alive_characters: int = len(self.get_alive_characters())

        # Get all possible hazard zones
        all_cells: List[Tuple[int, int]] = list(itertools.product(range(-TERRAIN_RADIUS, TERRAIN_RADIUS + 1), repeat=2))
        cells_by_hazard_direction: Dict[str: List[Tuple[int, int]]] = {}
        cells_by_hazard_direction["north"] = [c for c in all_cells if c[1] > 0]
        cells_by_hazard_direction["south"] = [c for c in all_cells if c[1] < 0]
        cells_by_hazard_direction["east"] = [c for c in all_cells if c[0] < 0]
        cells_by_hazard_direction["west"] = [c for c in all_cells if c[0] > 0]
        
        hazard_zone_weights: Dict[str, float] = {}
        characters_in_hazard_zones: Dict[str, List[Character]] = {}
        for direction, cells in cells_by_hazard_direction.items():
            characters_in_hazard_zones[direction] = [
                c for c in self.__characters
                if c.alive and c.position in cells
            ]
            
            total_characters_in_hazard_zone = len(characters_in_hazard_zones[direction])
            sum_of_hypes = sum([c.hype for c in characters_in_hazard_zones[direction]])
            
            if total_characters_in_hazard_zone == total_alive_characters:
                # Never take a hazard zone were all characters are in
                average_hype = sum_of_hypes / total_characters_in_hazard_zone
                zone_weight = 0
            elif total_characters_in_hazard_zone > 0 and sum_of_hypes > 0:
                # Usual case
                average_hype = sum_of_hypes / total_characters_in_hazard_zone
                zone_weight = 1 / average_hype
            elif total_characters_in_hazard_zone > 0:
                # If no hype, the weight is the number of characters in the zone (which is usually a low enough number for the weight to be very high)
                average_hype = sum_of_hypes / total_characters_in_hazard_zone
                zone_weight = total_characters_in_hazard_zone
            else:
                # If no character, set everything to 0
                average_hype = 0
                zone_weight = 0
            hazard_zone_weights[direction] = zone_weight
            self.save_message(f"🔥🔥 Hazard zone {direction} has {total_characters_in_hazard_zone} characters with an average hype of {average_hype:.2f} (weight = {zone_weight:.2f})", channel="debug")
        
        # Abort if no valid hazard zone is found
        if sum(list(hazard_zone_weights.values())) == 0:
            return "aborted"
        
        # Define hazard zone
        hazard_zone = random.choices(
            list(hazard_zone_weights.keys()),
            list(hazard_zone_weights.values()),
        )[0]
        
        # Get all characters in the specific hazard zone
        characters_in_hazard_zone: List[Character] = characters_in_hazard_zones[hazard_zone]
        
        for character in characters_in_hazard_zone:
            self.save_message("🔥🔥 A deadly event is occuring", channel=character.name)
        self.save_message(f"🔥🔥 Deadly zone is occuring {hazard_zone}", channel="debug")
        # TODO: put the following back
        # self.save_message(f"🔥🔥 {len(characters_in_hazard_zone)} trapped characters: {', '.join([c.name for c in total_characters_in_hazard_zone])}", channel="debug")

        # Each character moves in a random direction (TODO: the character can chose)
        for character in characters_in_hazard_zone:
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
            self.save_message("🔥🔥 You tried fleeing to the {direction}".format(direction=direction.replace("go ", "")), channel=character.name)
            self.save_message("🔥🔥 {character} tried fleeing to the {direction}".format(character=character.name, direction=direction.replace("go ", "")), channel="debug")
            character.move(direction, silent=True)

        # Kill characters that are still in the hazard zone
        for character in characters_in_hazard_zone:
            if character.position in cells_by_hazard_direction[hazard_zone]:
                character.alive = False
                character.statistics["cause_of_death"] = "hazard"
                self.save_message(f"💀🔥 You did not manage to escape the danger", channel=character.name)
                self.save_message(f"💀💀 {character.name} died", channel="public", anti_channels=[character.name])
                self.save_message(f"💀🔥 {character.name} did not manage to escape the danger", channel="debug")
                for channel in [c.name for c in self.__characters if c != character]:
                    self.save_message(f"💀💀 A tribute has fallen", channel=channel)
            else:
                if random_bool(1-EVENT_FLEE_PROBABILITY):
                    character.alive = False
                    character.statistics["cause_of_death"] = "hazard"
                    self.save_message(f"💀🔥 You stumbled trying to escape the danger", channel=character.name)
                    self.save_message(f"💀💀 {character.name} died", channel="public", anti_channels=[character.name])
                    self.save_message(f"💀🔥 {character.name} stumbled trying to escape the danger.", channel="debug")
                else:
                    self.save_message(f"🔥✅ You barely escaped the hazard zone", channel=character.name)
                    self.save_message(f"🔥✅ {character.name} barely escaped the hazard zone", channel="debug")
    
    
    def __show_time_and_day(self) -> str:

        if self.phase == "move":
            prefix = "Start of "
        else:
            prefix = ""
        if self.time == "day":
            for channel in ["public", "debug"] + [c.name for c in self.__characters]:
                self.save_message("🌞🌞 {prefix}Day {day}".format(prefix=prefix, day=self.day), channel=channel, emphasis=True)
        else:
            for channel in ["public", "debug"] + [c.name for c in self.__characters]:
                self.save_message("🌙🌙 {prefix}Night {day}".format(prefix=prefix, day=self.day), channel=channel, emphasis=True)


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
                        self.save_message(f"- {character.name}", channel=channel)
                        self.__announced_dead_characters.append(character)

            # Announce the remaining tributes
            for channel in ["public", "debug"] + [c.name for c in self.__characters]:
                if channel == "debug":
                    self.save_message(f"⚔️⚔️ The standing:", channel="debug", emphasis=True)
                    for character in self.get_alive_characters():
                        self.save_message(f"- {character.name}", channel="debug")
                else:
                    self.save_message(f"⚔️⚔️ {len(self.get_alive_characters())} tributes remain standing", channel=channel, emphasis=True)
