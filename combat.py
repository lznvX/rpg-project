"""combat mechanic prototype

Created on 2025.03.12
Contributors:
    Jakub
"""


from typing import NamedTuple, Self
from get_input import get_input
import random as r
import time
from lang import get_lang_choice, f


text = get_lang_choice()
auto_turn_delay = 0.5 # seconds
current_battle = None


class Stats(NamedTuple):
    """Stores the stats of a charcter.

	Use more than one instance per character to differentiate base and current
	stats.
	"""
    max_health: int=None     # if it drops to 0, you die
    max_stamina: int=None    # used as a resource for performing PHYSICAL actions
    max_mana: int=None       # used as a resource for performing MAGICAL actions

    strength: int=None       # increases damage of PHYSICAL attacks
    agility: int=None        # determines turn order, flee chance, damage of some attacks
    acumen: int=None         # determines damage of MAGICAL attacks

    armor: int=None              # decreases PHYSICAL damage taken
    magical_resistance: int=None # decreases MAGICAL damage taken


    def modify(self, changes: Self) -> Self:
        """Generate new stat sheet based on an existing one.

        Changes are represented as another stat sheet. A value of None (default
        value for all stats) results in no change, allowing for modification
        of 1, some, or all stats at the same time.
        """
        new_stats = []
        for old, new in zip(self, changes):
            if new == None:
                new_stats.append(old)
            else:
                new_stats.append(new)
        return Stats(*new_stats)


class DefaultStats(NamedTuple):
    """A collection of default stats for various character races."""

              #       MHP, MST, MMA, STR, AGI, ACU, ARM, RES
    human     = Stats(  8,  16,   4,   8,   6,   4,   2,   4)
    goblin    = Stats(  2,   8,   2,   2,  16,   1,   1,   2)
    hobgoblin = Stats(  5,   8,   3,   4,   8,   2,   2,   2)


class DamageInstance(NamedTuple):
    """Holds information about a single instance of damage.

    Created as a result of an attack or other interaction. Should be passed to
    the target of the attack/interaction.
    """
    damage: float
    damage_type: str
    effects: dict


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


class Character(NamedTuple):
    """Holds data for a combat-capable character (Player, goblin, etc.).

    The default constructor should only be used as an argument of
    Character.modify(). For all other purposes use Character.new().
    """
    name: str=None
    is_player: bool=None
    is_alive: bool=None

    BASE: Stats=None
    current: Stats=None

    health: int=None
    stamina: int=None
    mana: int=None

    actions: list[Action]=None
    effects: dict=None


    @staticmethod
    def new(name: str, is_player: bool, base_stats: Stats, actions: list[Action],
            initial_effects: dict) -> Self:
        """Character constructor.

        Needed because NamedTuple.__init__ can't be modified.
        """
        return Character(name,
                         is_player,
                         True,

                         base_stats,
                         base_stats,

                         base_stats.max_health,
                         base_stats.max_stamina,
                         base_stats.max_mana,

                         actions,
                         initial_effects)

    def modify(self, changes: Self) -> Self:
        """Generate new character sheet based on an existing one.

        Used to get around the un-mofifiablility of NamedTuple.
        Changes represents a second character sheet, empty except for the values
        to be changed.
        """
        new_char = []
        for old, new in zip(self, changes):
            if new == None:
                new_char.append(old)
            else:
                new_char.append(new)
        return Character(*new_char)


    def hit(self, attack: DamageInstance) -> (Self, int):
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


class Battle(NamedTuple):
    """Handles the combat.

    Use Battle.new() instead of the default constructor.
    """
    team1: list
    team2: list

    team1_name: str
    team2_name: str

    team1_targets: list
    team2_targets: list

    turn_order: list


    @staticmethod
    def new(team1: list[Character], team1_name: str,
            team2: list[Character], team2_name: str) -> Self:
        """Initialize a new Battle instance.

        Custom constructor to properly initialize the necessary variables.
        Needed because NamedTuple.__init__ can't be modified.
        """

        team1_targets = []
        for i, c in enumerate(team1):
            team1_targets.append(("team1", i))

        team2_targets = []
        for i, c in enumerate(team2):
            team2_targets.append(("team2", i))

        # Turn order is the two teams combined, sorted by agility
        # (Character with highest AGI goes first)
        turn_order = sorted(team1_targets + team2_targets, key=lambda x:
                            # Couldn't think of a better way to do this
                            team1[x[1]].current.agility if x[0] == 1
                            else team2[x[1]].current.agility, reverse=True)

        return Battle(team1, team2, team1_name, team2_name,
                      team1_targets, team2_targets, turn_order)


    @staticmethod
    def attack(attacker: Character, attack: Action, victim: Character
               ) -> (Character, Character, int):
        """Determine the result of an intercation during combat."""


        victim, damage_taken = victim.hit(DamageInstance(attack.get_damage(),
                               attack.damage_type, attack.effects))

        # returning the attacker too if we ever do thorns damage
        return attacker, victim, damage_taken


    def get_fighter(self, reference: (str, int)) -> Character:
        """Find the relevant character by reference.

        reference:
        - "team1" (player) / "team2" (enemy),
        - index within the team
        """
        try:
            match reference[0]:
                case "team1":
                    fighter = self.team1[reference[1]]
                case "team2":
                    fighter = self.team2[reference[1]]
                case _:
                    raise ValueError(f"Unknown fighter reference: {reference}")
        except IndexError:
            raise ValueError(f"Unknown fighter reference: {reference}")
        else:
            return fighter


    def get_player_action(self, player: Character, allies: list[(str, int)],
                          enemies: list[(str, int)]) -> (Action, (str, int)):
        """Get the player's choice of action and action target."""

        list_choices(player.actions, text.battle_action_choice.format(player.name))
        action_index = get_input(int, True, (1, len(player.actions)))
        action = player.actions[action_index-1]

        enemies_actual = []
        for e in enemies:
            enemies_actual.append(self.get_fighter(e))
        list_choices(enemies_actual, f(text.battle_target_choice, action))
        enemy_index = get_input(int, True, (1, len(enemies_actual)))
        enemy_ref = enemies[enemy_index-1]

        return action, enemy_ref


    def begin(self) -> None:

        print(text.battle_begin)
        print()
        print(self)

        is_fight_on = True
        turn = 0

        while is_fight_on:
            turn += 1

            print()
            print("====================")
            print(f(text.battle_turn, turn))
            time.sleep(2*auto_turn_delay)

            for fighter_ref in self.turn_order:
                fighter = self.get_fighter(fighter_ref)

                # Do we still need that?
                if not fighter.is_alive:
                    continue

                if fighter_ref[0] == "team1":
                    allies = self.team1_targets
                    enemies = self.team2_targets
                else:
                    allies = self.team2_targets
                    enemies = self.team1_targets


                # TODO: Implement player choice again
                if fighter.is_player:
                    print()
                    attack, target_ref = self.get_player_action(fighter, allies, enemies)
                else:
                    # TODO: Implement better NPC AI
                    attack = r.choice(fighter.actions)
                    target_ref = r.choice(enemies)

                target = self.get_fighter(target_ref)

                fighter, target, damage_dealt = Battle.attack(fighter, attack, target)

                print()
                print(f(text.battle_attack, fighter.name, attack.name, target.name))
                print(f(text.battle_damage, target.name, damage_dealt, target.health))

                # overwrite the fighter and character saved in the Battle instance
                if fighter_ref[0] == "team1":
                    self.team1[fighter_ref[1]] = fighter
                    self.team2[target_ref[1]] = target
                else:
                    self.team2[fighter_ref[1]] = fighter
                    self.team1[target_ref[1]] = target

                if not target.is_alive:
                    print(f(text.battle_death, target.name))
                    enemies.remove(target_ref)

                    if len(self.team1_targets) == 0:
                        print()
                        print(text.battle_loss)
                        is_fight_on = False
                        break
                    elif len(self.team2_targets) == 0:
                        print()
                        print(text.battle_win)
                        print(f(text.battle_rewards, "0", "0"))
                        is_fight_on = False
                        break
                time.sleep(auto_turn_delay)


    def __repr__(self) -> str:
        team1 = []
        for a in self.team1:
            team1.append(repr(a))
        team1 = ", ".join(team1)

        team2 = []
        for e in self.team2:
            team2.append(repr(e))
        team2 = ", ".join(team2)

        return f"{self.team1_name}\n{team1}\n\nVS\n\n{self.team2_name}\n{team2}"


light_stab = Action(text.light_stab_name, "attack", text.light_stab_desc, 1, "physical", {})
stab = Action(text.stab_name, "attack", text.stab_desc, 2, "physical", {})
slash = Action(text.slash_name, "attack", text.slash_desc, 3, "physical", {})


def Goblin() -> Character:
    return Character.new("Goblin", False, DefaultStats.goblin, [light_stab], {})


def Hobgoblin() -> Character:
    return Character.new("Hobgoblin", False, DefaultStats.hobgoblin, [stab], {})


def list_choices(choices: list | tuple, text: str="", start_from_1: bool=True,
                 template: str="{}) {}") -> None:

	print(text)
	for i, choice in enumerate(choices):
		if choice == None:
			continue
		print(template.format(i + start_from_1, choice))


if __name__ == "__main__":
    p = Character.new("Alice", False, DefaultStats.human, [slash, stab], {})
    q = Character.new("Bob", True, DefaultStats.human, [slash, stab], {})


    current_battle = Battle.new([p, q], "Adventuring Party", [Goblin(), Goblin(), Goblin(), Hobgoblin(), Hobgoblin()], "Goblin Gang")

    current_battle.begin()
