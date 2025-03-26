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
from common import Stats, DamageInstance, Character, Action


text = get_lang_choice()
auto_turn_delay = 0.5 # seconds


class DefaultStats(NamedTuple):
    """A collection of default stats for various character races."""

              #       MHP, MST, MMA, STR, AGI, ACU, ARM, RES
    human     = Stats(  8,  16,   4,   8,   6,   4,   2,   4)
    goblin    = Stats(  2,   8,   2,   2,  16,   1,   1,   2)
    hobgoblin = Stats(  5,   8,   3,   4,   8,   2,   2,   2)


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
		if choice is None:
			continue
		print(template.format(i + start_from_1, choice))


if __name__ == "__main__":
    p = Character.new("Alice", False, DefaultStats.human, [slash, stab], {})
    q = Character.new("Bob", True, DefaultStats.human, [slash, stab], {})


    current_battle = Battle.new([p, q], "Adventuring Party", [Goblin(), Goblin(), Goblin(), Hobgoblin(), Hobgoblin()], "Goblin Gang")

    current_battle.begin()
