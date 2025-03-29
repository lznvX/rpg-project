"""Classes and functions shared between several systems

Created on 2025.03.20
Contributors:
    Jakub
    Adrien
    Romain (added 7 lines, totally deserves to be here)
"""


from typing import NamedTuple
from uuid import UUID, uuid4


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


    def modify(self, changes: "Stats") -> "Stats":
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

    name: str
    action_type: str
    description: str

    base_damage: int
    damage_type: str
    effects: dict


    def get_damage(self) -> float:
        return self.base_damage


    def create_damage_instance(self) -> DamageInstance:
        return DamageInstance(self.damage(), self.damage_type, self.effects)


    def __repr__(self):
        return f"{self.name} (¤ {self.get_damage()})"


class Item(NamedTuple):

    name: str
    description: str # will show up when inspecting the item (later)

    tags: tuple[str]
    #   weapon -> melee, bow, staff (magic), shield, etc.
    #   armor -> or separate tags for slots, i.e. helmet, armor, boots, etc.
    #   consumable (e.g. potions, arrows, etc.)
    #   material (sellable stuff? maybe crafting)
    #   currency (have gold as an item -> balance carrying items vs carrying money)

    weight: int # -> limit for storage, heavy armor slows you down, +relevant in combat

    max_durability: int
    durability: int # do we want durability?

    stat_bonus: Stats # added to the user's stats
    actions: list[Action] # added to the user's actions
    uuid: UUID # used to keep track of applied bonuses


class Character(NamedTuple):
    """Holds data for a combat-capable character (Player, goblin, etc.).

    The default constructor should only be used as an argument of
    Character.modify(). For all other purposes use Character.new().
    """
    name: str = None
    is_player: bool = None
    is_alive: bool = None

    base: Stats = None
    bonuses: dict[UUID: Stats] = None

    current: Stats = None

    health: int = None
    stamina: int = None
    mana: int = None

    actions: list[Action] = None
    effects: dict = None


    @staticmethod
    def new(name: str, is_player: bool, base_stats: Stats, actions: list[Action],
            initial_effects: dict) -> "Character":
        """Character constructor.

        Needed because NamedTuple.__init__ can't be modified.
        """
        return Character(name,
                         is_player,
                         True,

                         base_stats,
                         dict(),
                         base_stats,

                         base_stats.max_health,
                         base_stats.max_stamina,
                         base_stats.max_mana,

                         actions,
                         initial_effects)

      
    def modify(self, changes: "Character") -> "Character":
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


    def hit(self, attack: DamageInstance) -> ("Character", int):
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


class DialogLine(NamedTuple):
    text: str
    character: Character = None


def move_toward(a: int | float, b: int | float, step: int | float = 1) -> int | float:
    """Returns a moved by step towards b without overshooting."""
    return min(a + step, b) if b >= a else max(a - step, b)
