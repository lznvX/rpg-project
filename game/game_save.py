"""Game save management

Contributors:
    Adrien
    Romain
"""

from __future__ import annotations
import logging
from typing import NamedTuple
from game_classes import Character
import files as fi
import monsters

logger = logging.getLogger(__name__)

DEFAULT_ZONE_PATH = "assets\\zones\\test_zone.pkl"


class GameSave(NamedTuple):
    """Un fichier de sauvgarde"""
    character: Character
    zone_path: str
    player_grid_y: int
    player_grid_x: int

    @classmethod
    def new(cls, character: Character = monsters.player(),
            zone_path: str = DEFAULT_ZONE_PATH, player_grid_y: int = 3,
            player_grid_x: int = 5) -> GameSave:
        logger.debug("Creating new GameSave")

        return cls(
            character,
            zone_path,
            player_grid_y,
            player_grid_x,
        )

    def _test():
        """Execute a series of test to see if the program is working"""
        test_save1 = GameSave.new(player_grid_x = 5, player_grid_y = 10)
        test_save2 = GameSave.new(player_grid_x = 3, player_grid_y = 7)
        fi.save_pickle(test_save1, "user_data\\game_saves\\test")
        test_save2 = fi.load_pickle(("user_data\\game_saves\\test"))
        assert test_save2 == test_save1
        fi.delete("user_data\\game_saves\\test")
        assert "test" not in fi.os.listdir("user_data\\game_Saves")
        print("Save tests passed")


if __name__ == "__main__":
    GameSave._test()
