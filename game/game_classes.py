"""Game classes for characters and actions

Created on 2025.05.14
Contributors:
    Jakub
"""

from __future__ import annotations
from typing import NamedTuple
from collections import Counter
from uuid import UUID, uuid4
from common import named_tuple_modifier
from lang import translate

null_uuid = UUID('00000000-0000-0000-0000-000000000000')


class SlotNotFoundError(ValueError):
    """Raised when a non-existent inventory slot is referenced."""
    pass
class ItemNotEquippableError(ValueError):
    """Raised when the player tries to equip a non-equippable item."""
    pass
class SlotEmptyError(ValueError):
    """Raised when an empty slot is supposed to be emptied."""
    # I'm not sure we need this?
    pass
class NotEnoughItemError(ValueError):
    """Raised when an inventory doesn't contain enough of an item to perform an action."""
    pass
class ItemNotFoundError(ValueError):
    pass
class IncompatibleSlotError(ValueError):
    """raised when an item is inserted in an incorrect slot."""
    pass
class TaskNotFoundError(ValueError):
    """raised by an Inventory.tasklist when referencing a nonexistant task."""
    pass
class CharacterNotFoundError(ValueError):
    """Raised when a character with the given UUID doesn't exist"""
    pass


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


    def modify(self, **changes) -> Stats:
        """Generate new stat sheet based on an existing one.

        Used to get around the un-mofifiablility of NamedTuple.
        """
        return named_tuple_modifier(Stats, self, **changes)


class Action(NamedTuple):
    """Describes an action during combat."""

    name: str           # Internal name; english only
    action_type: str    #

    base_damage: int    # How much damage is dealt by the action
    damage_type: str    # What type is the damage
                        # different damage types will result in different
                        # final damage, based on target's resistances
    effects: tuple[...] # Effects to be applied to the target


    @property
    def display_name(self) -> str:
        """Fetch the action's name in the appropriate language."""
        return translate("action_names." + self.name)


    @property
    def description(self) -> str:
        """Fetch the action's description in the appropriate language."""
        # will show up when inspecting the action (later)
        return translate("action_descriptions." + self.name)


    def get_damage(self) -> float:
        return self.base_damage


    def create_damage_instance(self) -> DamageInstance:
        return DamageInstance(self.damage(), self.damage_type, self.effects)


    def __repr__(self):
        return f"{self.display_name} (¤ {self.get_damage()})"


class Item(NamedTuple):
    name: str = None                # Internal name; english only

    tags: tuple[str] = None
    #   weapon -> melee, bow, staff (magic), shield, etc.
    #   armor -> or separate tags for slots, i.e. helmet, armor, boots, etc.
    #   consumable (e.g. potions, arrows, etc.)
    #   material (sellable stuff? maybe crafting)
    #   currency (have gold as an item -> balance carrying items vs carrying money)

    weight: int = None              # -> limit for storage, heavy armor slows
                                    # you down, +relevant in combat

    stat_bonus: Stats = None        # added to the user's stats
    actions: tuple[Action] = None   # added to the user's actions
    uuid: UUID = None               # used to keep track of applied bonuses


    @staticmethod
    def new(name: str="test_item",
            tags: tuple[str]=tuple(),
            weight: int=1,
            stat_bonus: Stats=Stats(),
            actions: tuple[Action]=tuple(),
            ) -> Item:
         """Item constructor.

         Needed because NamedTuple.__init__ can't be modified.
         """
         return Item(name,
                     tags,
                     weight,
                     stat_bonus,
                     actions,
                     # a null UUID corresponds to an un-equipped item
                     null_uuid
                     )


    def modify(self, **changes) -> Item:
        """Generate new item based on an existing one.

        Used to get around the un-mofifiablility of NamedTuple.
        """
        return named_tuple_modifier(Item, self, **changes)


    def equipped(self) -> Item:
        """Create an equipped version of the item.

        i.e. one that has a UUID.
        """
        return self.modify(uuid=uuid4())


    def unequipped(self) -> Item:
        """Create an unequipped version of the item.

        i.e. one that has an empty UUID.
        """
        return self.modify(uuid=null_uuid)


    @property
    def display_name(self) -> str:
        """Fetch the item's name in the appropriate language."""
        return translate("item_names." + self.name)


    @property
    def description(self) -> str:
        """Fetch the item's description in the appropriate language."""
        # will show up when inspecting the item (later)
        return translate("item_description." + self.name)


    def __repr__(self):
        return f"{self.display_name}"


class Inventory(NamedTuple):
    """The inventory of a character.

    Not necessarily the player.
    """
    equipment : dict[str, Item]
    tasklist : list[Task]
    backpack : Counter[Item]
    slots = ("mainhand", "offhand", "head", "body", "feet")


    @classmethod
    def new(self) -> Inventory:
        """Create a new empty inventory."""
        equipment = dict()
        tasklist = list()
        for slot in self.slots:
            equipment[slot] = None

        return Inventory(equipment, tasklist, Counter())


    def equip(self, slot: str, item: Item) -> UUID:
        """Equip an item from the backpack in the given slot.

        Returns the item's UUID so that references to the item may be added.

        Supports hot-swapping.
        """
        if not "equippable" in item.tags:
            raise ItemNotEquippableError(f"Item {item} not equippable")
        if not slot in item.tags:
            raise IncompatibleSlotError(f"Item {item} cannot be equipped in {slot}")

        if not slot in self.slots:
            raise SlotNotFoundError(f"Slot {slot} does not exist")

        if self.equipment[slot] is not None:
            # slot already occupied
            self.unequip(slot)

        self.remove(item)
        equipped_item = item.equipped()
        self.equipment[slot] = equipped_item
        return equipped_item.uuid


    def unequip(self, slot: str) -> UUID:
        """Remove an item from the given slot and add it back to the backpack.

        Returns the item's UUID so that references to the item may be deleted.
        """
        if not slot in self.slots:
            raise SlotNotFoundError(f"Slot {slot} does not exist")
        if self.equipment[slot] is None:
            raise SlotEmptyError(f"Slot {slot} is empty")

        item = self.equipment[slot]
        self.equipment[slot] = None
        self.add(item.unequipped())

        return item.uuid


    def add(self, item: Item, count: int=1):
        """Add an item to the backpack."""
        assert count >= 0

        self.backpack[item] += count


    def remove(self, item: Item, count: int=1):
        """Remove an item from the backpack."""
        assert count >= 0

        if self.backpack[item] < count:
            raise NotEnoughItemError(f"Inventory does not contain enough {item} to remove {count}")
        else:
            self.backpack[item] -= count

        if self.backpack[item] <= 0:
            del self.backpack[item]


    def use(self, item: Item):
        """Use an item from the backpack.

        The item is consumed.
        """
        if self.backpack[item] > 0:
            self.remove(item)
            #TODO: implement item using
        else:
            raise NotEnoughItemError(f"Inventory does not contain any {item}")


    def accept(self, task: Task):
        """Add a task to the tasklist."""
        self.tasklist.append(task)


    def finish(self, finished_task: Task):
        """Remove a task of the tasklist."""
        task_uuid = finished_task.uuid

        for task_id, task in enumerate(self.tasklist):
            if task.uuid != task_uuid:
                continue
            else:

                del self.tasklist[task_id]
                return None
        else:
            raise TaskNotFoundError(f"The task {task} is not in your task list.")


    def claim(self, task: Task):
        """Try to see if you have the ressources to complete a task"""
        if task not in self.tasklist:
            raise TaskNotFoundError(f"The task {task} is not in your task list.")
        else:
            for item in task.conditions.keys():
                if self.backpack[item] < task.conditions[item]:
                    raise NotEnoughItemError(f"Not enough {item} to finish {task}")
                    return None

            for item in task.conditions.keys():
                self.remove(item, task.conditions[item])

            for item in task.reward:
                self.add(item, task.reward[item])
            self.finish(task)


    @staticmethod
    def _test():
        item1 = Item.new("item1", ("head", "equippable"), 1, Stats(), tuple())
        item2 = Item.new("item2", ("item",), 1, Stats(), tuple())
        item3 = Item.new("item3", ("head", "equippable"), 1, Stats(), tuple())

        task1 = Task.new("task1", {item1 : 1}, {item2 : 3})
        task2 = Task.new("task2", {item1 : 12}, {item2 : 43})

        ti = Inventory.new()
        ti.add(item1)
        ti.add(item2, 10)
        ti.add(item1, 0)
        ti.remove(item2, 3)
        assert ti.backpack[item1] == 1
        assert ti.backpack[item2] == 7

        ti.equip("head", item1)
        assert ti.backpack[item1] == 0
        assert ti.equipment["head"].uuid != null_uuid
        assert ti.equipment["head"].unequipped() == item1

        ti.add(item3, 2)
        ti.equip("head", item3)
        assert ti.backpack[item1] == 1
        assert ti.backpack[item3] == 1
        assert ti.equipment["head"].unequipped() == item3

        ti.accept(task1)
        ti.accept(task2)
        assert task1 in ti.tasklist
        assert task2 in ti.tasklist

        ti.finish(task2)
        assert task2 not in ti.tasklist

        ti.claim(task1)
        assert task1 not in ti.tasklist
        assert ti.backpack[item1] == 0
        assert ti.backpack[item2] == 10

        print("Inventory tests passed")


class Character(NamedTuple):
    """Holds data for a combat-capable character (Player, goblin, etc.).

    The default constructor should not be used. Instead, use Character.new().
    """
    name: str = None
    uuid: UUID = None
    sprite_sheet: dict[str, str] = None
    is_player: bool = None
    is_alive: bool = None

    base: Stats = None
    bonuses: dict[UUID, Stats] = None

    current: Stats = None

    health: int = None
    stamina: int = None
    mana: int = None

    inventory: Inventory = None
    actions: dict[UUID, Action] = None
    effects: dict = None


    @staticmethod
    def new(name: str, sprite_sheet: dict[str, str], is_player: bool,
            base_stats: Stats, actions: dict[UUID, Action],
            initial_effects: dict, uuid: UUID=None) -> Character:
        """Character constructor.

        Needed because NamedTuple.__init__ can't be modified.
        """
        return Character(name,
                         uuid if uuid is not None else uuid4(),
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


    def equip(self, slot: str, item: Item) -> Character:
        """Equip an item from the backpack in the given slot.

        Supports hot-swapping.
        """
        try:
            item_uuid = self.inventory.equip(slot, item)
        except SlotNotFoundError:
            ...
        except ItemNotEquippableError:
            ...
        else:
            # self.actions[item_uuid] = item.actions

            self.bonuses[item_uuid] = item.stat_bonus
            new_stats = self.update_stats()
            updated_character = self.modify(current=new_stats)
            # would've been better to update the character directly, but NamedTuple...
            return updated_character


    def unequip(self, slot: str) -> Character:
        """Remove an item from the given slot and add it back to the backpack."""
        try:
            item_uuid = self.inventory.unequip(slot)
        except SlotNotFoundError:
            ...
        except SlotEmptyError:
            ...
        else:
            # del self.actions[item_uuid]

            del self.bonuses[item_uuid]
            new_stats = self.update_stats()
            updated_character = self.modify(current=new_stats)
            # would've been better to update the character directly, but NamedTuple...
            return updated_character


    def modify(self, **changes) -> Character:
        """Generate new character sheet based on an existing one.

        Used to get around the un-mofifiablility of NamedTuple.
        """
        return named_tuple_modifier(Character, self, **changes)


    def update_stats(self) -> Stats:
        new_stats = []

        for i, stat in enumerate(self.base):
            for bonus in self.bonuses.values():
                if bonus[i] is None:
                    continue
                else:
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

        return self.modify(health=health, is_alive=is_alive), damage_taken


    def __repr__(self) -> str:
        """Proper text rendering of characters."""
        # for a in self.actions.values():
        #     if a.get_damage() > 0:
        #         return f"{self.name} (♥ {self.health} / ¤ {a.get_damage()})"
        #     else:
        #         continue

        return f"{self.name} (♥ {self.health})"


    @staticmethod
    def _test():
        # I know this is unconventional, but it's just for testing
        import test_items as ti

        testchar = Character.new(
            "John Halo",
            None,
            True,
            #     MHP, MST, MMA, STR, AGI, ACU, ARM, RES
            Stats(  8,  16,   4,   8,   6,   4,   2,   4),
            [],
            {})

        testchar.inventory.add(ti.Sword, 2)
        testchar.inventory.add(ti.PotionHealth, 10)
        testchar.inventory.add(ti.AgiBoots)
        testchar.inventory.add(ti.StrHelmet)

        testchar = testchar.equip("feet", ti.AgiBoots)
        testchar = testchar.equip("head", ti.StrHelmet)
        testchar = testchar.equip("mainhand", ti.Sword)

                                   #     MHP, MST, MMA, STR, AGI, ACU, ARM, RES
        assert testchar.current == Stats(  8,  16,   4,  13,  11,   4,   9,   4)

        testchar = testchar.unequip("head")
        assert testchar.inventory.backpack[ti.StrHelmet] == 1

                                   #     MHP, MST, MMA, STR, AGI, ACU, ARM, RES
        assert testchar.current == Stats(  8,  16,   4,   8,  11,   4,   4,   4)

        print("Character tests passed")


class Party(NamedTuple):
    name: str
    members: tuple[Character]
    leader: UUID


    def get_member(self, member_uuid: UUID) -> Character:
        for member in self.members:
            if member.uuid == member_uuid:
                return member

        raise CharacterNotFoundError(f"Cannot find character with UUID {member_uuid} in {self.name}")


class Task(NamedTuple):
    """
    A quest that if the condition is fulfild give a reward
    """
    name: str
    conditions: Counter[Item]
    reward: Counter[Item]
    uuid: UUID


    @staticmethod
    def new(name: str, conditions: dict[Item, int], reward: dict[Item, int]) -> Item:
         """Task constructor.

         Needed because NamedTuple.__init__ can't be modified.
         """
         return Task(name,
                     Counter(conditions),
                     Counter(reward),
                     uuid4(),
                     )

    @property
    def display_name(self) -> str:
        """Fetch the task's name in the appropriate language."""
        try:
            return lang_text.task_names[self.name]
        except KeyError:
            return self.name


    @property
    def description(self) -> str:
        """Fetch the task's description in the appropriate language."""
        # will show up when inspecting the task (later)
        try:
            return lang_text.task_descriptions[self.name]
        except KeyError:
            return ""


if __name__ == "__main__":
    # Tests
    Inventory._test()
    Character._test()
