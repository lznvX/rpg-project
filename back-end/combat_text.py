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
from lang import translate, f
from game_classes import Stats, DamageInstance, Character, Action, Party, CharacterNotFoundError
import monsters as m
import test_items as ti
from uuid import UUID
import logging


combat_log = logging.getLogger(__name__)
#auto_turn_delay = 0.5 # seconds


combat_log.debug(" combat.py loaded")


class CombatParty(NamedTuple):
    name: str
    members: dict[UUID, (Character, bool)]
    leader: UUID


    @staticmethod
    def new(party: Party) -> CombatParty:
        name = party.name
        leader = party.leader
        members = dict()
        for member in party.members:
            members[member.uuid] = (member, True)

        combat_log.info(f" Creating CombatParty \"{name}\"")
        combat_log.debug(f" {name} members:\n\n{members}\n\nleader: {leader}\n")

        return CombatParty(name, members, leader)


    def get_member(self, member_uuid: UUID) -> Character:
        if self.has_member(member_uuid):
            char = self.members[member_uuid][0]
            # combat_log.debug(f" {self.name} - found member {char}")
            return char
        else:
            raise CharacterNotFoundError(f"Cannot find character with UUID {member_uuid} in {self.name}")


    def has_member(self, member_uuid: UUID) -> bool:
        """Check if a member with a given UUID exists in this CombatParty."""
        if member_uuid in self.members.keys():
            return True
        else:
            return False


    @property
    def valid_targets(self) -> list[UUID]:
        """Generate a list of all attackable targets in this CombatParty.

        i.e. any members that are alive
        """
        # combat_log.debug(f" {self.name} - collecting valid targets")
        targets = []
        for target_id in self.members.keys():
            if self.get_member(target_id).is_alive:
                targets.append(target_id)
            else:
                continue

        return targets


    def update_member(self, member_uuid, new_member) -> None:
        self.members[member_uuid] = (new_member, self.members[member_uuid][1])


    def __repr__(self):
        return ", ".join([str(self.get_member(member_uuid)) for member_uuid in self.valid_targets])


    def __str__(self):
        return repr(self)


class Battle(NamedTuple):
    """Handles the combat.

    Use Battle.new() instead of the default constructor.
    """
    team1: CombatParty
    team2: CombatParty

    turn_order: list[UUID]


    def get_teams(self, fighter_uuid: UUID) -> (CombatParty, CombatParty):
        """Find the ally and enemy party based on a character's UUID."""
        if self.team1.has_member(fighter_uuid):
            return self.team1, self.team2
        elif self.team2.has_member(fighter_uuid):
            return self.team2, self.team1
        else:
            raise CharacterNotFoundError(f"Cannot find character with UUID {fighter_uuid} in the current battle")


    @staticmethod
    def new(team1: Party, team2: Party) -> Battle:
        """Initialize a new Battle instance.

        Custom constructor to properly initialize the necessary variables.
        Needed because NamedTuple.__init__ can't be modified.
        """
        combat_log.info(f" Creating a Battle between '{team1.name}' and '{team2.name}'")

        combat_team1 = CombatParty.new(team1)
        combat_team2 = CombatParty.new(team2)

        targets1 = combat_team1.valid_targets
        targets2 = combat_team2.valid_targets

        # doesn't need to be sorted until the battle begins
        turn_order = targets1 + targets2

        return Battle(combat_team1, combat_team2, turn_order)


    @staticmethod
    def attack(attacker: Character, attack: Action, victim: Character
               ) -> (Character, Character, int):
        """Determine the result of an intercation during combat."""


        victim, damage_taken = victim.hit(DamageInstance(attack.get_damage(),
                               attack.damage_type, attack.effects))

        # returning the attacker too if we ever do thorns damage
        return attacker, victim, damage_taken


    def get_fighter(self, fighter_uuid: UUID) -> Character:
        """Find the relevant character by UUID."""
        # combat_log.debug(f" Looking for fighter {fighter_uuid}")

        if self.team1.has_member(fighter_uuid):
            return self.team1.get_member(fighter_uuid)
        elif self.team2.has_member(fighter_uuid):
            return self.team2.get_member(fighter_uuid)
        else:
            raise CharacterNotFoundError(f"Cannot find character with UUID {fighter_uuid} in the current battle")


    def _sort_turn_order(self):
        sort_key = lambda uuid: self.get_fighter(uuid).current.agility
        combat_log.debug(" Sorting turn order")
        self.turn_order.sort(key=sort_key, reverse=True)
        combat_log.debug(" Turn order sorted")


    def get_player_action(self, player: Character, allies: CombatParty,
                          enemies: CombatParty) -> (Action, UUID):
        """Get the player's choice of action and action target."""
        combat_log.debug(" Getting player input")

        action_names = []
        for action in player.actions:
            action_names.append(action[1])
        list_choices(action_names, translate("combat.action_choice").format(player.name))
        action_index = get_input(int, True, (1, len(player.actions)))
        action = player.actions[action_index-1][1]
        combat_log.debug(f" Player chooses to use <{action.name}>")

        enemies_actual = []
        for enemy in enemies.valid_targets:
            enemies_actual.append(self.get_fighter(enemy))
        list_choices(enemies_actual, f(translate("combat.target_choice"), action))
        enemy_index = get_input(int, True, (1, len(enemies_actual)))
        enemy_uuid = enemies.valid_targets[enemy_index-1]
        combat_log.debug(f" Player chooses to attack {self.get_fighter(enemy_uuid)} ({enemy_uuid})")

        return action, enemy_uuid


    def begin(self) -> None:

        combat_log.info(" Battle started")
        print(translate("combat.begin"))
        print()
        print(self)

        self._sort_turn_order()
        is_fight_on = True
        turn = 0
        #time.sleep(0.5)

        while is_fight_on:
            turn += 1
            combat_log.info(f" Turn {turn} started")

            print()
            print("====================")
            print(f(translate("combat.turn"), turn))
            #time.sleep(2*auto_turn_delay)

            for fighter_uuid in self.turn_order:
                allies, enemies = self.get_teams(fighter_uuid)

                fighter = allies.get_member(fighter_uuid)
                combat_log.info(f" {fighter} starts their turn")

                # pick action and target
                if fighter.is_player:
                    print()
                    attack, target_uuid = self.get_player_action(fighter, allies, enemies)
                else:
                    # TODO: Implement better NPC AI
                    attack_action_source, attack = r.choice(fighter.actions)
                    target_uuid = r.choice(enemies.valid_targets)
                target = enemies.get_member(target_uuid)

                # Resolve attack
                combat_log.info(f" {fighter.name} uses <{attack.name}> on {target}")
                print()
                print(f(translate("combat.attack"), fighter, attack.display_name, target))

                fighter, target, damage_dealt = Battle.attack(fighter, attack, target)

                combat_log.info(f" {target.name} takes ¤ {damage_dealt} damage -> ♥ {target.health}")
                print(f(translate("combat.damage"), target.name, damage_dealt, target.health))

                # update the fighter and character saved in the Battle instance
                allies.update_member(fighter_uuid, fighter)
                enemies.update_member(target_uuid, target)

                # remove dead characters, check win/loss conditions
                if not target.is_alive:
                    combat_log.info(f" {target.name} dies")
                    print(f(translate("combat.death"), target.name))
                    self.turn_order.remove(target_uuid)

                    if len(self.team1.valid_targets) == 0:
                        combat_log.info(" Battle ends as player loss")
                        print()
                        print(translate("combat.loss"))
                        is_fight_on = False
                        break

                    elif len(self.team2.valid_targets) == 0:
                        combat_log.info(" Battle ends as player victory")
                        print()
                        print(translate("combat.win"))
                        print(f(translate("combat.rewards"), "0", "0"))
                        is_fight_on = False
                        break

                #time.sleep(auto_turn_delay)


    def __repr__(self) -> str:
        return f"{self.team1.name}\n{self.team1}\n\nVS\n\n{self.team2.name}\n{self.team2}"


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
            actions         = [],
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
            actions         = [],
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
