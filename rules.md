# General remarks

This is a turn-based game. The last player alive wins. All the other should be forgotten by the history.

At each turn, players will have chose an action they will perform during the next time period.

The following actions can be chosen:
- **"hunt"**, where the character will look for other characters in the same region and attack them;
- **"gather"**, where the character will look for resources (water and food), but is more vulnerable to attacks;
- **"hide"**, where the character is imune to attacks;
- **"rest"**, where the character will regain some energy, but is extremely vulnerable to attacks.

# Statistics

Each character has the following statistics:
- **Health**: 10 max, and reaching 0 results in the character dying immediately;
- **Mental**: 3 max, and reaching 0 results in the character dying immediately;
- **Energy**: 3 max. Each night where the character does not rest, it decreases. Once it reaches 0, the mental decreases instead;
- **Hunger**: 5 max. Every food restores hunger completely, while every turn where the character does not eat reduces hunger by 1. Once it reaches 0, the character dies;
- **Thirst**: 3 max. Every water restores thirst completely, while every turn where the character does not eat reduces thirst by 1. Once it reaches ', the character dies;
- **Hype**: 100 max, starting with 0. Some actions reduce it and other increase it. Each round, you have a probability to earn a gift based on your current hype.

# First turn

During the first turn, the character will have special actions:
- **"run towards"** the cornucopia, where the character will try to take a weapon from the cornucopia: high risk, high reward;
- **"run away"** from the cornucopia, where the character will try to hide in the forest, taking less risks, but starting with no weapons.

# Damage calculation

Let `swDMG` be the damage of the strongest weapon the attacking character has. The real damage dealt `rDMG` is simply:
- `rDMG` = `swDMG` * 1, if the attacked player is also hunting
- `rDMG` = `swDMG` * 2, if the attacked player is gathering
- `rDMG` = `swDMG` * 4, if the attacked player is resting

# Details for nerds

- During the first turn, running towards grants a weapon with about a $50\%$ chance, and be immediately killed with a $50\%$ chance;
- During the first turn, running away will succeed with a $70\%$ chance, and be immediately attacked with a $30\%$ probability. The amount of damage taken depends on the weapon the attacker has found;
- Hunting will fail if no player is available in the region;
- Hunting will fail if the initial target has been killed by another player in the same turn;
- If all the conditions are met, hunting may still fail with a $100\%-70\%=30\%$ probability during day, and $100\%-70\%70\%=0.51\%$ during night;
- Gathering will allow the player to find between 1 and 3 resources, being water, food or both;
- Gathering will fail with a $100\%-90\%=10\%$ probability during day, and $100\%-90\%*70\%=0.37\%$ during night;
- Hiding and resting do always succeed;
- Hiding does in $10\%$ of the cases allow to gather 1-2 resources, which will be water, food or both;

# Hype

Here are the values:
- Hiding reduces hype by 30.
- Resting reduces hype by 20.
- Gathering reduces hype by 10.
- Being attacked increases hype by 10;
- Hunting increases hype by 20;
- Attacking successfully a player increases hype by 30;
- Killing a player increases hype by 50, as well as the hype of the killed player;

The gift sent by the sponsors is picked depending on what the character needs, namely:
- if the character has their thirst not full and has no water, the sponsor might send 3 units of water;
- if the character has their hunger not full and has no food, the sponsor might send 3 units of food;
- if the character has their health not full, the sponsor might send medecine that restore 3 health points (**This is the only way you can restore health!**);
- if the character has no weapon, the sponsor might send a random weapon; 
- If more than one condition is met, the sponsor will send one of the gifts at random.
- Receiving a gift successfully also restores one unit of mental (**This is the only way you can restore mental!**)
- If no condition is met, the drone sending the gift will unfortunately crash and the character will receive nothing.
