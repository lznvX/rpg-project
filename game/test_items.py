"""A list of test items

Created on 2025.04.09
Contributors:
    Adrien
    Jakub
"""


from common import Item, Action, Stats
from lang import get_lang_choice


text = get_lang_choice()


"""
name: str
description: str # will show up when inspecting the item (later)

tags: tuple[str]

weight: int # -> limit for storage, heavy armor slows you down, +relevant in combat

max_durability: int
durability: int # do we want durability?

stat_bonus: Stats # added to the user's stats
actions: tuple[Action] # added to the user's actions
uuid: UUID # used to keep track of applied bonuses
"""


light_stab = Action(text.light_stab_name, "attack", text.light_stab_desc, 1, "physical", {})
stab = Action(text.stab_name, "attack", text.stab_desc, 2, "physical", {})
slash = Action(text.slash_name, "attack", text.slash_desc, 3, "physical", {})


Sword = Item("Sword", "A pointy thing", ("equippable", "weapon", "mainhand", "offhand"), 3, 100, 100, Stats(), (stab, slash), "UUID")

StrHelmet = Item(
    "Helmet of Strength",
    "A spartan helmet, enchanted with a strength spell",
    ("equippable", "head"),
    2,
    100, 100,
    Stats(strength=5, armor=5),
    tuple(),
    "UUID")

AgiBoots = Item(
    "Hermes' Boots",
    "A pair of boots with suspicious wings",
    ("equippable", "feet"),
    2,
    100, 100,
    Stats(agility=5, armor=2),
    tuple(),
    "UUID")

PotionHealth = Item(
    "Potion of Healing",
    "Heals ♥ 5 when consumed",
    ("consumable", "potion"),
    1,
    1, 1,
    Stats(),
    tuple(),
    "UUID")
