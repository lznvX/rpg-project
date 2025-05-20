"""Combat mechanic prototype.

Handles the core logic for turn-based battles, party management, and interactions
between player and enemy teams.

Docstrings partly written by GitHub Copilot (GPT-4.1),
verified and modified when needed by us.

Created on 2025.03.12
Contributors:
    Jakub
    Romain
"""

from __future__ import annotations
import logging
import random as r
from typing import NamedTuple
from uuid import UUID
from common import EnumObject, try_sleep
from enums import EVENT_TYPES, UI_ELEMENT_TYPES, RECTANGLE_PRESETS
from game_classes import (
    Action,
    Character,
    CharacterNotFoundError,
    DamageInstance,
    Item,
    Party,
)
from lang import DialogLine, f, translate
import monsters as m
import test_items as ti
from get_input import get_input

is_main = __name__ == "__main__"
auto_turn_delay = 0.5 if is_main else 0  # seconds
logger = logging.getLogger(__name__)


class FightOver(RuntimeError):
    """Raised to indicate the battle is over."""
    pass


class CombatParty(NamedTuple):
    """Represents one side in a battle, containing active members and the party leader."""
    name: str
    members: dict[UUID, (Character, bool)]
    leader: UUID

    @staticmethod
    def new(party: Party) -> CombatParty:
        """Construct a CombatParty from a Party object."""
        name = party.name
        leader = party.leader
        members = dict()
        for member in party.members:
            members[member.uuid] = (member, True)

        logger.info(f"Creating CombatParty \"{name}\"")
        logger.debug(f"{name} members:\n\n{members}\n\nleader: {leader}\n")

        return CombatParty(name, members, leader)

    def to_party(self) -> Party:
        """Convert back to a Party, including only alive members."""
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
        """Get a Character by their UUID, or raise if not present."""
        if self.has_member(member_uuid):
            char = self.members[member_uuid][0]
            # logger.debug(f" {self.name} - found member {char}")
            return char
        else:
            raise CharacterNotFoundError(
                f"Cannot find character with UUID {member_uuid} in {self.name}",
            )

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
        # logger.debug(f" {self.name} - collecting valid targets")
        targets = []
        for target_id in self.members.keys():
            if self.get_member(target_id).is_alive:
                targets.append(target_id)
            else:
                continue

        return targets

    def update_member(self, member_uuid, new_member) -> None:
        """Update a member’s Character instance."""
        self.members[member_uuid] = (new_member, self.members[member_uuid][1])

    def __repr__(self):
        """String representation of alive party members."""
        return ", ".join([str(self.get_member(member_uuid)) for member_uuid in self.valid_targets])

    def __str__(self):
        """Alias for __repr__."""
        return repr(self)


class Battle(NamedTuple):
    """Handles the combat between two parties.

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
            raise CharacterNotFoundError(
                f"Cannot find character with UUID {fighter_uuid} in the current battle",
            )

    @staticmethod
    def new(team1: Party, team2: Party) -> Battle:
        """Initialize a new Battle instance.

        Custom constructor to properly initialize the necessary variables.
        Needed because NamedTuple.__init__ can't be modified.
        """
        logger.info(f"Creating a Battle between '{team1.name}' and '{team2.name}'")

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
        """Determine the result of an interaction during combat.

        Returns the attacker, the updated victim, and the damage taken.
        """
        hit = DamageInstance(
            attack.get_damage(weapon, attacker.current),
            attack.damage_type,
            attack.effects,
        )

        victim, damage_taken = victim.hit(hit)

        # returning the attacker too if we ever do thorns damage
        return attacker, victim, damage_taken

    def get_fighter(self, fighter_uuid: UUID) -> Character:
        """Find the relevant character by UUID."""
        # logger.debug(f" Looking for fighter {fighter_uuid}")

        if self.team1.has_member(fighter_uuid):
            return self.team1.get_member(fighter_uuid)
        elif self.team2.has_member(fighter_uuid):
            return self.team2.get_member(fighter_uuid)
        else:
            raise CharacterNotFoundError(
                f"Cannot find character with UUID {fighter_uuid} in the current battle",
            )

    def _sort_turn_order(self):
        """Sort fighters by agility for turn order."""
        sort_key = lambda uuid: self.get_fighter(uuid).current.agility
        logger.debug("Sorting turn order")
        self.turn_order.sort(key=sort_key, reverse=True)
        logger.debug("Turn order sorted")

    def get_player_action(self, player: Character, allies: CombatParty,
                          enemies: CombatParty) -> (Action, UUID):
        """Get the player's choice of action and action target."""
        logger.debug("Getting player input")

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
        logger.debug(f"Player chooses to use <{action.name}>")

        enemies_actual = []
        for enemy in enemies.valid_targets:
            enemies_actual.append(self.get_fighter(enemy))
        list_choices(enemies_actual, f(translate("combat.target_choice"), action))
        enemy_index = get_input(int, True, (1, len(enemies_actual)))
        enemy_uuid = enemies.valid_targets[enemy_index-1]
        logger.debug(
            f"Player chooses to attack {self.get_fighter(enemy_uuid)} ({enemy_uuid})",
        )

        return action, weapon, enemy_uuid

    def begin(self) -> None:
        """Start the battle loop, handling turns until completion."""
        logger.info("Battle started")
        self.output(f"{translate('combat.begin')}\n\n{self}")

        self._sort_turn_order()
        is_fight_on = True
        try_sleep(auto_turn_delay)
        self.new_turn()

        if is_main:
            while is_fight_on:
                try:
                    self.advance(None)
                except FightOver:
                    break
                try_sleep(auto_turn_delay)

    def new_turn(self) -> int:
        """Advance to the next turn, updating state and cleaning up dead fighters."""
        self.progress["turn"] += 1
        self.progress["turn_progress"] = 0
        turn = self.progress["turn"]
        logger.info(f"Turn {turn} started")
        self.output(f(translate("combat.turn"), turn))

        for fighter_uuid in self.turn_order:
            if self.get_fighter(fighter_uuid).is_alive:
                continue
            else:
                self.turn_order.remove(fighter_uuid)

        try_sleep(2*auto_turn_delay)

    def check_win_loss_conditions(self) -> int:
        """Check if one side has lost, returning 1 (win), -1 (loss), or 0 (ongoing)."""
        if len(self.team1.valid_targets) == 0:
            logger.info("Battle ends as player loss")
            self.output(translate("combat.loss"))

            if is_main:
                raise FightOver("The player looses")
            else:
                return -1

        elif len(self.team2.valid_targets) == 0:
            logger.info("Battle ends as player victory")
            output = translate("combat.win")
            output += "\n\n"
            output += f(translate("combat.rewards"), "0", "0")
            self.output(output)

            if is_main:
                raise FightOver("The player wins")
            else:
                return 1
        else:
            return 0

    def advance(self, player_choice: tuple[Action, Item, UUID] = None) -> EnumObject:
        """Advance the battle by one action (player or NPC)."""
        player_action_resolved = False

        while True:
            turn_progress = self.progress["turn_progress"]
            if turn_progress < len(self.turn_order):
                fighter_uuid = self.turn_order[turn_progress]

                allies, enemies = self.get_teams(fighter_uuid)
                fighter = allies.get_member(fighter_uuid)
                if not fighter.is_alive:
                    self.progress["turn_progress"] += 1
                    continue

                logger.info(f"{fighter} starts their turn")

                if fighter.is_player:
                    if player_action_resolved or player_choice is None:
                        if __name__ == "__main__":
                            attack, weapon, target_uuid = self.get_player_action(
                                fighter,
                                allies,
                                enemies
                            )
                        else:
                            target_choice_event = self.get_target_choice_event(enemies)
                            action_choice_event = self.get_action_choice_event(fighter)
                            self.return_dialog.append(target_choice_event)
                            self.return_dialog.append(action_choice_event)
                            dialog_event = self.get_dialog_event()
                            self.return_dialog.clear()
                            return dialog_event

                    else:
                        attack, weapon, target_uuid = player_choice
                        player_action_resolved = True

                else:
                    attack_action_source, attack = r.choice(fighter.actions)
                    target_uuid = r.choice(enemies.valid_targets)
                    weapon = fighter.inventory.find_equipped_item(attack_action_source)

                target = enemies.get_member(target_uuid)

                logger.info(f"{fighter.name} uses <{attack.name}> on {target}")
                output = f(translate("combat.attack"), fighter, attack.display_name, target)

                fighter, target, damage_dealt = Battle.attack(fighter, weapon, attack, target)

                if fighter.is_player:
                    self.return_dialog.append(EnumObject(
                        EVENT_TYPES.SET_CHARACTER,
                        fighter,
                    ))
                elif target.is_player:
                    self.return_dialog.append(EnumObject(
                        EVENT_TYPES.SET_CHARACTER,
                        target,
                    ))

                logger.info(
                    f"{target.name} takes ¤ {damage_dealt} damage -> ♥ {target.health}",
                )
                output += "\n\n"
                output += f(
                    translate("combat.damage"),
                    target.display_name,
                    damage_dealt,
                    target.health,
                )
                

                allies.update_member(fighter_uuid, fighter)
                enemies.update_member(target_uuid, target)

                if not target.is_alive:
                    logger.info(f"{target.name} dies")
                    output += "\n\n"
                    output += f(translate("combat.death"), target.display_name)

                    match self.check_win_loss_conditions():
                        case 0:
                            pass
                        case 1:
                            dialog_event = self.get_dialog_event()
                            self.return_dialog.clear()
                            return dialog_event
                        case -1:
                            self.return_dialog.append(EnumObject(
                                EVENT_TYPES.GAME_OVER,
                            ))
                            dialog_event = self.get_dialog_event()
                            self.return_dialog.clear()
                            return dialog_event
                        case _:
                            raise NotImplementedError("How did we get here?")

                self.output(output)
                self.progress["turn_progress"] += 1
            else:
                self.new_turn()
                continue

    def get_target_choice_event(self, enemies: CombatParty) -> EnumObject:
        """Construct an event for the player to choose an enemy target."""
        options = ()
        on_confirm_events = {}

        for enemy_uuid in enemies.valid_targets:
            options += (self.get_fighter(enemy_uuid).__repr__(),)
            on_confirm_events[len(options) - 1] = EnumObject(
                EVENT_TYPES.SET_BATTLE_TARGET,
                enemy_uuid,
            )

        choice_constructor = EnumObject(
            UI_ELEMENT_TYPES.CHOICE_BOX,
            {
                "options": options,
                "on_confirm_events": on_confirm_events,
                "rectangle_preset": RECTANGLE_PRESETS.MENU,
            },
        )
        return EnumObject(
            EVENT_TYPES.MAKE_UI_ELEMENT,
            choice_constructor,
        )

    def get_action_choice_event(self, fighter: Character) -> EnumObject:
        """Construct an event for the player to choose an action."""
        options = ()
        on_confirm_events = {}

        for weapon_uuid, action in fighter.actions:
            weapon = fighter.inventory.find_equipped_item(weapon_uuid)
            options += (action.display(weapon, fighter.current),)
            on_confirm_events[len(options) - 1] = EnumObject(
                EVENT_TYPES.SET_BATTLE_ACTION,
                (action, weapon),
            )

        choice_constructor = EnumObject(
            UI_ELEMENT_TYPES.CHOICE_BOX,
            {
                "options": options,
                "on_confirm_events": on_confirm_events,
                "rectangle_preset": RECTANGLE_PRESETS.MENU,
            },
        )
        return EnumObject(
            EVENT_TYPES.MAKE_UI_ELEMENT,
            choice_constructor,
        )

    def get_dialog_event(self) -> EnumObject:
        """Construct a dialog event from buffered lines."""
        return_dialog = tuple(self.return_dialog)
        dialog_constructor = EnumObject(
            UI_ELEMENT_TYPES.DIALOG_BOX,
            {
                "dialog": return_dialog,
                "rectangle_preset": RECTANGLE_PRESETS.MENU,
            },
        )
        return EnumObject(
            EVENT_TYPES.MAKE_UI_ELEMENT,
            dialog_constructor,
        )

    def output(self, text: str) -> None:
        """Output a message to the screen or dialog buffer, depending on context."""
        if is_main:
            print("\n" + text)
        else:
            self.return_dialog.append(DialogLine(text))

    def __repr__(self) -> str:
        """String representation of the current battle state."""
        return f"{self.team1.name}\n{self.team1}\n\nVS\n\n{self.team2.name}\n{self.team2}"


def list_choices(choices: list | tuple, text: str = "", start_from_1: bool = True,
                 template: str = "{}) {}") -> None:
    """Utility function to print a numbered list of choices."""
    print(text)
    for i, choice in enumerate(choices):
        if choice is None:
            continue
        print(template.format(i + start_from_1, choice))


def _test_pcs():
    """Test function to generate sample player characters for debugging."""
    alice = Character.new(
        name="Alice",
        sprite_sheet=None,
        is_player=False,
        base_stats=m.DefaultStats.human,
        actions=[],
        initial_effects={}
    )
    alice.inventory.add(ti.Sword)
    alice.inventory.add(ti.AgiBoots)
    alice = alice.equip("mainhand", ti.Sword)
    alice = alice.equip("feet", ti.AgiBoots)

    logger.debug(f"Alice's equipment:\n\n{alice.inventory._get_equipment_dump()}\n")

    bob = Character.new(
        name="Bob",
        sprite_sheet=None,
        is_player=True,
        base_stats=m.DefaultStats.human,
        actions=[],
        initial_effects={}
    )
    bob.inventory.add(ti.Sword)
    bob.inventory.add(ti.Dagger)
    bob.inventory.add(ti.StrHelmet)
    bob = bob.equip("mainhand", ti.Sword)
    bob = bob.equip("offhand", ti.Dagger)
    bob = bob.equip("head", ti.StrHelmet)

    logger.debug(f"Bob's equipment:\n\n{bob.inventory._get_equipment_dump()}\n")

    return alice, bob


if is_main:
    logging.basicConfig(filename='logs/combat_test.log', filemode='wt', encoding='utf-8', level=logging.DEBUG,
    format="%(name)-9s :: %(levelname)-8s :: %(message)s", force=True)

    alice, bob = _test_pcs()
    player_party = Party("Adventuring Party", [alice, bob], bob.uuid)

    gg_leader = m.hobgoblin()
    goblin_gang = Party(
        "Goblin Gang",
        [
            gg_leader,
            m.goblin(),
            m.goblin(),
            m.goblin(),
            m.goblin(),
        ],
        gg_leader.uuid,
    )

    current_battle = Battle.new(player_party, goblin_gang)
    current_battle.begin()
