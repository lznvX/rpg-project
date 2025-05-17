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


class Save(NamedTuple):
    """Un fichier de sauvgarde"""
    character : Character
    worldPosition : tuple[str, int, int] #le premier int représente l'axe y et le deuxième l'axe x
    
    @classmethod
    def new(cls, character: Character = monsters.Player(),
        worldPosition: tuple[str, int, int] = ("test_zone.pkl", 3, 3)
    ) -> Save:
        """Create a new Savefile"""
        logger.debug(f"the save {Save(character, worldPosition)} is created ")
        return Save(character, worldPosition)
        
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
