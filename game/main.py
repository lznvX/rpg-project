"""Main game script

Run with CTRL+T (Thonny), currently contains game loop setup, utility labels and
interface tests. If _curses module missing, run pip install windows-curses in
terminal.

Contributors:
    Romain
    Adrien
"""

from __future__ import annotations
import logging
import os
import time
from typing import Callable, NamedTuple
from uuid import UUID
from combat import Battle
from common import EnumObject, remap_dict, try_append
import cuinter
from cuinter import UI_ELEMENT_CLASSES
from enums import EVENT_TYPES, UI_ELEMENT_TYPES, RECTANGLE_PRESETS
from files import load_text_dir, load_pickle, save_pickle
from game_classes import Action, Character, DamageInstance, Item, Party
from game_save import DEFAULT_ZONE_PATH, GameSave
from lang import DialogLine, translate
import monsters
import settings
import world
from world import WORLD_OBJECT_CLASSES

logging.basicConfig(
    filename="logs\\game.log",
    filemode="w",
    encoding="utf-8",
    level=logging.DEBUG,
    format="%(name)-12s :: %(levelname)-8s :: %(message)s",
)
logger = logging.getLogger(__name__)

FPS_COUNTER_REFRESH = 1 # Time between each HUD counter update
MOVE_MAP = {
    ord("w"): (-1, 0, "up"),
    ord("s"): (1, 0, "down"),
    ord("a"): (0, -1, "left"),
    ord("d"): (0, 1, "right"),
}

GAME_SAVE_PATH = "user_data\\game_saves\\save_1.pkl"
TILE_SPRITE_DIR_PATH = "assets\\sprites\\tiles"
MENU_CHOICE_PATH = "assets\\choices\\menu_choice.pkl"


class Globals(NamedTuple):
    grid: world.Grid
    player: world.WorldCharacter
    health_label: cuinter.Label
    zone_path: str
    battle: Battle
    battle_action: tuple[Action, Item]
    battle_target: UUID

    @classmethod
    def new(cls) -> Globals:
        tile_sprites = load_text_dir(TILE_SPRITE_DIR_PATH)
        tileset = remap_dict(tile_sprites, world.TILE_NAME_TO_CHAR)

        grid = world.Grid.new(tileset)
        player = world.WorldCharacter.new(
            grid=grid,
            grid_y=0,
            grid_x=0,
            character=monsters.player(),
            sprite_key="down",
            y_offset=-1,
            x_offset=0,
        )
        health_label = cuinter.Label.new(
            y=1,
            x=0,
            text=f"♥ {player.character.health}/{player.character.current.max_health}"
        )

        return cls(
            grid=grid,
            player=player,
            health_label=health_label,
            zone_path=DEFAULT_ZONE_PATH,
            battle=None,
            battle_action=None,
            battle_target=None,
        )


def _make_globals_manager() -> tuple[Callable, ...]:
    # I mean it's not the global keyword right ?
    cache = Globals.new()

    def get_cache() -> Globals:
        return cache

    def config_cache(**kwargs) -> None:
        nonlocal cache
        cache = cache._replace(**kwargs)

    return get_cache, config_cache


def _make_world_object_manager() -> tuple[Callable, ...]:
    cache = []

    def get_cache() -> list[object]:
        return cache

    def add_item(world_object: object) -> None:
        if world_object is None:
            return

        logger.debug(f"Adding world object: {world_object}")
        nonlocal cache
        cache.append(world_object)

    def clear_cache() -> None:
        logger.debug("Clearing world objects")
        nonlocal cache
        cache.clear()

    return get_cache, add_item, clear_cache


def _make_event_manager() -> tuple[Callable, ...]:
    cache = []

    def get_cache() -> list[EnumObject]:
        return cache

    def add_item(event: EnumObject) -> None:
        if event is None:
            return

        nonlocal cache
        cache.append(event)

    def clear_cache() -> None:
        nonlocal cache
        cache.clear()

    return get_cache, add_item, clear_cache


def press_key(key: int) -> None:
    player = get_globals().player

    for world_object in get_world_objects():
        if (
            not isinstance(world_object, world.WalkTrigger)
            or key != world_object.key
        ):
            continue

        add_event(world_object.on_walk(player.grid_y, player.grid_x))

    if key in MOVE_MAP:
        old_y, old_x = player.grid_y, player.grid_x
        move_y, move_x, direction = MOVE_MAP[key]
        player = player.move(move_y, move_x)

        if player.grid_multi_sprite.sprite_key != direction:
            player = player.config(sprite_key=direction)

        if old_y != player.grid_y or old_x != player.grid_x:
            for world_object in get_world_objects():
                if (
                    not isinstance(world_object, world.WalkTrigger)
                    or world_object.key is not None
                ):
                    continue

                add_event(world_object.on_walk(player.grid_y, player.grid_x))

    elif key == ord("m"):
        load_ui_element(MENU_CHOICE_PATH)

    config_globals(player=player)


def make_ui_element(constructor: EnumObject) -> None:
    ui_element_type, args = constructor
    ui_element_class = UI_ELEMENT_CLASSES[ui_element_type]

    if isinstance(args, dict):
        match ui_element_type:
            case UI_ELEMENT_TYPES.DIALOG_BOX:
                if "dialog" in args:
                    args["dialog"] = DialogLine.process_dialog(args["dialog"])
            case UI_ELEMENT_TYPES.CHOICE_BOX:
                if "options" in args:
                    args["options"] = translate(args["options"])

    try:
        if isinstance(args, dict):
            ui_element_class.new(**args)
        elif isinstance(args, (tuple, list)):
            ui_element_class.new(*args)
        else:
            ui_element_class.new(args)
    except AttributeError:
        logger.error(f"Not implemented: {ui_element_class}.new()")


def make_world_object(constructor: EnumObject) -> None:
    world_object_type, args = constructor
    world_object_class = WORLD_OBJECT_CLASSES[world_object_type]
    grid = get_globals().grid

    try:
        if isinstance(args, dict):
            world_object = world_object_class.new(grid=grid, **args)
        elif isinstance(args, (tuple, list)):
            world_object = world_object_class.new(grid=grid, *args)
        else:
            world_object = world_object_class.new(grid, args)
        add_world_object(world_object)
    except AttributeError:
        logger.error(f"Not implemented: {world_object_class}.new()")


def load_ui_element(ui_element_path: str) -> None:
    constructor = load_pickle(ui_element_path)
    make_ui_element(constructor)


def load_zone(zone_path: str, player_grid_y: int = 0, player_grid_x: int = 0) -> None:
    zone_data = load_pickle(zone_path)
    tilemap, world_object_constructors = zone_data
    
    grid = get_globals().grid
    grid = grid.load_tilemap(tilemap)
    grid = grid.center(cuinter.get_screen_height(), cuinter.get_screen_width())

    player = get_globals().player
    player = player.config(
        grid=grid,
        grid_y=player_grid_y,
        grid_x=player_grid_x,
    )

    config_globals(
        grid=grid,
        player=player,
        zone_path=zone_path,
    )

    clear_world_objects()
    for constructor in world_object_constructors:
        make_world_object(constructor)


def load_battle(battle_path: str) -> None:
    # Should load battle data and plug into Battle.new(), but no time
    player = get_globals().player

    leader = monsters.hobgoblin()
    battle = Battle.new(
        Party(
            name="Player party",
            members=(player.character,),
            leader=player.character.uuid,
        ),
        Party(
            name="Goblin squad",
            members=(
                leader,
                monsters.goblin(),
                monsters.goblin(),
            ),
            leader=leader.uuid,
        ),
    )

    battle.begin()
    add_event(battle.advance())

    config_globals(battle=battle)


def game_over() -> None:
    # TODO Implement game_over()
    logger.error("Not implemented: game_over()")


def set_battle_action(attack: Action, weapon: Item) -> None:
    battle = get_globals().battle
    battle_target = get_globals().battle_target

    if battle_target is not None:
        add_event(battle.advance((
            attack,
            weapon,
            battle_target,
        )))
        config_globals(battle_target=None)
    else:
        config_globals(battle_action=(attack, weapon))


def set_battle_target(target_uuid: UUID) -> None:
    battle = get_globals().battle
    battle_action = get_globals().battle_action

    if battle_action is not None:
        add_event(battle.advance((
            *battle_action,
            target_uuid,
        )))
        config_globals(battle_action=None)
    else:
        config_globals(battle_target=target_uuid)


def set_character(character: Character) -> None:
    player = get_globals().player
    player = player.config(
        character=character,
    )

    health_label = get_globals().health_label
    health_label = health_label.config(
        text=f"♥ {character.health}/{character.current.max_health}",
    )

    config_globals(
        player=player,
        health_label=health_label,
    )


def equip_item(slot: str, item: Item) -> None:
    set_character(get_globals().player.character.equip(slot, item))


def unequip_item(slot: str) -> None:
    set_character(get_globals().player.character.unequip(slot))


def add_item(item: Item, count: int = 1) -> None:
    get_globals().player.character.inventory.add(item, count)


def remove_item(item: Item, count: int = 1) -> None:
    get_globals().player.character.inventory.remove(item, count)


def use_item(item: Item) -> None:
    # Should be in the item's actions, but no time
    logger.debug(f"Using item: {item}")

    player = get_globals().player

    match item.name:
        case "potion_health":
            if player.character.inventory.backpack[item] < 1:
                logger.error(f"Not enough {item.name} to use")
                return 

            remove_item(item)
            updated_character, damage_taken = player.character.hit(
                DamageInstance(
                    damage=-5,
                    damage_type="true",
                    effects={},
                ),
            )

            set_character(updated_character)


def open_item(item: Item) -> None:
    logger.debug(f"Opening item: {item}")

    inventory = get_globals().player.character.inventory

    options = ()
    on_confirm_events = {}

    if "equippable" in item.tags:
        for slot in inventory.slots:
            if slot not in item.tags:
                continue
            if (
                inventory.equipment[slot] is not None
                and item.name == inventory.equipment[slot].name
            ):
                equip_entry = translate("item_unequip")
                on_confirm_event = EnumObject(
                    EVENT_TYPES.UNEQUIP_ITEM,
                    slot,
                )
            else:
                for it, count in inventory.backpack.items():
                    if it.name != item.name or count < 1:
                        continue
                    equip_entry = translate("item_equip")
                    on_confirm_event = EnumObject(
                        EVENT_TYPES.EQUIP_ITEM,
                        (
                            slot,
                            it,
                        ),
                    )
                    break
                else:
                    continue

            equip_entry += f" {item.display_name}"
            equip_entry += f": {translate('equipment_slots.' + slot)}"
            options += (equip_entry,)
            on_confirm_events[len(options) - 1] = EnumObject(
                EVENT_TYPES.MULTI_EVENT,
                (
                    on_confirm_event,
                    EnumObject(
                        EVENT_TYPES.OPEN_ITEM,
                        item,
                    ),
                ),
            )

    elif "consumable" in item.tags:
        if inventory.backpack[item] > 1:
            on_use_event = EnumObject(
                EVENT_TYPES.OPEN_ITEM,
                item,
            )
        else:
            on_use_event = EnumObject(
                EVENT_TYPES.OPEN_BACKPACK,
            )
        use_entry = f"{translate('item_use')}"
        use_entry += f" {item.display_name}"
        use_entry += f" ({inventory.backpack[item]})"
        options += (use_entry,)
        on_confirm_events[len(options) - 1] = EnumObject(
            EVENT_TYPES.MULTI_EVENT,
            (
                EnumObject(
                    EVENT_TYPES.USE_ITEM,
                    item,
                ),
                on_use_event,
            ),
        )

    options += (translate("menu.back"),)
    on_confirm_events[len(options) - 1] = EnumObject(
        EVENT_TYPES.OPEN_BACKPACK,
    )

    cuinter.ChoiceBox.new(
        options=options,
        on_confirm_events=on_confirm_events,
        rectangle_preset=RECTANGLE_PRESETS.MENU,
    )


def open_equipment() -> None:
    logger.debug("Opening equipment")

    slot_items = get_globals().player.character.inventory.equipment.items()
    options = ()
    on_confirm_events = {}

    for i, (slot, item) in enumerate(slot_items):
        slot_entry = translate("equipment_slots." + slot) + ": "
        if item is None:
            slot_entry += translate("equipment_none")
            on_confirm_events[i] = EnumObject(
                EVENT_TYPES.OPEN_BACKPACK,
            )
        else:
            slot_entry += item.display_name
            on_confirm_events[i] = EnumObject(
                EVENT_TYPES.OPEN_ITEM,
                item,
            )
        options += (slot_entry,)

    options += (translate("menu.back"),)
    on_confirm_events[len(options) - 1] = EnumObject(
        EVENT_TYPES.LOAD_UI_ELEMENT,
        "assets\\choices\\menu_choice.pkl",
    )

    cuinter.ChoiceBox.new(
        options=options,
        on_confirm_events=on_confirm_events,
        rectangle_preset=RECTANGLE_PRESETS.MENU,
    )


def open_backpack() -> None:
    logger.debug("Opening backpack")

    item_counts = sorted(get_globals().player.character.inventory.backpack.items())
    options = ()
    on_confirm_events = {}

    for i, (item, count) in enumerate(item_counts):
        item_entry = item.display_name
        if count > 1:
            item_entry += f" ({count})"
        options += (item_entry,)
        on_confirm_events[i] = EnumObject(
            EVENT_TYPES.OPEN_ITEM,
            item,
        )

    options += (translate("menu.back"),)
    on_confirm_events[len(options) - 1] = EnumObject(
        EVENT_TYPES.LOAD_UI_ELEMENT,
        "assets\\choices\\menu_choice.pkl",
    )

    cuinter.ChoiceBox.new(
        options=options,
        on_confirm_events=on_confirm_events,
        rectangle_preset=RECTANGLE_PRESETS.MENU,
    )


def config_settings(**kwargs) -> None:
    settings.config(**kwargs)


def save_game() -> None:
    logger.debug("Saving game")

    player = get_globals().player
    zone_path = get_globals().zone_path

    game_save = GameSave(
        player.character,
        zone_path,
        player.grid_y,
        player.grid_x,
    )

    save_pickle(game_save, GAME_SAVE_PATH)


def load_game() -> None:
    logger.debug("Loading game")

    if os.path.exists(GAME_SAVE_PATH):
        game_save = load_pickle(GAME_SAVE_PATH)
    else:
        game_save = GameSave.new()

    set_character(game_save.character)
    load_zone(
        game_save.zone_path,
        game_save.player_grid_y,
        game_save.player_grid_x,
    )


def quit_game() -> None:
    logger.debug("Quitting game")
    settings.save()
    cuinter.fullscreen()
    quit()


def multi_event(*args: EnumObject) -> None:
    for event in args:
        add_event(event)


def main() -> None:
    settings.load()

    cuinter.setup()

    add_event(EnumObject(
        EVENT_TYPES.LOAD_GAME,
    ))
    if settings.get().first_time:
        add_event(EnumObject(
            EVENT_TYPES.LOAD_UI_ELEMENT,
            "assets\\dialogs\\welcome_dialog.pkl",
        ))

    fps_label = cuinter.Label.new(
        y=0,
        x=0,
        text="FPS:"
    )
    last_time = time.time()
    fps_timer = last_time  # Time of the last FPS update
    frame_count = 0

    while True:
        current_time = time.time()
        delta_time = current_time - last_time # Time since last frame
        last_time = current_time

        frame_count += 1
        if current_time - fps_timer >= FPS_COUNTER_REFRESH:
            average_fps = frame_count / (current_time - fps_timer)
            fps_label.config(text=f"FPS: {round(average_fps)}")
            fps_timer = current_time
            frame_count = 0

        events = get_events() + cuinter.update()
        clear_events()

        for event_type, event_value in events:
            event_function = EVENT_FUNCTIONS[event_type]
            if isinstance(event_value, dict):
                event_function(**event_value)
            elif (
                not hasattr(event_value, '_fields')
                and isinstance(event_value, (tuple, list))
            ):
                event_function(*event_value)
            elif event_value is not None:
                event_function(event_value)
            else:
                event_function()


EVENT_FUNCTIONS = {
    EVENT_TYPES.PRESS_KEY: press_key,
    EVENT_TYPES.MAKE_UI_ELEMENT: make_ui_element,
    EVENT_TYPES.MAKE_WORLD_OBJECT: make_world_object,
    EVENT_TYPES.LOAD_UI_ELEMENT: load_ui_element,
    EVENT_TYPES.LOAD_ZONE: load_zone,
    EVENT_TYPES.LOAD_BATTLE: load_battle,
    EVENT_TYPES.GAME_OVER: game_over,
    EVENT_TYPES.SET_BATTLE_ACTION: set_battle_action,
    EVENT_TYPES.SET_BATTLE_TARGET: set_battle_target,
    EVENT_TYPES.SET_CHARACTER: set_character,
    EVENT_TYPES.EQUIP_ITEM: equip_item,
    EVENT_TYPES.UNEQUIP_ITEM: unequip_item,
    EVENT_TYPES.ADD_ITEM: add_item,
    EVENT_TYPES.REMOVE_ITEM: remove_item,
    EVENT_TYPES.USE_ITEM: use_item,
    EVENT_TYPES.OPEN_ITEM: open_item,
    EVENT_TYPES.OPEN_EQUIPMENT: open_equipment,
    EVENT_TYPES.OPEN_BACKPACK: open_backpack,
    EVENT_TYPES.CONFIG_SETTINGS: config_settings,
    EVENT_TYPES.SAVE_GAME: save_game,
    EVENT_TYPES.LOAD_GAME: load_game,
    EVENT_TYPES.QUIT_GAME: quit_game,
    EVENT_TYPES.MULTI_EVENT: multi_event,
}

(
    get_globals,
    config_globals,
) = _make_globals_manager()
(
    get_world_objects,
    add_world_object,
    clear_world_objects,
) = _make_world_object_manager()
(
    get_events,
    add_event,
    clear_events,
) = _make_event_manager()

if __name__ == "__main__":
    main()
