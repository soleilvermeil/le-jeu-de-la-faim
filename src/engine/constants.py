MAX_HEALTH = 10
MAX_MENTAL = 2
MAX_ENERGY = 2
MAX_HUNGER = 10
MAX_THIRST = 5
MAX_HYPE = 100
TERRAIN_RADIUS = 1
HUNT_SUCCESS_PROBABILITY = 0.7
RESOURCE_GATHER_PROBA_WHILE_GATHERING = 0.9
MIN_RESOURCES_WHILE_GATHERING = 1
MAX_RESOURCES_WHILE_GATHERING = 3
RESOURCE_GATHER_PROBA_WHILE_HIDING = 0.1
MIN_RESOURCES_WHILE_HIDING = 1
MAX_RESOURCES_WHILE_HIDING = 2
WEAPONS = [
    ("a trident", 5),
    ("a bow", 5),
    ("an axe", 4),
    ("throwing knives", 3),
    ("a pickaxe", 3),
    ("a dagger", 3),
    ("a mace", 3),
    ("a scythe", 3),
    ("a sword", 4),
    ("a machete", 4),
    ("a spear", 3),
    ("a chain", 3),
]
NATURE_WEAPONS = [
    ("a rock", 2),
    ("a branch", 2),
    ("a stone", 2),
    ("a piece of wood", 2),
]
WEAPON_GATHER_PROBA_WHILE_GATHERING = 0.2
WEAPON_GATHER_PROBA_WHILE_HIDING = 0.2
FLEE_PROBABILITY = 0.7
NIGHT_PROBABILITY_FACTOR = 0.7
EVENT_FLEE_PROBABILITY = 0.8
EVENT_PROBABILITY = 0.5
HYPE_WHEN_KILLING = 30   # in previous version : 30
HYPE_WHEN_ATTACKING = 20 # in previous version : 20
HYPE_WHEN_HUNTING = 0   # in previous version : 10
HYPE_WHEN_ATTACKED = 20  # in previous version : 20
HYPE_WHEN_GATHERING = 0  # in previous version : 0
HYPE_WHEN_RESTING = -10  # in previous version : -10
HYPE_WHEN_HIDING = -30   # in previous version : -30
GIFT_FOOD = 1
GIFT_WATER = 1
GIFT_HEALTH = 3
TIPS = [
    # Real tips:
    "Resources are harder to find at night...",
    "Attacking players is harder at night, but being attacked is also less likely...",
    "Not sleeping at night is tiring...",
    "Medecine is the only way to recover health...",
    "Sponsors like action and love violence...",
    "You are vulnerable when you gather resources, and even more when you rest...",
    "Maybe you could find some resources while hiding...",
    "Everyone love receiving gifts...",
    "A single morsel of food is enough to fill you up...",
    "A single drop of water is enough to quench your thirst...",
    "Sponsor approval is a valuable advantage...",
    "Cornucopia is said to be full of weapons...",
    "If sponsors don't like you, gamemakers will hate you...",
    # Propaganda:
    "Remember, only the strong survive; the Games reward those who prove their worth!",
    "The Capitol gives you a chance to shine; don't waste it, or you'll fade into obscurity.",
    "Who will rise to be our next victor? Will it be you, or will you let others claim your destiny?",
    "Fame and fortune await those who dare to fight; make the Capitol proud!",
    "Don't forget, the Capitol feeds you, trains you, and lets you play your part in history.",
    "For the glory of the Capitol, may the odds forever be in your favor.",
    "Victory will bring rewards beyond your wildest dreams—failure will be your last breath.",
    "The Games are a celebration of loyalty and honor; prove your dedication to the Capitol.",
    "Every death is a message, every victory a triumph of the Capitol's might.",
    "Fight for your life, but never forget, the Capitol controls your fate.",
    "This is your moment; make the Capitol's watchers remember you forever.",
]
PERSONNALITIES = [
    ("ruthless/cold-blooded", "You are trained for combat, aggressive, have a lack of empathy for weaker tributes."),
    ("strategic/cunning", "You utilize intellect, deception, and charm rather than brute force."),
    ("noble/heroic", "You show compassion, loyalty, and have a desire to protect others, even at great risk."),
    ("terrified/timid", "You are fearful of confrontation, ill-prepared for the brutality of the arena."),
    ("manipulative/charismatic", "You are skilled in winning allies and sponsors, leveraging charm or emotional appeals."),
    ("unhinged/vengeful", "You are sometimes driven by anger, trauma, or defiance, leading to erratic but dangerous behavior.")
]
