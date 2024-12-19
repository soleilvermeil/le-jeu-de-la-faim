from typing import TYPE_CHECKING, Dict, List, Literal, Tuple
from utils import *
from .constants import *
from .bag import Bag
from .weapon import Weapon


if TYPE_CHECKING:
    from game import Game


class Character:
    def __init__(self, name: str):
        self.name: str = name
        self.health: int = MAX_HEALTH
        self.mental: int = MAX_MENTAL
        self.energy: int = MAX_ENERGY
        self.hunger: int = MAX_HUNGER
        self.thirst: int = MAX_THIRST
        self.hype: int = 0
        self.position: Tuple[int] = (0, 0)
        self.__current_action: str = "none"
        self.current_spotted_characters: int = 0
        self.bag: Bag = Bag()
        self.alive: bool = True
        self.statistics: dict = {
            "kills": 0,
            "gifts_received": 0,
            "position_history": [self.position],
            "cause_of_death": "",
        }
        self.__game: "Game" = None
        self.visited_cells: List[Tuple[int]] = [(0, 0)]


    def set_game(self, game: "Game") -> None:
        self.__game = game

    
    def get_action(self) -> str:
        return self.__current_action


    def __repr__(self) -> str:
        return self.name
    

    def to_dict(self) -> Dict[str, str | int | float | bool]:
        """
        Returns a flat dictionary (i.e. all values are either strings,
        integers, floats or booleans) representing the character.
        """
        return {
            "alive": self.alive, # bool
            "health": self.health, # int
            "mental": self.mental, # int
            "energy": self.energy, # int
            "hunger": self.hunger, # int
            "thirst": self.thirst, # int
            "hype": self.hype, # int
            "current_action": self.__current_action, # str
            "current_spotted_characters": self.current_spotted_characters, # int
            "x": self.position[0], # int
            "y": self.position[1], # int
            "bag_food": self.bag.food, # int
            "bag_water": self.bag.water, # int
            "bag_best_weapon_name": self.get_best_weapon().name, # str
            "bag_best_weapon_damage": self.get_best_weapon().damage, # int
            "bag_weapons_count": len(self.bag.weapons), # int
            "stats_kills": self.statistics["kills"], # int
            "stats_gifts_received": self.statistics["gifts_received"], # int
            "stats_cause_of_death": self.statistics["cause_of_death"], # str
        }


    def show(self) -> str:
        """
        Returns a string representation of the character, often used to show
        the character's state to their character.
        """
        result = ""
        result += f"Name: {self.name}" + "\n"
        result += progress_bar(label="Health", value=self.health, max_value=MAX_HEALTH) + "\n"
        result += progress_bar(label="Mental", value=self.mental, max_value=MAX_MENTAL) + "\n"
        result += progress_bar(label="Energy", value=self.energy, max_value=MAX_ENERGY) + "\n"
        result += progress_bar(label="Hunger", value=self.hunger, max_value=MAX_HUNGER) + "\n"
        result += progress_bar(label="Thirst", value=self.thirst, max_value=MAX_THIRST) + "\n"
        result += progress_bar(label="Hype  ", value=self.hype  , max_value=MAX_HYPE  ) + "\n"
        result += self.bag.show() + "\n"
        return result[:-1]


    def move(self, direction: Literal["stay", "go north", "go south", "go west", "go east"]) -> None:

        # Move accordingly
        x, y = self.position
        if direction == "stay":
            pass
        elif direction == "go north" and y < TERRAIN_RADIUS:
            y += 1
        elif direction == "go south" and y > -TERRAIN_RADIUS:
            y -= 1
        elif direction == "go west" and x > -TERRAIN_RADIUS:
            x -= 1
        elif direction == "go east" and x < TERRAIN_RADIUS:
            x += 1
        else:
            pass
            # raise ValueError(f"Unknown direction: {direction}")
        if self.position != (x, y):
            biome = self.__game.map_.cells[(x, y)].name.replace("|", " ")
            icon = self.__game.map_.cells[(x, y)].icon
            self.__game.save_message("🚶{icon} {character} moved from {coords1} to {coords2}, and is now {biome}".format(icon=icon, character=self.name, coords1=coords(self.position), coords2=coords(x, y), biome=biome), channel="debug")
        self.position = (x, y)

        # Update the statistics
        self.statistics["position_history"].append(self.position)
        
        # If the visited cell is new, add it to the list
        if self.position not in self.visited_cells:
            self.visited_cells.append(self.position)
        
        # If the character was moving, inform them of the current cell
        if direction != "stay":
            cell = self.__game.map_.cells[self.position]
            self.__game.save_message("🚶{icon} You are now {biome}".format(icon=cell.icon, biome=cell.name.replace("|", " ")), channel=self.name)


    def act(self, action: str) -> None:

        # Check if the character's action is valid, and print a message to the
        # character's channel if it is
        if action == "hunt":
            self.__game.save_message("🔪🔪 You decided to hunt...", channel=self.name, emphasis=True)
            self.__game.save_message("🔪🔪 {character} decided to hunt...".format(character=self.name), channel="debug")
        elif action == "gather":
            self.__game.save_message("🌾🌾 You decided to gather resources...", channel=self.name, emphasis=True)
            self.__game.save_message("🌾🌾 {character} decided to gather resources...".format(character=self.name), channel="debug")
        elif action == "hide":
            self.__game.save_message("👻👻 You decided to hide...", channel=self.name, emphasis=True)
            self.__game.save_message("👻👻 {character} decided to hide...".format(character=self.name), channel="debug")
        elif action == "rest":
            self.__game.save_message("🛌🛌 You decided to rest...", channel=self.name, emphasis=True)
            self.__game.save_message("🛌🛌 {character} decided to rest...".format(character=self.name), channel="debug")
        elif action == "run away":
            self.__game.save_message("🔪🌲 You decided to run away from the cornucopia...", channel=self.name, emphasis=True)
            self.__game.save_message("🔪🌲 {character} decided to run away from the cornucopia...".format(character=self.name), channel="debug")
        elif action == "run towards":
            self.__game.save_message("🔪🩸 You decided to run towards the cornucopia...", channel=self.name, emphasis=True)
            self.__game.save_message("🔪🩸 {character} decided to run towards the cornucopia...".format(character=self.name), channel="debug")
        elif action == "go north":
            self.__game.save_message("🚶⬆️ You decided to go north...", channel=self.name, emphasis=True)
            self.__game.save_message("🚶⬆️ {character} decided to go north...".format(character=self.name), channel="debug")
        elif action == "go south":
            self.__game.save_message("🚶⬇️ You decided to go south...", channel=self.name, emphasis=True)
            self.__game.save_message("🚶⬇️ {character} decided to go south...".format(character=self.name), channel="debug")
        elif action == "go west":
            self.__game.save_message("🚶⬅️ You decided to go west...", channel=self.name, emphasis=True)
            self.__game.save_message("🚶⬅️ {character} decided to go west...".format(character=self.name), channel="debug")
        elif action == "go east":
            self.__game.save_message("🚶➡️ You decided to go east...", channel=self.name, emphasis=True)
            self.__game.save_message("🚶➡️ {character} decided to go east...".format(character=self.name), channel="debug")
        elif action == "stay":
            self.__game.save_message("🚶❎ You decided to stay...", channel=self.name, emphasis=True)
            self.__game.save_message("🚶❎ {character} decided to stay...".format(character=self.name), channel="debug")
        else:
            raise ValueError(f"Unknown action: {action}")
        
        # Update the character's action
        self.__current_action = action


    def get_best_weapon(self) -> Weapon:
        """
        Returns the best weapon in the character's bag. If the character has no
        weapon, returns a weapon called "bare hands" with a damage of 1.
        """
        if len(self.bag.weapons) == 0:
            return Weapon("bare hands", 1)
        else:
            return max(self.bag.weapons, key=lambda w: w.damage)
    

    def change_hype(self, value: int, show: bool = True) -> None:
        """
        Changes the hype of the character by the given value, and prints a
        message to the character's channel if the hype is high enough and
        `show` is True.
        """
        # If `show` is True, print a message to the character's channel
        if value / MAX_HYPE >= 0.3 and show:
            self.__game.save_message("🎉✅ Sponsors loved that", channel=self.name)
        if value / MAX_HYPE >= 0.2 and show:
            self.__game.save_message("🎉✅ Sponsors liked that", channel=self.name)
        elif value / MAX_HYPE >= 0.1 and show:
            self.__game.save_message("🎉✅ Sponsors appreciated that", channel=self.name)
        elif value / MAX_HYPE <= -0.3 and show:
            self.__game.save_message("🎉❌ Sponsors hated that", channel=self.name)
        elif value / MAX_HYPE <= -0.2 and show:
            self.__game.save_message("🎉❌ Sponsors disliked that", channel=self.name)
        elif value / MAX_HYPE <= -0.1 and show:
            self.__game.save_message("🎉❌ Sponsors were annoyed by that", channel=self.name)

        # Change the hype
        self.hype = min(max(0, self.hype + value), MAX_HYPE)

        # Print a debug message
        if value > 0:
            self.__game.save_message("f🎉✅ Hype for {character} increased by {hype}".format(character=self.name, hype=value), channel="debug")
        elif value < 0:
            self.__game.save_message("🎉❌ Hype for {character} decreased by {hype}".format(character=self.name, hype=abs(value)), channel="debug")


    def loot(self, dead_character: "Character") -> None:
        """
        Loot the body of a dead character. Note that this does NOT include the
        hype of the dead character.
        """
        # Print the looting messages to the stealing character's channel
        self.__game.save_message("💰💰 You have looted {attacked_character}'s body".format(attacked_character=dead_character.name), channel=self.name)
        self.__game.save_message("💰🍒 Received {food} food".format(food=dead_character.bag.food), channel=self.name)
        self.__game.save_message("💰💧 Received {water} water".format(water=dead_character.bag.water), channel=self.name)
        if len(dead_character.bag.weapons) > 0:
            self.__game.save_message("💰🔪 Received {weapons}".format(weapons=", ".join([w.name for w in dead_character.bag.weapons])), channel=self.name)

        # Print the looting messages to the debug channel
        self.__game.save_message("💰💰 {attacking_character} has looted {attacked_character}'s body".format(attacking_character=self.name, attacked_character=dead_character.name), channel="debug")
        self.__game.save_message("💰🍒 {attacking_character} has looted {food} food".format(attacking_character=self.name, food=dead_character.bag.food), channel="debug")
        self.__game.save_message("💰💧 {attacking_character} has looted {water} water".format(attacking_character=self.name, water=dead_character.bag.water), channel="debug")
        if len(dead_character.bag.weapons) > 0:
            self.__game.save_message("💰🔪 {attacking_character} has looted {weapons}".format(attacking_character=self.name, weapons=", ".join([w.name for w in dead_character.bag.weapons])), channel="debug")

        # Transfer the resources
        self.bag.steal(dead_character.bag)

    def __be_attacked(self, other: "Character") -> None:
        """
        Inflict damage to the character when they are attacked by another
        character. NOTE: This method should only be called by the `attack`
        method.
        """
        damage = other.get_best_weapon().damage
        if self.__current_action == "hunt":
            damage *= 1
        elif self.__current_action == "gather":
            damage *= 2
        elif self.__current_action == "rest":
            damage *= 4
        elif self.__current_action == "run away":  # Only during the first turn
            damage *= 2
        else:
            raise ValueError(f"Characters should not be able to be attacked while doing '{self.__current_action}'")
        self.health = max(self.health - damage, 0)
        self.__game.save_message("🔪🤕 {attacking_character} inflicted you {damage} damage ({current_health}/{max_health} HP left)".format(attacking_character=other.name, damage=damage, current_health=self.health, max_health=MAX_HEALTH), channel=self.name)
        self.__game.save_message("🔪🤕 You inflicted {damage} damage to {attacked_character}".format(attacked_character=self.name, damage=damage), channel=other.name)
        self.__game.save_message("🔪🤕 {attacked_character} took {damage} damage ({current_health}/{max_health} HP left)".format(attacked_character=self.name, damage=damage, current_health=self.health, max_health=MAX_HEALTH), channel="debug")

        # Check if dead
        if self.health <= 0:
            self.alive = False
            self.statistics["cause_of_death"] = "killed"
            self.__game.save_message("💀🔪 You have been killed", channel=self.name)
            self.__game.save_message("💀🔪 You killed {attacked_character}".format(attacked_character=self.name), channel=other.name)
            self.__game.save_message("💀🔪 {attacked_character} has been killed".format(attacked_character=self.name), channel="public", anti_channels=[self.name, other.name])
            self.__game.save_message("💀🔪 {attacked_character} has been killed by {attacking_character}".format(attacked_character=self.name, attacking_character=other.name), channel="debug")

        # If still alive, gain some hype
        else:
            self.change_hype(HYPE_WHEN_ATTACKED)

    def attack(self, other: "Character") -> None:
        """
        Attack another character.
        """
        # Print the attack messages to the corresponding channels
        self.__game.save_message("🔪😈 You have attacked {attacked_character} with {weapon}".format(attacked_character=other.name, weapon=self.get_best_weapon().name), channel=self.name)
        self.__game.save_message("🔪😈 You have been attacked by {attacking_character} with {weapon}".format(attacking_character=self.name, weapon=self.get_best_weapon().name), channel=other.name)
        self.__game.save_message("🔪😈 {attacking_character} attacked {attacked_character} with {weapon}".format(attacking_character=self.name, attacked_character=other.name, weapon=self.get_best_weapon().name), channel="debug")

        # Call the `__be_attacked` method of the other character
        other.__be_attacked(self)

        # Gain some hype for attacking
        hype_gain = HYPE_WHEN_ATTACKING

        # Check if the other character is dead
        if not other.alive:

            # Update statistics
            self.statistics["kills"] += 1

            # Get hype for the kill + the other character's hype
            hype_gain += HYPE_WHEN_KILLING + other.hype
            
            # Loot the body
            self.loot(other)

        # Transfer the hype
        self.change_hype(hype_gain)


    def gather(self) -> None:
        """
        Gather resources. The character may find food, water, and weapons.
        The probability of finding resources is lower at night.
        """
        # Compute the success rate
        success_proba = RESOURCE_GATHER_PROBA_WHILE_GATHERING
        if self.__game.time == "night":
            success_proba *= NIGHT_PROBABILITY_FACTOR

        # If the character succeeded to gather
        if random_bool(success_proba):

            # If the character found resources (and thus not a weapon)
            if not random_bool(WEAPON_GATHER_PROBA_WHILE_GATHERING * self.__game.map_.cells[self.position].weapon_proba_multiplier):
                resources = random.randint(MIN_RESOURCES_WHILE_GATHERING, MAX_RESOURCES_WHILE_GATHERING)
                food = random.randint(0, resources)
                water = resources - food
                food *= self.__game.map_.cells[self.position].food_multiplier
                water *= self.__game.map_.cells[self.position].water_multiplier
                self.bag.food += food
                self.bag.water += water
                if food > 0 and water > 0:
                    self.__game.save_message("🌾✅ You found some food and water", channel=self.name)
                elif food > 0 and water == 0:
                    self.__game.save_message("🌾✅ You found some food", channel=self.name)
                elif food == 0 and water > 0:
                    self.__game.save_message("🌾✅ You found some water", channel=self.name)
                self.__game.save_message("🌾✅ {character} gathered {food} food and {water} water".format(character=self.name, food=food, water=water), channel="debug")

            # If a weapon is found instead
            else:

                # Check if the weapon is dangerous or not
                if random_bool(self.__game.map_.cells[self.position].dangerous_weapon_proba):
                    weapon_tuple: tuple = random.choice(WEAPONS)
                else:
                    weapon_tuple: tuple = random.choice(NATURE_WEAPONS)
                weapon = Weapon(name=weapon_tuple[0], damage=weapon_tuple[1])
                self.bag.add_weapon(weapon)
                self.__game.save_message("🌾🔪 You found {weapon}".format(weapon=weapon.name), channel=self.name)
                self.__game.save_message("🌾🔪 {character} found {weapon}".format(character=self.name, weapon=weapon.name), channel="debug")

        # If the character failed to gather
        else:
            self.__game.save_message("🌾❌ You failed to gather", channel=self.name)
            self.__game.save_message("🌾❌ {character} failed to gather".format(character=self.name), channel="debug")

        # Change the hype
        self.change_hype(HYPE_WHEN_GATHERING)


    def hide(self):
        """
        Hide. The character may find food, water, and weapons, but with
        usually very low probabilities. The character is not impacted by the
        time of day.
        """

        # If the character found resources of any kind
        if random_bool(RESOURCE_GATHER_PROBA_WHILE_HIDING):

            # If the character found resources (and thus not a weapon)
            if not random_bool(WEAPON_GATHER_PROBA_WHILE_HIDING  * self.__game.map_.cells[self.position].weapon_proba_multiplier):
                resources = random.randint(MIN_RESOURCES_WHILE_HIDING, MAX_RESOURCES_WHILE_HIDING)
                food = random.randint(0, resources)
                water = resources - food
                food *= self.__game.map_.cells[self.position].food_multiplier
                water *= self.__game.map_.cells[self.position].water_multiplier
                if food > 0 and water > 0:
                    self.__game.save_message("👻🍒 You found some food while hiding ", channel=self.name)
                elif food > 0 and water == 0:
                    self.__game.save_message("👻💧 You found some water while hiding ", channel=self.name)
                elif food == 0 and water > 0:
                    self.__game.save_message("👻🌾 You found some food and water while hiding ", channel=self.name)
                self.__game.save_message("👻✅ {character} found {food} food and {water} water while hiding ".format(character=self.name, food=food, water=water), channel="debug")

            # If a weapon is found instead
            else:
                weapon_tuple: tuple = random.choice(NATURE_WEAPONS)
                weapon: Weapon = Weapon(name=weapon_tuple[0], damage=weapon_tuple[1])
                self.bag.add_weapon(weapon)
                self.__game.save_message("👻🔪 You found {weapon} while hiding ".format(weapon=weapon.name), channel=self.name)
                self.__game.save_message("👻🔪 {character} found {weapon} while hiding ".format(character=self.name, weapon=weapon.name), channel="debug")

        # If the character found nothing
        else:
            self.__game.save_message("👻❌ {character} didn't find anything while hiding ".format(character=self.name), channel="debug")
        
        # Change the hype
        self.change_hype(HYPE_WHEN_HIDING)


    def rest(self) -> None:
        """
        Rest. The character regains some energy. NOTE: this method should only
        be called if the character is not attacked during the resolve.
        """
        # Add energy
        self.energy = min(self.energy + 1, MAX_ENERGY)

        # Change the hype
        self.change_hype(HYPE_WHEN_RESTING)


    def evolve(self, time: Literal["day", "night"]) -> None:

        # Hype: Each turn, a character might receive a gift if their hype is high enough
        if random_bool(self.hype / MAX_HYPE):
            self.__game.save_message("🎁🎉 An unknown sponsor sent a gift to {character} ".format(character=self.name), channel="public")
            self.__game.save_message("🎁🎉 An unknown sponsor sent a gift to {character} (proba = {proba}) ".format(character=self.name, proba=f"{self.hype / MAX_HYPE:.0%}"), channel="debug")
            potential_gift = []
            if self.bag.water == 0 and self.hunger < MAX_THIRST:
                potential_gift.append("water")
            if self.bag.food == 0 and self.thirst < MAX_HUNGER:
                potential_gift.append("food")
            if self.health < MAX_HEALTH:
                potential_gift.append("medecine")
            if len(self.bag.weapons) == 0:
                potential_gift.append("weapon")

            # If the fullfills at least one gift condition
            if len(potential_gift) > 0:

                # Choose a gift
                gift = random.choice(potential_gift)
                if gift == "water":
                    water = 3
                    self.bag.water += water
                    self.__game.save_message("🎁💧 You received some water from an unknown sponsor ", channel=self.name)
                    self.__game.save_message("🎁💧 {character} received {water} water from an unknown sponsor ".format(character=self.name, water=water), channel="debug")
                if gift == "food":
                    food = 3
                    self.bag.food += food
                    self.__game.save_message("🎁🍒 You received some food from an unknown sponsor ", channel=self.name)
                    self.__game.save_message("🎁🍒 {character} received {food} food from an unknown sponsor ".format(character=self.name, food=food), channel="debug")
                if gift == "medecine":
                    delta_health = 3
                    self.health = min(self.health + delta_health, MAX_HEALTH)
                    self.__game.save_message("🎁💊 You received some medecine from an unknown sponsor ", channel=self.name)
                    self.__game.save_message("🎁💊 {character}'s health was restored by {health} thanks to an unknown sponsor ".format(character=self.name, health=delta_health), channel="debug")
                if gift == "weapon":
                    weapon_tuple: tuple = random.choice(WEAPONS)
                    weapon: Weapon = Weapon(name=weapon_tuple[0], damage=weapon_tuple[1])
                    self.bag.add_weapon(weapon)
                    self.__game.save_message("🎁🔪 You received {weapon} from an unknown sponsor ".format(weapon=weapon.name), channel=self.name)
                    self.__game.save_message("🎁🔪 {character} received {weapon} from an unknown sponsor ".format(character=self.name, weapon=weapon.name), channel="debug")

                # The gift also restores some mental
                if self.mental < MAX_MENTAL:
                    self.mental += 1
                    self.__game.save_message("🎁❤️‍🩹 The gift made you feel a bit happier ", channel=self.name)
                    self.__game.save_message("🎁❤️‍🩹 {character} feels a bit happier thanks to the gift".format(character=self.name), channel="debug")

                # Update statistics
                self.statistics["gifts_received"] += 1

            # If the character has no need for a gift, the drone crashes
            else:
                self.__game.save_message("🎁❌ The drone sending your gift crashed in a tree and has been destroyed ", channel=self.name)
                self.__game.save_message("🎁❌ The gift for {character} could not be delivered ".format(character=self.name), channel="debug")

            # Lower the hype
            self.hype = MAX_HYPE // 2

        # If the character is the last one alive, skip the evolution to avoid
        # having no winner at all. TODO: this is a temporary fix, because the
        # actor playing this character might wonder why their character does
        # not die, for example if they were starving previous turn.
        alive_characters = [c for c in self.__game.get_alive_characters()]
        if len(alive_characters) == 1:
            return
        
        # Thirst
        if self.bag.water >= 1:
            self.bag.water -= 1
            self.thirst = MAX_THIRST
            self.__game.save_message("💧✅ You drinked some water ", channel=self.name)
            self.__game.save_message("💧✅ {character} drinks water ({water} left) ".format(character=self.name, water=self.bag.water), channel="debug")
        elif self.thirst > MAX_THIRST // 2:
            self.thirst -= 1
            self.__game.save_message("💧❌ You are slightly thirsty ", channel=self.name)
            self.__game.save_message("💧❌ {character} is thirsty and will die in {turns} turns ".format(character=self.name, turns=self.thirst+1), channel="debug")
        elif self.thirst > 1:
            self.thirst -= 1
            self.__game.save_message("💧❌ You are thirsty ", channel=self.name)
            self.__game.save_message("💧❌ {character} is thirsty and will die in {turns} turns ".format(character=self.name, turns=self.thirst+1), channel="debug")
        elif self.thirst == 1:
            self.thirst -= 1
            self.__game.save_message("💧❌ You are deshydrated and will die next turn if you don't manage to find water ", channel=self.name)
            self.__game.save_message("💧❌ {character} is deshydrated and will die next turn ".format(character=self.name), channel="debug")
        else:
            self.alive = False
            self.statistics["cause_of_death"] = "thirst"
            self.__game.save_message("💀💧 You died of thirst ", channel=self.name)
            self.__game.save_message("💀💧 {character} died of thirst ".format(character=self.name), channel="public", anti_channels=self.name)
            self.__game.save_message("💀💧 {character} died of thirst ".format(character=self.name), channel="debug")
            return

        # Hunger
        if self.bag.food >= 1:
            self.bag.food -= 1
            self.hunger = MAX_HUNGER
            self.__game.save_message("🍒✅ You ate some food ", channel=self.name)
            self.__game.save_message("🍒✅ {character} ate food ({food} left) ".format(character=self.name, food=self.bag.food), channel="debug")
        elif self.hunger > MAX_HUNGER // 2:
            self.hunger -= 1
            self.__game.save_message("🍒❌ You are slightly hungry ", channel=self.name)
            self.__game.save_message("🍒❌ {character} is hungry and will die in {turns} turns ".format(character=self.name, turns=self.hunger+1), channel="debug")
        elif self.hunger > 1:
            self.hunger -= 1
            self.__game.save_message("🍒❌ You are hungry", channel=self.name)
            self.__game.save_message("🍒❌ {character} is hungry and will die in {turns} turns ".format(character=self.name, turns=self.hunger+1), channel="debug")
        elif self.hunger == 1:
            self.hunger -= 1
            self.__game.save_message("🍒❌ You are starving and will die next turn if you don't manage to find food ", channel=self.name)
            self.__game.save_message("🍒❌ {character} is starving and will die next turn ".format(character=self.name), channel="debug")
        else:
            self.alive = False
            self.statistics["cause_of_death"] = "hunger"
            self.__game.save_message("💀🍒 You died of hunger ", channel=self.name)
            self.__game.save_message("💀🍒 {character} died of hunger ".format(character=self.name), channel="public", anti_channels=[self.name])
            self.__game.save_message("💀🍒 {character} died of hunger ".format(character=self.name), channel="debug")
            return
        
        # Energy: if a character does not rest during the night, they will lose
        # 1 energy. If they have no energy, they will lose mental health
        # instead. During the day, energy does not change. 
        if time == "night":
            if self.__current_action == "rest":
                self.__game.save_message("🛌✅ You have regained some energy ", channel=self.name)
                self.__game.save_message("🛌✅ {character} has regained 1 energy ".format(character=self.name), channel="debug")
            else:
                if self.energy > 1:
                    self.energy -= 1
                    self.__game.save_message("🛌❌ You are tired ", channel=self.name)
                    self.__game.save_message("🛌❌ {character} is tired ({energy} energy left) ".format(character=self.name, energy=self.energy), channel="debug")
                elif self.energy == 1:
                    self.energy -= 1
                    self.__game.save_message("🛌❌ You are exhausted ", channel=self.name)
                    self.__game.save_message("🛌❌ {character} is exhausted ({energy} energy left) ".format(character=self.name, energy=self.energy), channel="debug")
                elif self.mental > 1:
                    self.mental -= 1
                    self.__game.save_message("🛌❌ Your lack of sleep is driving you insane, and you should rest within {turns} turns ".format(turns=self.mental+1), channel=self.name)
                    self.__game.save_message("🛌❌ {character}'s lack of sleep is driving them insane ({turns} turns before dying) ".format(character=self.name, turns=self.mental+1), channel="debug")
                elif  self.mental == 1:
                    self.mental -= 1
                    self.__game.save_message("🛌❌ Your lack of sleep is driving you insane, and you should rest immediately ", channel=self.name)
                    self.__game.save_message("🛌❌ {character}'s lack of sleep is driving them insane (last turns before dying) ".format(character=self.name), channel="debug")
                else:
                    self.alive = False
                    self.statistics["cause_of_death"] = "madness"
                    self.__game.save_message("💀🧠 You killed yourself", channel=self.name)
                    self.__game.save_message("💀🧠 {character} killed themself".format(character=self.name), channel="public", anti_channels=[self.name])
                    self.__game.save_message("💀🧠 {character} killed themself".format(character=self.name), channel="debug")
                    return
                
        # If a character has not moved for 3 turns, their position is revealed
        if len(self.statistics["position_history"]) > 3 and TERRAIN_RADIUS > 0:
            p_1 = self.statistics["position_history"][-1]
            p_2 = self.statistics["position_history"][-2]
            p_3 = self.statistics["position_history"][-3]
            if p_1 == p_2 == p_3:
                self.__game.save_message("👀👀 {character} has been spotted at {coords} ".format(character=self.name, coords=coords(p_1)), channel="public")
                self.__game.save_message("👀👀 {character} has been spotted at {coords} ".format(character=self.name, coords=coords(p_1)), channel="debug")

        # If a character has no health, they die (this should not happen)
        if self.health == 0 and self.alive:
            self.alive = False
            self.statistics["cause_of_death"] = "health"
            self.__game.save_message("💀💀 You died ", channel=self.name)
            self.__game.save_message("💀💀 {character} died ".format(character=self.name), channel="public", anti_channels=[self.name])
            self.__game.save_message("💀💀 {character} died for unknown reasons ".format(character=self.name), channel="debug")
            return

        # Clears the number of spotted characters
        self.current_spotted_characters = 0

        # Reset action (should be performed last) 
        self.__current_action = "none"
