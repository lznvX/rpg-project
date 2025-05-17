"""Lorem ipsum

Created on Tue May 13 21:47:27 2025
@author: widmo
"""


from typing import NamedTuple
from files import load_text_dir
from game_classes import Stats, Character, Inventory, Item
import test_items as ti


"""
name: str,
sprite_sheet: dict[str, str],
is_player: bool,
base_stats: Stats,
actions: tuple(UUID, Action),
initial_effects: dict
"""

PLAYER_SPRITE_DIR_PATH = r"assets\sprites\characters\player"


class DefaultStats(NamedTuple):
    """A collection of default stats for various character races."""

               #         MHP, MST, MMA, STR, AGI, ACU, ARM, RES
               # default: 20,  20,  20,  10,  10,  10,   2,   2

    human        = Stats( 20,  50,   0,  10,  10,  10,   2,   4)
    goblin       = Stats(  5,  20,   0,   2,  14,   0,   1,   2)
    hobgoblin    = Stats( 10,  25,   0,   6,  11,   1,   2,   2)
    goblin_chief = Stats( 20,  30,   5,  10,   8,   5,   4,   4)


def Player():
    char = Character.new(
        name            = "player",
        sprite_sheet    = load_text_dir(PLAYER_SPRITE_DIR_PATH),
        is_player       = True,
        base_stats      = DefaultStats.human,
        actions         = [],
        initial_effects = {}
        )
    char.inventory.add(ti.PotionHealth, 3)
    char.inventory.add(ti.Dagger)
    char.inventory.add(ti.Sword, 2)
    char = char.equip("mainhand", ti.Sword)
    char = char.equip("offhand", ti.Sword)
    return char


def Goblin():
    char = Character.new(
        name            = "goblin",
        sprite_sheet    = None,
        is_player       = False,
        base_stats      = DefaultStats.goblin,
        actions         = [],
        initial_effects = {}
        )
    char.inventory.add(ti.Dagger)
    char = char.equip("mainhand", ti.Dagger)
    return char


def Hobgoblin():
    char = Character.new(
        name            = "hobgoblin",
        sprite_sheet    = None,
        is_player       = False,
        base_stats      = DefaultStats.hobgoblin,
        actions         = [],
        initial_effects = {}
        )
    char.inventory.add(ti.Dagger, 2)
    char = char.equip("mainhand", ti.Dagger)
    char = char.equip("offhand", ti.Dagger)
    return char


def GoblinChief():
    char = Character.new(
        name            = "goblin_chieftain",
        sprite_sheet    = None,
        is_player       = False,
        base_stats      = DefaultStats.goblin_chief,
        actions         = [],
        initial_effects = {}
        )
    char.inventory.add(ti.Sword)
    char = char.equip("mainhand", ti.Sword)
    return char


def Bandit():
    char = Character.new(
        name            = "bandit",
        sprite_sheet    = None,
        is_player       = False,
        base_stats      = DefaultStats.human,
        actions         = [],
        initial_effects = {}
        )
    char.inventory.add(ti.Dagger)
    char = char.equip("mainhand", ti.Dagger)
    return char


if __name__ == "__main__":
    print(Goblin())
    print(Hobgoblin())
    print(GoblinChief())
