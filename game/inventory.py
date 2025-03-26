"""
Fait ...

auteur : Adrien Buschbeck
"""

from typing import NamedTuple

class inventory(NamedTuple):
    """L'inventaire du personnage"""
    armure : object | None
    m_d : object | None 
    m_g : object | None
    bp : dict
    
    
    def equip(loc, obj1):
        """equipe un objet sur une partie du corps """
        if loc == None :
            loc = obj1    
        else:
            pass
    
    
    def take(obj1, bp):
        """Prend un objet et le met dans l'inventaire"""
        bp.append(obj1)

