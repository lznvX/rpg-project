"""combat mechanic prototype

Created on 2025.03.12
Contributors:
    Jakub
"""


from __future__ import annotations
from typing import NamedTuple
from get_input import get_input
import random as r
import time
from lang import get_lang_choice, f
from common import Stats, DamageInstance, Character, Action, Party, CharacterNotFoundError
import monsters as m
import test_items as ti
from uuid import UUID


text = get_lang_choice()
auto_turn_delay = 0.5 # seconds


class CombatParty(NamedTuple):
    name: str
    members: dict[UUID, (Character, bool)]
    leader: UUID


    @staticmethod
    def new(party: Party) -> CombatParty:
        name = party.name
        leader = party.leader
        members = dict()
        for m in party.members:
            members[m.uuid] = (m, True)

        return CombatParty(name, members, leader)


    def get_member(self, member_uuid: UUID) -> Character:
        try:
            char = self.members[member_uuid][0]
        except KeyError:
            raise CharacterNotFoundError(f"Cannot find character with UUID {member_uuid} in {self.name}")

        return char

    def get_valid_targets(self) -> list[UUID]:
        """Generate a list of all attackable targets in this CombatParty.

        i.e. any members that are alive
        """
        targets = []
        for target_id in self.members.keys():
            if self.get_member(target_id).is_alive:
                targets.append(target_id)
            else:
                continue

        return targets


class Battle(NamedTuple):
    """Handles the combat.

    Use Battle.new() instead of the default constructor.
    """
    team1: CombatParty
    team2: CombatParty

    turn_order: list[UUID]

    # team1: list
    # team2: list

    # team1_name: str
    # team2_name: str

    # team1_targets: list
    # team2_targets: list

    # turn_order: list


    def get_team_of_fighter(self, fighter_uuid: UUID) -> CombatParty:
        """Find which team a given character belongs to."""

        try:
            team1.get_member


    @staticmethod
    def new(team1: Party, team2: Party) -> Battle:
        """Initialize a new Battle instance.

        Custom constructor to properly initialize the necessary variables.
        Needed because NamedTuple.__init__ can't be modified.
        """

        combat_team1 = CombatParty(team1)
        combat_team2 = CombatParty(team2)

        targets1 = combat_team1.get_valid_targets()
        targets2 = combat_team2.get_valid_targets()

        turn_order = sorted(targets1 + targets2,
                            key=lambda x:
                            # Couldn't think of a better way to do this
                            team1[x[1]].current.agility if x[0] == 1
                            else team2[x[1]].current.agility, reverse=True
                            )


        # team1_targets = []
        # for i, c in enumerate(team1):
        #     team1_targets.append(("team1", i))

        # team2_targets = []
        # for i, c in enumerate(team2):
        #     team2_targets.append(("team2", i))

        # # Turn order is the two teams combined, sorted by agility
        # # (Character with highest AGI goes first)
        # turn_order = sorted(team1_targets + team2_targets, key=lambda x:
        #                     # Couldn't think of a better way to do this
        #                     team1[x[1]].current.agility if x[0] == 1
        #                     else team2[x[1]].current.agility, reverse=True)

        # return Battle(team1, team2, team1_name, team2_name,
        #               team1_targets, team2_targets, turn_order)


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


def list_choices(choices: list | tuple, text: str="", start_from_1: bool=True,
                 template: str="{}) {}") -> None:

	print(text)
	for i, choice in enumerate(choices):
		if choice is None:
			continue
		print(template.format(i + start_from_1, choice))


def _test_pcs():
    alice = Character.new(
            name            = "Alice",
            sprite_sheet    = None,
            is_player       = False,
            base_stats      = m.DefaultStats.human,
            actions         = {},
            initial_effects = {}
            )
    alice.inventory.add(ti.Sword)
    alice.inventory.add(ti.AgiBoots)
    alice = alice.equip("mainhand", ti.Sword)
    alice = alice.equip("feet", ti.AgiBoots)

    bob = Character.new(
            name            = "Bob",
            sprite_sheet    = None,
            is_player       = True,
            base_stats      = m.DefaultStats.human,
            actions         = {},
            initial_effects = {}
            )
    bob.inventory.add(ti.Sword)
    bob.inventory.add(ti.StrHelmet)
    bob = bob.equip("mainhand", ti.Sword)
    bob = bob.equip("head", ti.StrHelmet)

    return alice, bob


if __name__ == "__main__":
    alice, bob = _test_pcs()
    player_party = Party("Adventuring Party", [alice, bob], bob.uuid)


    gg_leader = m.Hobgoblin()
    goblin_gang = Party("Goblin Gang", [gg_leader, m.Goblin(), m.Goblin(), m.Goblin(), m.Goblin()], gg_leader.uuid)


    current_battle = Battle.new(player_party, goblin_gang)

    current_battle.begin()
