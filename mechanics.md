


# Le Jeu de la Faim

## Core Game Mechanics

### Basic Information
- The game is a survival simulation where multiple tributes compete until only one remains
- The game alternates between day and night cycles
- Each turn has two phases: movement and action

### Character Stats
- Health (Max: 10) - Reduced by attacks, death at 0
- Mental (Max: 2) - Reduced by lack of sleep
- Energy (Max: 2) - Used for staying awake at night
- Hunger (Max: 10) - Must eat regularly
- Thirst (Max: 5) - Must drink regularly
- Hype (Max: 100) - Determines sponsor gift probability

### Map and Movement
- The arena is a square grid with the cornucopia at the center (0,0)
- Players can move one space per turn (north, south, east, west) or stay put
- Different terrain types affect resource gathering:
  - Forest (🌳) - Balanced resources
  - Lake (💦) - 3x water multiplier
  - Rain Forest (🌴) - 2x water multiplier
  - Dry Forest (🌵) - No food/water available
  - Cornucopia (🌽) - 3x weapon probability, guaranteed dangerous weapons

### Actions
1. Hunt - Attack other tributes
2. Gather - Collect resources
3. Rest - Recover energy
4. Hide - Stay safe with low chance of resources

### Resource Management
- Food and water are consumed each turn
- Running out of either results in death
- Resources can be obtained through:
  - Gathering (90% success rate, 1-3 resources)
  - Hiding (10% success rate, 1-2 resources)
  - Sponsor gifts (probability based on hype)

### Combat System
- Weapons have different damage values (1-5)
- Base hunt success rate: 70%
- Night reduces success rate by 30%
- Vulnerability multipliers:
  - Gathering: 2x damage
  - Resting: 4x damage
  - Running (first turn): 2x damage

### Hype System
Actions affect sponsor approval:
- Killing: +30 hype
- Attacking: +20 hype
- Being attacked: +20 hype
- Hunting: +10 hype
- Gathering: 0 hype
- Resting: -10 hype
- Hiding: -30 hype

## Strategic Implications

### Early Game (Cornucopia)
- High-risk, high-reward decision:
  - Running towards: 
    - Pros: Better weapons (3-5 damage)
    - Cons: High death risk
  - Running away:
    - Pros: Safety
    - Cons: Only basic weapons available (1-2 damage)

### Resource Management
- Critical thresholds:
  - Water lasts 5 turns max
  - Food lasts 10 turns max
  - Energy depletes at night unless resting
- Optimal gathering locations:
  - Lakes for water priority
  - Forests for balanced resources
  - Avoid dry forests

### Combat Strategy
- Best times to attack:
  - When opponents are gathering (2x damage)
  - When opponents are resting (4x damage)
  - During day (better success rate)
- Defensive considerations:
  - Hiding reduces resource gain but provides safety
  - Moving regularly prevents position reveal (occurs after 3 static turns)

### Sponsor Management
- High hype increases gift probability
- Gifts can provide:
  - Food (3 units)
  - Water (3 units)
  - Medicine (3 health)
  - Weapons (random dangerous weapon)
- Aggressive play maintains high hype
- Passive play reduces sponsor interest

### Night Strategy
- Important choices:
  - Rest to maintain energy/mental
  - Risk activities with 30% reduced success
- Random events more common at night
  - Half the map becomes dangerous
  - Affects areas with lower average hype

### Optimal Patterns
1. Maintain resource buffer
2. Rest during night when energy is low
3. Balance aggressive play for hype with survival needs
4. Stay mobile to avoid position reveal
5. Use terrain advantages for resource gathering
6. Monitor opponent patterns for optimal attack timing