"""The inventory system

Created on 2025.03.19
Contributors:
    Adrien
    Jakub
"""

from collections import Counter
from typing import NamedTuple, Self
from common import Item, Stats


class Inventory(NamedTuple):
    """The inventory of a character.

    Not necessarily the player.
    """
    equipment: dict[str, Item]
    backpack: Counter[Item, int]
    slots = ("mainhand", "offhand", "head", "body", "feet")


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


    @classmethod
    def new(self) -> Self:
        """Create a new empty inventory."""
        equipment = dict()
        for slot in self.slots:
            equipment[slot] = None

        return Inventory(equipment, Counter())


    @staticmethod
    def _test():
        item1 = Item("item1", "lorem ipsum", ("item", "equippable"), 1, 100, 100, Stats(), tuple(), "UUID")
        item2 = Item("item2", "Poland", ("item",), 1, 100, 100, Stats(), tuple(), "UUID")
        item3 = Item("item3", "Ave Caesar", ("item", "equippable"), 1, 100, 100, Stats(), tuple(), "UUID")

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

        print("All tests passed")


if __name__ == "__main__":
    Inventory._test()
