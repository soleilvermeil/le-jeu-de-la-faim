import random
import itertools
from typing import Tuple, Literal
from .constants import *
from .cell import Cell

class Map:

    def __init__(
        self,
        radius: int,
        which: Literal["forest", "jungle", "ruins", "colosseum"] | None = None,
    ) -> None:

        if which is None:
            which = random.choice(["forest", "jungle", "ruins", "colosseum"])

        cornucopia = Cell(
            "at|the cornucopia",
            icon="🌽",
            food_multiplier=0.5,
            water_multiplier=0.5,
            weapon_proba_multiplier=3,
            dangerous_weapon_proba=1,
            visibility_proba=1.0,
        )

        if which == "forest":

            cells = [
                Cell(
                    "in|a forest",
                    icon="🌳",
                ),
                Cell(
                    "at|a lake",
                    icon="💦",
                    water_multiplier=3,
                    visibility_proba=0.9,
                ),
                Cell(
                    "in|a dense rain forest",
                    icon="🌴",
                    water_multiplier=1.5,
                    visibility_proba=0.5,
                ),
                Cell(
                    "in|a dry forest",
                    icon="🌵",
                    food_multiplier=0.5,
                    water_multiplier=0.5,
                ),
            ]

        elif which == "jungle":
            cells = [
                Cell(
                    "in|a jungle",
                    icon="🌴",
                    water_multiplier=1.5,
                    food_multiplier=1.5,
                    visibility_proba=0.5,
                ),
                Cell(
                    "in|a lush jungle",
                    icon="🌿",
                    water_multiplier=2,
                    food_multiplier=3,
                    visibility_proba=0.5,
                ),
                Cell(
                    "at|a river",
                    icon="🌊",
                    water_multiplier=3,
                    visibility_proba=0.9,
                ),
            ]

        elif which == "colosseum":

            cells = [
                Cell(
                    "in|a dark corridor",
                    icon="🏰",
                    visibility_proba=0.3,
                    food_multiplier=0.1,
                    water_multiplier=0.1,
                ),
                Cell(
                    "in|a wide room",
                    icon="🏰",
                    visibility_proba=1.0,
                    food_multiplier=0.1,
                    water_multiplier=0.1,
                ),
            ]

        elif which == "ruins":

            cells = [
                Cell(
                    "in|a collapsed building",
                    icon="🏚️",
                    food_multiplier=0.2,
                    water_multiplier=0.5,
                    visibility_proba=0.5,
                    weapon_proba_multiplier=1.5,  # A higher chance of finding weapons due to exposed materials
                    dangerous_weapon_proba=0.5,   # A slight chance of finding a real weapon
                ),
                Cell(
                    "in|a ruined store",
                    icon="🏪",
                    food_multiplier=1.5,  # Stores might have some supplies left
                    water_multiplier=1.0,
                    visibility_proba=0.5,  # Sheltered locations decrease visibility
                    weapon_proba_multiplier=1.5,  # Higher chance of finding improvised weapons
                    dangerous_weapon_proba=0.5,  # Slight chance of finding a real weapon
                ),
            ]


        self.cells = {
            (x, y): random.choice(cells)
            for x, y in itertools.product(range(-radius, radius+1), range(-radius, radius+1)) if (x, y) != (0, 0)
        }
        self.cells[(0, 0)] = cornucopia





    def draw(self, discovered_cells, current_position: Tuple[int, int], inner_cell_width: int = 3) -> str:

        corner = ""
        v_edge = ""
        h_edge = ""

        # Top boundary
        result = (corner + h_edge * inner_cell_width) * (2 * TERRAIN_RADIUS + 1) + corner + "\n"

        for y in range(TERRAIN_RADIUS, -TERRAIN_RADIUS-1, -1):
            result += v_edge
            for x in range(-TERRAIN_RADIUS, TERRAIN_RADIUS+1):
                if (x, y) in discovered_cells and (x, y) != current_position:
                    icon = self.cells[(x, y)].icon
                elif (x, y) in discovered_cells and (x, y) == current_position:
                    icon = ">" + self.cells[(x, y)].icon + "<"
                else:
                    icon = "❓"
                result += f"{icon:^{inner_cell_width}}" + v_edge
            result += "\n"
            result += (corner + h_edge * inner_cell_width) * (2 * TERRAIN_RADIUS + 1) + corner + "\n"

        # Return
        return result[:-1]
