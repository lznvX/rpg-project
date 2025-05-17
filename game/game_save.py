"""Game save management

Contributors:
    Adrien
    Romain
"""

from __future__ import annotations
import logging
from typing import NamedTuple
from game_classes import Character, Stats
import monsters

DEFAULT_ZONE_PATH = "assets\\zones\\test_zone.pkl"


class GameSave(NamedTuple):
    """Un fichier de sauvgarde"""
    character: Character
    zone_path: str
    player_grid_y: int
    player_grid_x: int
    
    @classmethod
    def new(cls, character: Character = monsters.Player(),
            zone_path: str = DEFAULT_ZONE_PATH, player_grid_y: int = 3,
            player_grid_x: int = 5) -> GameSave:
        logger.debug("Creating new GameSave")

        return cls(
            character,
            zone_path,
            player_grid_y,
            player_grid_x,
        )
        
#     def _test():
#         save1 = Save.new(worldPosition=("zone2.pkl", 5, 5))
#         save2 = Save.new(worldPosition=("zone1.pkl", 3, 7))
#         Save.save(None, save1,"save_1")
#         save2 = Save.load("save_1", "save_1")
#         assert save2 == save1
#         delete("save_1.pkl", "Saves\\Game_Saves")
#         print("Save tests passed")


logger = logging.getLogger(__name__)

# if __name__ == "__main__":
#     Save._test()
