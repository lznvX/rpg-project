"""
Fait ...

auteur : Adrien Buschbeck
"""

from typing import NamedTuple

class inventory(NamedTuple):
    """L'inventaire du personnage"""
    armure : Items = None
    m_d : Items = None 
    m_g : Items = None
    bp : dict
    
    
    def equip(loc, obj1):
        """equipe un objet sur une partie du corps """
        if loc == None :
            loc = obj1    
        else:
            pass
    
    
    def take(obj: Item, self.bp: Item):
        """Prend un objet et le met dans l'inventaire"""
        for i in slef.bp:
            if i == None:
                self.bp[i] = obj
        else:
            pass

