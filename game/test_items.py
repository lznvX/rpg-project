"""A list of test items

Created on 2025.04.09
Contributors:
    Adrien
    Jakub
"""

from game_classes import Item, Action, Stats, null_uuid


""" Item

 name: str        # Internal name; english only

 tags: tuple[str]
 #   weapon -> melee, bow, staff (magic), shield, etc.
 #   armor -> or separate tags for slots, i.e. helmet, armor, boots, etc.
 #   consumable (e.g. potions, arrows, etc.)
 #   material (sellable stuff? maybe crafting)
 #   currency (have gold as an item -> balance carrying items vs carrying money)

 weight: int # -> limit for storage, heavy armor slows you down, +relevant in combat

 stat_bonus: Stats # added to the user's stats
 actions: tuple[Action] # added to the user's actions
 uuid: UUID # used to keep track of applied bonuses
"""


light_stab = Action("light_stab",
    "attack",
    2, "physical",
    None)

stab = Action("stab",
    "attack",
    5, "physical",
    None)

slash = Action("slash",
    "attack",
    10, "physical",
    None)


Dagger = Item(
    "dagger",
    ("equippable", "weapon", "mainhand", "offhand"),
    5,
    Stats(),
    (light_stab,),
    null_uuid)

Sword = Item(
    "sword",
    ("equippable", "weapon", "mainhand", "offhand"),
    10,
    Stats(),
    (stab, slash),
    null_uuid)

StrHelmet = Item(
    "str_helmet",
    ("equippable", "head"),
    20,
    Stats(strength=5, armor=5),
    tuple(),
    null_uuid)

AgiBoots = Item(
    "agi_boots",
    ("equippable", "feet"),
    15,
    Stats(agility=5, armor=2),
    tuple(),
    null_uuid)

PotionHealth = Item(
    "potion_health",
    ("consumable", "potion"),
    4,
    Stats(),
    tuple(),
    null_uuid)
