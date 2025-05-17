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
import random
import time
from typing import NamedTuple
from common import EnumObject, remap_dict, try_append
import cuinter
from cuinter import UI_ELEMENT_CLASSES
from enums import EVENT_TYPES, UI_ELEMENT_TYPES, RECTANGLE_PRESETS
from files import load_text_dir, load_pickle, save_pickle
from game_classes import Character, Item, Stats
from lang import DialogLine, translate
import monsters
from save import Save
import settings
import world
from world import WORLD_OBJECT_CLASSES

FPS_COUNTER_REFRESH = 1 # Time between each FPS counter update
MOVE_MAP = {
    ord("w"): (-1, 0, "up"),
    ord("s"): (1, 0, "down"),
    ord("a"): (0, -1, "left"),
    ord("d"): (0, 1, "right"),
}

TILE_SPRITE_DIR_PATH = "assets\\sprites\\tiles"
MENU_CHOICE_PATH = "assets\\choices\\menu_choice.pkl"

############ Code to run on startup

logging.basicConfig(
    filename="logs\\game.log",
    filemode="w",
    encoding="utf-8",
    level=logging.DEBUG,
    format="%(name)-8s :: %(levelname)-8s :: %(message)s",
)
logger = logging.getLogger(__name__)

last_time = time.time()
fps_timer = last_time  # Time of the last FPS update
frame_count = 0

settings.load()

tiles = load_text_dir(TILE_SPRITE_DIR_PATH)
tileset = remap_dict(tiles, world.TILE_NAME_TO_CHAR)

grid = world.Grid.new(tileset)

nb_save = len(os.listdir("user_data\\game_saves"))
current_save = None

current_zone_path = None
player = world.WorldCharacter.new(
    grid=grid,
    grid_y=0,
    grid_x=0,
    character=monsters.Player(),
    sprite_key="down",
    y_offset=-1,
    x_offset=0,
)

fps_label = cuinter.Label.new(0, 0)

world_objects = []
new_events = [
    EnumObject(
        EVENT_TYPES.LOAD_GAME, current_save
    ),
]
#if settings.get("first_time"):
#    new_events.append(EnumObject(
#        EVENT_TYPES.LOAD_UI_ELEMENT,
#        "assets\\dialogs\\welcome_dialog.pkl",
#    ))

############

while 1:
    ############ Frame calculations
    
    current_time = time.time()
    delta_time = current_time - last_time # Time since last frame
    last_time = current_time
    
    frame_count += 1
    if current_time - fps_timer >= FPS_COUNTER_REFRESH:
        average_fps = frame_count / (current_time - fps_timer)
        fps_label.config(text=f"FPS : {round(average_fps)}")
        fps_timer = current_time
        frame_count = 0
    
    ############ Event handling, code to run every frame
    
    events = new_events + cuinter.update()
    new_events.clear()
    
    for event_type, value in events:
        match event_type:
            case EVENT_TYPES.PRESS_KEY:
                # Key presses only passed to events if they weren't caught by a UI element
                if not isinstance(value, int):
                    logger.error(f"Expected value of type int, got {value}")
                    continue
                
                for world_object in world_objects:
                    if (not isinstance(world_object, world.WalkTrigger)
                    or value != world_object.key):
                        continue
                    
                    try_append(
                        new_events,
                        world_object.on_walk(player.grid_y, player.grid_x),
                    )
                
                if value in MOVE_MAP:
                    old_y, old_x = player.grid_y, player.grid_x
                    move_y, move_x, direction = MOVE_MAP[value]
                    player = player.move(move_y, move_x)
                    
                    if player.grid_multi_sprite.sprite_key != direction:
                        player = player.config(sprite_key=direction)
                    
                    if old_y != player.grid_y or old_x != player.grid_x:
                        for world_object in world_objects:
                            if (not isinstance(world_object, world.WalkTrigger)
                            or world_object.key is not None):
                                continue
                            
                            try_append(
                                new_events,
                                world_object.on_walk(player.grid_y, player.grid_x),
                            )
                    logger.debug(f"Now the position is {(player.grid_x, player.grid_y)}")
                
                elif value == ord("m"):
                    try_append(
                        new_events,
                        EnumObject(
                            EVENT_TYPES.LOAD_UI_ELEMENT,
                            MENU_CHOICE_PATH,
                        ),
                    )
                
            
            case EVENT_TYPES.MAKE_UI_ELEMENT:
                if not isinstance(value, EnumObject):
                    logger.error(f"Expected value of type EnumObject, got {value}")
                    continue
                
                ui_element_type, args = value
                ui_element_class = UI_ELEMENT_CLASSES[ui_element_type]
                
                if isinstance(args, dict):
                    match constructor.enum:
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
            
            case EVENT_TYPES.MAKE_WORLD_OBJECT:
                if not isinstance(value, EnumObject):
                    logger.error(f"Expected value of type EnumObject, got {value}")
                    continue
                
                world_object_type, args = value
                world_object_class = WORLD_OBJECT_CLASSES[world_object_type]
                
                try:
                    if isinstance(args, dict):
                        new_world_object = world_object_class.new(grid=grid, **args)
                    elif isinstance(args, (tuple, list)):
                        new_world_object = world_object_class.new(grid=grid, *args)
                    else:
                        new_world_object = world_object_class.new(grid, args)
                    try_append(world_objects, new_world_object)
                except AttributeError:
                    logger.error(f"Not implemented: {world_object_class}.new()")
            
            case EVENT_TYPES.LOAD_UI_ELEMENT:
                if not isinstance(value, str):
                    logger.error(f"Expected value of type str, got {value}")
                    continue
                
                constructor = load_pickle(value)
                if constructor is None:
                    continue
                elif not isinstance(constructor, EnumObject):
                    logger.error(f"Expected constructor of type EnumObject, got {constructor}")
                    continue
                
                new_event = EnumObject(
                    EVENT_TYPES.MAKE_UI_ELEMENT,
                    constructor,
                )
                try_append(new_events, new_event)
            
            case EVENT_TYPES.LOAD_ZONE:
                if (not isinstance(value, tuple)
                or len(value) != 3
                or not isinstance(value[0], str)
                or not isinstance(value[1], int)
                or not isinstance(value[2], int)):
                    logger.error(f"Expected value of type tuple[str, int, int], got {value}")
                    continue
                
                zone_path, player_grid_y, player_grid_x = value
                zone_data = load_pickle(zone_path)
                logger.debug(f"{zone_path}")
                if zone_data is None:
                    continue
                
                tilemap, world_objects_constructors = zone_data
                
                grid = grid.load_tilemap(tilemap)
                grid = grid.center(cuinter.screen_height, cuinter.screen_width)
                
                current_zone_path = zone_path
                player = player.config(grid=grid, grid_y=player_grid_y, grid_x=player_grid_x)
                
                
                world_objects.clear()
                for constructor in world_objects_constructors:
                    new_event = EnumObject(
                        EVENT_TYPES.MAKE_WORLD_OBJECT,
                        constructor,
                    )
                    try_append(new_events, new_event)
            
            case EVENT_TYPES.LOAD_COMBAT:
                if not isinstance(value, str):
                    logger.error(f"Expected value of type str, got {value}")
                    continue
                
                combat_data = load_pickle(zone_path)
                if combat_data is None:
                    continue
                
                logger.error("Not implemented: EVENT_TYPES.LOAD_COMBAT")
            
            case EVENT_TYPES.CONFIG_SETTINGS:
                if not isinstance(value, dict):
                    logger.error(f"Expected value of type dict, got {value}")
                    continue
                
                settings.config(**value)
            
            case EVENT_TYPES.OPEN_ITEM:
                if not isinstance(value, Item):
                    logger.error(f"Expected value of type Item, got {value}")
                    continue
                
                logger.debug("Opened item")
                logger.error("Not implemented: EVENT_TYPES.OPEN_ITEM")
            
            case EVENT_TYPES.OPEN_EQUIPMENT:
                logger.debug("Opened equipment")
                
                equipment = player.character.inventory.equipment
                options = ()
                for slot_name, equiped_item in equipment.items():
                    slot_entry = translate("equipment_slots." + slot_name) + ": "
                    if equiped_item is None:
                        slot_entry += translate("none")
                    else:
                        slot_entry += equiped_item.display_name
                    options += (slot_entry,)
                    
                options += (translate("menu_back"),)
                
                on_confirm_events = {
                    len(options) - 1: EnumObject(
                        EVENT_TYPES.LOAD_UI_ELEMENT,
                        "assets\\choices\\menu_choice.pkl",
                    ),
                }
                
                cuinter.ChoiceBox.new(
                    options=options,
                    on_confirm_events=on_confirm_events,
                    rectangle_preset=RECTANGLE_PRESETS.MENU,
                )
            
            case EVENT_TYPES.OPEN_BACKPACK:
                logger.debug("Opened backpack")
                
                items = player.character.inventory.backpack.elements()
                options = tuple(item.display_name for item in items)
                options += (translate("menu_back"),)
                on_confirm_events = {
                    len(options) - 1: EnumObject(
                        EVENT_TYPES.LOAD_UI_ELEMENT,
                        "assets\\choices\\menu_choice.pkl",
                    ),
                }
                
                cuinter.ChoiceBox.new(
                    options=options,
                    on_confirm_events=on_confirm_events,
                    rectangle_preset=RECTANGLE_PRESETS.MENU,
                )
            
            case EVENT_TYPES.SAVE_GAME:
                logger.debug("Saved game")
                
                current_save = Save(player.character, (current_zone_path, player.grid_y, player.grid_x))
                save_pickle(current_save, "user_data\\game_saves\\save_1.pkl")
            
            case EVENT_TYPES.LOAD_GAME:
                logger.debug("Loaded game")
                
                if nb_save <= 0:
                    current_save = Save.new(
                        monsters.Player(),
                        (
                            "assets\\zones\\test_zone.pkl",
                            1,
                            2
                        ),
                    )
                    save_pickle(current_save, "user_data\\game_saves\\save_1.pkl")
                    current_zone_path = current_save.worldPosition[0]
                
                current_save = load_pickle("user_data\\game_saves\\save_1.pkl")
                logger.debug(current_save.character.sprite_sheet)
                player = player.config(
                    character=current_save.character,
                    grid_y=current_save.worldPosition[1],
                    grid_x=current_save.worldPosition[2],
                )
                new_event = EnumObject(
                    EVENT_TYPES.LOAD_ZONE,
                    current_save.worldPosition,
                )
                
                try_append(new_events, new_event)
            
            case EVENT_TYPES.QUIT:
                settings.save()
                logger.debug("Quitting")
                quit()
            
            case EVENT_TYPES.MULTI_EVENT:
                if (not isinstance(value, tuple)
                or not all(isinstance(element, EnumObject) for element in value)):
                    logger.error(f"Expected value of type tuple[EnumObject], got {value}")
                    continue
                
                for new_event in value:
                    try_append(new_events, new_event)
