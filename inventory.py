"""
Fait ...

auteur : Adrien Buschbeck
"""

from typing import NamedTuple
from common import Item

class Inventory(NamedTuple):
    """L'inventaire du personnage"""
    mainhand: Item = None
    ofthand: Item = None
    feet: Item = None
    body: Item = None
    head: Item = None
    equipment: dict[str: Item]
    backpack: dict[Item: int]
    slots = ("mainhand", "offhand", "head", "body", "feet")
    
    
    def equip(self, slot, object):
        """equipe un objet sur une partie du corps """
        if not object.is_equippable:
            raise ValueError((f"Item {object_used} not equippable"))
        if not slot in self.slots:
            raise ValueError((f"Slot {slot} does not exist"))
        if equipment[slot] not is None:
            # TODO: implement equipment swapping
            raise ValueError(f"Slot {slot} is occupied")
        equipment[slot] = object
        self.use(object)
        

    def unequip(self, slot):
        """equipe un objet sur une partie du corps """
        if not slot in self.slots:
            raise ValueError((f"Slot {slot} does not exist"))
        if equipment[slot] is None:
            raise ValueError(f"Slot {slot} is empty")
        equipment[slot] = None
        self.add(object)

    
    def add(self, object_taken: Item):
        """Prend un objet et le met dans l'inventaire"""
        if backpack[object_taken] is None:
            self.backpack[object_taken] = 1
        else:
            self.backpack[object_taken] += 1

    def use(self, object_used: Item):
        if backpack[object_taken] is None:
            raise ValueError(f"Item {object_used} not found")
        elif backpack[object_taken] <= 0:
            raise ValueError(f"Not enough of {object_used}")     
        else:
            self.backpack[object_taken] -= 1
            if self.backpack[object_taken] <= 0:
                self.backpack[object_taken] = None
