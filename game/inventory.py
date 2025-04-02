"""
Fait ...

auteur : Adrien Buschbeck, Jakub Mann
"""

from typing import NamedTuple
from common import Item, Stats

class Inventory(NamedTuple):
    """L'inventaire du personnage"""
    equipment: dict[str: Item]
    backpack: dict[Item: int]
    slots = ("mainhand", "offhand", "head", "body", "feet")

    def equip(self, slot, item):
        """equipe un objet sur une partie du corps """
        if not object.is_equippable: #error
            raise ValueError((f"Item {item} not equippable"))
        if not slot in self.slots:
            raise ValueError((f"Slot {slot} does not exist"))

        if self.equipment[slot] is not None: #if already a equipment
            current_item = self.equipment[slot]
            self.equipment[slot] = None
            self.equip(slot, object)
            self.add(current_item)
        self.equipment[slot] = object
        self.use(object)

    def unequip(self, slot):
        """equipe un objet sur une partie du corps """
        if not slot in self.slots:
            raise ValueError((f"Slot {slot} does not exist"))
        if self.equipment[slot] is None:
            raise ValueError(f"Slot {slot} is empty")
        self.equipment[slot] = None
        self.add(object)

    def add(self, item: Item):
        """Prend un objet et le met dans l'inventaire"""
        if item not in self.backpack.keys():
            self.backpack[item] = 1
        elif self.backpack[item] is None:
            self.backpack[item] = 1
        else:
            self.backpack[item] += 1

    def use(self, item: Item):
        if self.backpack[item] is None:
            raise ValueError(f"Item {item} not found")
        elif self.backpack[item] <= 0:
            raise ValueError(f"Not enough of {item}")
        else:
            self.backpack[item] -= 1
            if self.backpack[item] <= 0:
                self.backpack[item] = None
    def _test():
        item1 = Item("item1", "lorem ipsum", ("item",), 1, 100, 100, Stats(), tuple(), "UUID")
        item2 = Item("item2", "Poland", ("item",), 1, 100, 100, Stats(), tuple(), "UUID")

        test_inventory = Inventory.new()
        test_inventory.add(item1)

    @classmethod
    def new(self):

        equipment = dict()
        for slot in self.slots:
            equipment[slot] = None

        return Inventory(equipment, dict())

if __name__ == "__main__":
    ...
