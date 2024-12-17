import random
import itertools
from typing import Tuple
from .constants import *
from .cell import Cell


class Map:
    def __init__(self, radius: int):
        lake = Cell("at|a lake", icon="💦", water_multiplier=3)
        rain_forest = Cell("in|a rain forest", icon="🌴", water_multiplier=2, food_multiplier=2)
        forest = Cell("in|a forest", icon="🌳")  # Baseline
        dry_forest = Cell("in|a dry forest", icon="🌵", water_multiplier=0)
        plain = Cell("on|a plain", icon="🌱", food_multiplier=0, water_multiplier=0)
        cornucopia = Cell("at|the cornucopia", icon="🌽", weapon_proba_multiplier=3, dangerous_weapon_proba=1)
        self.cells = {
            (x, y): random.choice([lake, rain_forest, forest, dry_forest, plain])
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