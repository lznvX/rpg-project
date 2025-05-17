"""combat mechanic prototype

Created on 2025.03.12
Contributors:
    Jakub
    Romain (just did implementation with the rest)
"""


from __future__ import annotations
import logging
import random as r
from typing import NamedTuple
from uuid import UUID
from common import EnumObject, try_sleep
from enums import EVENT_TYPES, UI_ELEMENT_TYPES, RECTANGLE_PRESETS
from game_classes import Stats, DamageInstance, Character, Action, Party, Item, CharacterNotFoundError
from lang import DialogLine, f, translate
import monsters as m
import test_items as ti

combat_log = logging.getLogger(__name__)
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

        combat_log.info(f"Creating CombatParty \"{name}\"")
        combat_log.debug(f"{name} members:\n\n{members}\n\nleader: {leader}\n")

        return CombatParty(name, members, leader)


    def to_party(self) -> Party:
        name = self.name
        leader = self.leader

        members = []
        for character, is_alive in self.members.values():
            if is_alive:
                members.append(character)
            else:
                continue

        return Party(name, tuple(members), leader)


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
    progress: dict[str, int]

    return_dialog: list[str | DialogLine | EnumObject]


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
        combat_log.info(f"Creating a Battle between '{team1.name}' and '{team2.name}'")

        combat_team1 = CombatParty.new(team1)
        combat_team2 = CombatParty.new(team2)

        targets1 = combat_team1.valid_targets
        targets2 = combat_team2.valid_targets

        # doesn't need to be sorted until the battle begins
        turn_order = targets1 + targets2

        progress = {
            "turn": 0,
            "turn_progress": 0,
            }

        return Battle(
            team1=combat_team1,
            team2=combat_team2,
            turn_order=turn_order,
            progress=progress,
            return_dialog=[],
        )


    @staticmethod
    def attack(attacker: Character, weapon: Item, attack: Action, victim: Character
               ) -> (Character, Character, int):
        """Determine the result of an interaction during combat."""

        # combat_log.debug(f" {attack.get_damage}")
        # combat_log.debug(f" {attack.get_damage(weapon, attacker.current)}, {attack.damage_type}, {attack.effects}")

        hit = DamageInstance(attack.get_damage(weapon, attacker.current), attack.damage_type, attack.effects)

        victim, damage_taken = victim.hit(hit)

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
        combat_log.debug("Sorting turn order")
        self.turn_order.sort(key=sort_key, reverse=True)
        combat_log.debug("Turn order sorted")


    def get_player_action(self, player: Character, allies: CombatParty,
                          enemies: CombatParty) -> (Action, UUID):
        """Get the player's choice of action and action target."""
        combat_log.debug("Getting player input")

        print()

        # U G L Y
        action_names = []
        for action in player.actions:
            weapon = player.inventory.find_equipped_item(action[0])
            action_names.append(action[1].display(weapon, player.current))
        list_choices(action_names, translate("combat.action_choice").format(player.name))
        action_index = get_input(int, True, (1, len(player.actions)))
        action = player.actions[action_index-1][1]
        weapon = player.inventory.find_equipped_item(player.actions[action_index-1][0])
        combat_log.debug(f"Player chooses to use <{action.name}>")

        enemies_actual = []
        for enemy in enemies.valid_targets:
            enemies_actual.append(self.get_fighter(enemy))
        list_choices(enemies_actual, f(translate("combat.target_choice"), action))
        enemy_index = get_input(int, True, (1, len(enemies_actual)))
        enemy_uuid = enemies.valid_targets[enemy_index-1]
        combat_log.debug(f"Player chooses to attack {self.get_fighter(enemy_uuid)} ({enemy_uuid})")

        return action, weapon, enemy_uuid


    def begin(self) -> None:
        combat_log.info("Battle started")
        self.output(f"{translate('combat.begin')}\n\n{self}")

        self._sort_turn_order()
        is_fight_on = True
        try_sleep(auto_turn_delay)
        self.new_turn()

        # is this allowed? no prob for me, dunno if Kessler will get angry
        if is_main:
            while is_fight_on:
                self.advance(None)
                # why is the delay broken? was commented out
                try_sleep(auto_turn_delay)


    def new_turn(self) -> int:
        self.progress["turn"] += 1
        self.progress["turn_progress"] = 0
        turn = self.progress["turn"]
        combat_log.info(f"Turn {turn} started")
        self.output(f(translate("combat.turn"), turn))

        for fighter_uuid in self.turn_order:
            if self.get_fighter(fighter_uuid).is_alive:
                continue
            else:
                self.turn_order.remove(fighter_uuid)

        try_sleep(2*auto_turn_delay)


    def check_win_loss_conditions(self) -> int:
        if len(self.team1.valid_targets) == 0:
            combat_log.info("Battle ends as player loss")
            self.output(translate("combat.loss"))
            is_fight_on = False
            return -1
        elif len(self.team2.valid_targets) == 0:
            combat_log.info("Battle ends as player victory")
            combat_win = translate("combat.win")
            combat_rewards = f(translate("combat.rewards"), "0", "0")
            self.output(f"{translate('combat.begin')}\n\n{self}")
            is_fight_on = False
            return 1
        else:
            return 0


    def advance(self, player_choice: tuple[Action, Item, UUID] = None) -> EnumObject:
        player_action_resolved = False

        while True:
            turn_progress = self.progress["turn_progress"]
            if turn_progress < len(self.turn_order):
                # Setup stuff
                fighter_uuid = self.turn_order[turn_progress]

                allies, enemies = self.get_teams(fighter_uuid)
                fighter = allies.get_member(fighter_uuid)
                if not fighter.is_alive:
                    # needed because turn_order is only cleaned at the end of a turn
                    self.progress["turn_progress"] += 1
                    continue

                combat_log.info(f"{fighter} starts their turn")

                if fighter.is_player:
                    # TODO: Handle player
                    # pretty sure multiple PCs are supported

                    # player_action_resolved dictates whether the data in...
                    # player_choice is for this turn or the previous one
                    if player_action_resolved or player_choice is None:
                        if __name__ == "__main__":
                            attack, weapon, target_uuid = self.get_player_action(fighter, allies, enemies)
                        else:
                            # HAHAHA  U G L I E R
                            target_options = ()
                            target_on_confirm_events = {}

                            for enemy_uuid in enemies.valid_targets:
                                target_options += (self.get_fighter(enemy_uuid).__repr__(),)
                                target_on_confirm_events[len(target_options) - 1] = EnumObject(
                                    EVENT_TYPES.SET_BATTLE_TARGET,
                                    enemy_uuid,
                                )

                            target_choice_constructor = EnumObject(
                                UI_ELEMENT_TYPES.CHOICE_BOX,
                                {
                                    "options": target_options,
                                    "on_confirm_events": target_on_confirm_events,
                                    "rectangle_preset": RECTANGLE_PRESETS.MENU,
                                },
                            )
                            target_choice_event = EnumObject(
                                EVENT_TYPES.MAKE_UI_ELEMENT,
                                target_choice_constructor,
                            )

                            action_options = ()
                            action_on_confirm_events = {}

                            for weapon_uuid, action in fighter.actions:
                                weapon = fighter.inventory.find_equipped_item(weapon_uuid)
                                action_options += (action.display(weapon, fighter.current),)
                                action_on_confirm_events[len(action_options) - 1] = EnumObject(
                                    EVENT_TYPES.SET_BATTLE_ACTION,
                                    (action, weapon),
                                )

                            action_choice_constructor = EnumObject(
                                UI_ELEMENT_TYPES.CHOICE_BOX,
                                {
                                    "options": action_options,
                                    "on_confirm_events": action_on_confirm_events,
                                    "rectangle_preset": RECTANGLE_PRESETS.MENU,
                                },
                            )
                            action_choice_event = EnumObject(
                                EVENT_TYPES.MAKE_UI_ELEMENT,
                                action_choice_constructor,
                            )

                            self.return_dialog.append(target_choice_event)
                            self.return_dialog.append(action_choice_event)
                            return_dialog = tuple(self.return_dialog)
                            self.return_dialog.clear()

                            dialog_constructor = EnumObject(
                                UI_ELEMENT_TYPES.DIALOG_BOX,
                                {
                                    "dialog": return_dialog,
                                    "rectangle_preset": RECTANGLE_PRESETS.MENU,
                                },
                            )
                            dialog_event = EnumObject(
                                EVENT_TYPES.MAKE_UI_ELEMENT,
                                dialog_constructor,
                            )

                            return dialog_event

                    else:
                        attack, weapon, target_uuid = player_choice
                        player_action_resolved = True

                else:
                    # Handle NPCs
                    # TODO: Implement better NPC AI
                    attack_action_source, attack = r.choice(fighter.actions)
                    target_uuid = r.choice(enemies.valid_targets)
                    weapon = fighter.inventory.find_equipped_item(attack_action_source)

                target = enemies.get_member(target_uuid)

                # Resolve attack
                combat_log.info(f"{fighter.name} uses <{attack.name}> on {target}")
                self.output(f(translate("combat.attack"), fighter, attack.display_name, target))

                fighter, target, damage_dealt = Battle.attack(fighter, weapon, attack, target)

                combat_log.info(f"{target.name} takes ¤ {damage_dealt} damage -> ♥ {target.health}")
                self.output(f(translate("combat.damage"), target.display_name, damage_dealt, target.health))

                # update the fighter and character saved in the Battle instance
                allies.update_member(fighter_uuid, fighter)
                enemies.update_member(target_uuid, target)

                # remove dead characters, check win/loss conditions
                if not target.is_alive:
                    combat_log.info(f"{target.name} dies")
                    self.output(f(translate("combat.death"), target.display_name))
                    # self.turn_order.remove(target_uuid)

                    match self.check_win_loss_conditions():
                        case 0:
                            # nothing happens
                            pass
                        case 1:
                            updated_party = self.team1.to_party()
                            raise NotImplementedError("Tell Mr Frontend that we won :)")
                        case -1:
                            raise NotImplementedError("Tell Mr Frontend that we lost :(")
                        case _:
                            raise NotImplementedError("How did we get here?")



                self.progress["turn_progress"] += 1
            else:
                self.new_turn()
                continue


    def output(self, text: str) -> None:
        if is_main:
            print("\n" + text)
        else:
            self.return_dialog.append(text)


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
    bob.inventory.add(ti.Dagger)
    bob.inventory.add(ti.StrHelmet)
    bob = bob.equip("mainhand", ti.Sword)
    bob = bob.equip("mainhand", ti.Dagger)
    bob = bob.equip("head", ti.StrHelmet)

    return alice, bob


is_main = __name__ == "__main__"
auto_turn_delay = 0.5 if is_main else 0 # seconds
if is_main:
    alice, bob = _test_pcs()
    player_party = Party("Adventuring Party", [alice, bob], bob.uuid)


    gg_leader = m.Hobgoblin()
    goblin_gang = Party("Goblin Gang", [gg_leader, m.Goblin(), m.Goblin(), m.Goblin(), m.Goblin()], gg_leader.uuid)


    current_battle = Battle.new(player_party, goblin_gang)

    current_battle.begin()
