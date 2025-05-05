"""Classes and functions shared between several systems

Created on 2025.03.20
Contributors:
    Jakub
    Adrien
    Romain
"""


from __future__ import annotations
from collections import Counter
import logging
import os
import pickle
from typing import NamedTuple
from uuid import UUID, uuid4
from lang import get_lang_choice, f

text = get_lang_choice()


class DamageInstance(NamedTuple):
    """Holds information about a single instance of damage.

    Created as a result of an attack or other interaction. Should be passed to
    the target of the attack/interaction.
    """
    damage: float
    damage_type: str
    effects: dict


class Stats(NamedTuple):
    """Stores the stats of a charcter.

    Use more than one instance per character to differentiate base and current
    stats.
    """
    max_health: int = None   # if it drops to 0, you die
    max_stamina: int = None  # used as a resource for performing PHYSICAL actions
    max_mana: int = None     # used as a resource for performing MAGICAL actions

    strength: int = None     # increases damage of PHYSICAL attacks
    agility: int = None      # determines turn order, flee chance, damage of some attacks
    acumen: int = None       # determines damage of MAGICAL attacks

    armor: int = None                # decreases PHYSICAL damage taken
    magical_resistance: int = None   # decreases MAGICAL damage taken


    def modify(self, changes: Stats) -> Stats:
        """Generate new stat sheet based on an existing one.

        Changes are represented as another stat sheet. A value of None (default
        value for all stats) results in no change, allowing for modification
        of 1, some, or all stats at the same time.
        """
        new_stats = []
        for old, new in zip(self, changes):
            if new is None:
                new_stats.append(old)
            else:
                new_stats.append(new)
        return Stats(*new_stats)


class Action(NamedTuple):
    """Describes an action during combat."""

    name: str           # Internal name; english only
    action_type: str    #

    base_damage: int    # How much damage is dealt by the action
    damage_type: str    # What type is the damage
                        # different damage types will result in different
                        # final damage, based on target's resistances
    effects: dict       # Effects to be applied to the target


    @property
    def display_name(self) -> str:
        """Fetch the action's name in the appropriate language."""
        try:
            return text.action_names[self.name]
        except KeyError:
            return self.name


    @property
    def description(self) -> str:
        """Fetch the action's description in the appropriate language."""
        # will show up when inspecting the action (later)
        try:
            return text.action_descriptions[self.name]
        except:
            return ""


    def get_damage(self) -> float:
        return self.base_damage


    def create_damage_instance(self) -> DamageInstance:
        return DamageInstance(self.damage(), self.damage_type, self.effects)


    def __repr__(self):
        return f"{self.display_name} (¤ {self.get_damage()})"


class Item(NamedTuple):
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


    @property
    def display_name(self) -> str:
        """Fetch the item's name in the appropriate language."""
        try:
            return text.item_names[self.name]
        except KeyError:
            return self.name


    @property
    def description(self) -> str:
        """Fetch the item's description in the appropriate language."""
        # will show up when inspecting the item (later)
        try:
            return text.item_descriptions[self.name]
        except KeyError:
            return ""


    def __repr__(self):
        return f"{self.display_name}"


class Inventory(NamedTuple):
    """The inventory of a character.

    Not necessarily the player.
    """
    equipment: dict[str: Item]
    backpack: Counter[Item: int]
    slots = ("mainhand", "offhand", "head", "body", "feet")


    @classmethod
    def new(self) -> Inventory:
        """Create a new empty inventory."""
        equipment = dict()
        for slot in self.slots:
            equipment[slot] = None

        return Inventory(equipment, Counter())


    def equip(self, slot: str, item: Item):
        """Equip an item from the backpack in the given slot.

        Supports hot-swapping.
        """
        if not "equippable" in item.tags:
            raise ValueError(f"Item {item} not equippable")
        if not slot in self.slots:
            raise ValueError(f"Slot {slot} does not exist")

        if self.equipment[slot] is not None:
            # slot already occupied
            self.unequip(slot)

        self.remove(item)
        self.equipment[slot] = item


    def unequip(self, slot: str):
        """Remove an item from the given slot and add it back to the backpack."""
        if not slot in self.slots:
            raise ValueError(f"Slot {slot} does not exist")
        if self.equipment[slot] is None:
            raise ValueError(f"Slot {slot} is empty")

        item = self.equipment[slot]
        self.equipment[slot] = None
        self.add(item)


    def add(self, item: Item, count: int=1):
        """Add an item to the backpack."""
        assert count >= 0

        self.backpack[item] += count


    def remove(self, item: Item, count: int=1):
        """Remove an item from the backpack."""
        assert count >= 0

        if self.backpack[item] < count:
            raise ValueError(f"Inventory does not contain enough {item} to remove {count}")
        else:
            self.backpack[item] -= count


    def use(self, item: Item):
        """Use an item from the backpack.

        The item is consumed.
        """
        if self.backpack[item] > 0:
            self.remove(item)
            #TODO: implement item using
        else:
            raise ValueError(f"Inventory does not contain any {item}")


    @staticmethod
    def _test():
        item1 = Item("item1", ("item", "equippable"), 1,  Stats(), tuple(), "UUID")
        item2 = Item("item2", ("item",), 1, Stats(), tuple(), "UUID")
        item3 = Item("item3", ("item", "equippable"), 1, Stats(), tuple(), "UUID")

        ti = Inventory.new()
        ti.add(item1)
        ti.add(item2, 10)
        ti.add(item1, 0)
        ti.remove(item2, 3)
        assert ti.backpack[item1] == 1
        assert ti.backpack[item2] == 7

        ti.equip("head", item1)
        assert ti.backpack[item1] == 0
        assert ti.equipment["head"] == item1

        ti.add(item3, 2)
        ti.equip("head", item3)
        assert ti.backpack[item1] == 1
        assert ti.backpack[item3] == 1
        assert ti.equipment["head"] == item3

        print("Inventory tests passed")


class Character(NamedTuple):
    """Holds data for a combat-capable character (Player, goblin, etc.).

    The default constructor should only be used as an argument of
    Character.modify(). For all other purposes use Character.new().
    """
    name: str = None
    sprite_sheet: dict[str, str] = None
    is_player: bool = None
    is_alive: bool = None

    base: Stats = None
    bonuses: dict[UUID: Stats] = None

    current: Stats = None

    health: int = None
    stamina: int = None
    mana: int = None

    inventory: Inventory=None
    actions: list[Action] = None
    effects: dict = None


    @staticmethod
    def new(name: str, sprite_sheet: dict[str, str], is_player: bool, base_stats: Stats, actions: list[Action],
            initial_effects: dict) -> Character:
        """Character constructor.

        Needed because NamedTuple.__init__ can't be modified.
        """
        return Character(name,
                         sprite_sheet,
                         is_player,
                         True,

                         base_stats,
                         dict(),
                         base_stats,

                         base_stats.max_health,
                         base_stats.max_stamina,
                         base_stats.max_mana,

                         Inventory.new(),
                         actions,
                         initial_effects)


    def modify(self, changes: Character) -> Character:
        """Generate new character sheet based on an existing one.

        Used to get around the un-mofifiablility of NamedTuple.
        Changes represents a second character sheet, empty except for the values
        to be changed.
        """
        new_char = []
        for old, new in zip(self, changes):
            if new is None:
                new_char.append(old)
            else:
                new_char.append(new)
        return Character(*new_char)


    def update_stats(self) -> Stats:
        new_stats = []

        for i, stat in enumerate(self.BASE):
            for bonus in self.bonuses.values():
                stat += bonus[i]
            new_stats.append(stat)
        return Stats(*new_stats)


    def hit(self, attack: DamageInstance) -> (Character, int):
        """Calculate the effect of an attack.

        Returns a modified character sheet of the target and the damage taken.
        """
        # TODO: account for damage type, resistance, etc.
        damage_taken = int(attack.damage)

        health = self.health - damage_taken
        is_alive = self.is_alive

        if health <= 0:
            health = 0
            is_alive = False

        # With this, healing can just be negative damage
        if health > self.current.max_health:
            health = self.current.max_health

        return self.modify(Character(health=health, is_alive=is_alive)), damage_taken


    def __repr__(self) -> str:
        """Proper text rendering of characters."""
        for a in self.actions:
            if a.get_damage() > 0:
                return f"{self.name} (♥ {self.health} / ¤ {a.get_damage()})"
            else:
                continue
        return f"{self.name} (♥ {self.health})"


    @staticmethod
    def _test():
        testchar = Character.new(
            "John Halo",
            True,
            Stats(  8,  16,   4,   8,   6,   4,   2,   4),
            [],
            {})


class DialogLine(NamedTuple):
    lang_key: str
    character: Character = None

    @property
    def text(self):
        """Returns the text of the specified lang_key in the selected language."""
        try:
            lang_text = getattr(text, self.lang_key)
            if isinstance(lang_text, str):
                return lang_text
            elif lang_text is None:
                raise ValueError
            else:
                error_msg = f"Expected lang_text of type str, got {lang_text}"
        except (AttributeError, ValueError):
            error_msg = f"Selected Language doesn't contain '{self.lang_key}'"
        
        logger.error(error_msg)
        return error_msg


class EnumObject(NamedTuple):
    """
    Stores an object with an associated int. Usually used to define how the object is used, such as
    in events and world objects.
    """
    enum: int
    value: object


class _EventTypes(NamedTuple):
    PRESS_KEY: int
    LOAD_ZONE: int
    START_DIALOG: int
    MULTI_EVENT: int

    @classmethod
    def new(cls) -> _EventTypes:
        return cls(*range(4))


class _WorldObjectTypes(NamedTuple):
    GRID_SPRITE: int
    GRID_MULTI_SPRITE: int
    WORLD_CHARACTER: int
    WALK_TRIGGER: int
    
    @classmethod
    def new(cls) -> _WorldObjectTypes:
        return cls(*range(4))


def load_pickle(path: str) -> object:
    """Reads and returns the pickle object at the provided path."""
    try:
        with open(path, "rb") as file:
            return pickle.load(file)
    
    except FileNotFoundError:
        error_msg = f"File missing: {path}"
        logger.error(error_msg)
        return None


def load_text(path: str) -> str:
    """Reads and returns the content of the text file at the provided path."""
    try:
        with open(path, "r", encoding="utf-8") as file:
            return file.read()

    except FileNotFoundError:
        error_msg = f"File missing: {path}"
        logger.error(error_msg)
        return error_msg


def load_text_dir(path: str) -> dict[str, str]:
    """
    Returns a dict with keys being the filenames, values being the contents of
    the files in the directory.
    """
    texts = {}

    for entry in os.listdir(path):
        full_path = os.path.join(path, entry)
        name, ext = os.path.splitext(entry)

        if ext != ".txt":
            logger.warning(f"Expected txt file at path: {full_path}")
            continue

        texts[name] = load_text(full_path)

    return texts


def move_toward(a: int | float, b: int | float, step: int | float = 1) -> int | float:
    """Returns a moved by step towards b without overshooting."""
    return min(a + step, b) if b >= a else max(a - step, b)


def remap_dict(data: dict, key_map: dict) -> dict:
    """
    Returns a new dict with keys of data remapped through key_map and values
    unchanged.
    """
    return {key_map[k]: v for k, v in data.items() if k in key_map}


def try_append(collection: list, item: object) -> None:
    if item is not None:
        collection.append(item)


logger = logging.getLogger(__name__)
logging.basicConfig(filename="logs\\common.log", encoding="utf-8", level=logging.DEBUG)

EVENT_TYPES = _EventTypes.new()
WORLD_OBJECT_TYPES = _WorldObjectTypes.new()

if __name__ == "__main__":
    # Tests
    Inventory._test()
