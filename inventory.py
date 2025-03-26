"""
Fait ...

auteur : Adrien Buschbeck
"""

from typing import NamedTuple

class inventory(NamedTuple):
    """L'inventaire du personnage"""
    armure : Items = None
    right_hand : Items = None 
    left_hand : Items = None
    backpack : dict
    
    
    def equip(body_part, object):
        """equipe un objet sur une partie du corps """
        if body_part == None :
            body_part = object    
        else:
            pass
    
    
    def take(object_taken: Item, self.backpack):
        """Prend un objet et le met dans l'inventaire"""
        for i in slef.backpack:
            if i == None:
                self.backpack[i] = object_taken
        else:
            pass

