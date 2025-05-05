"""Main game script

Run with CTRL+T (Thonny), currently contains game loop setup, utility labels and
interface tests. If _curses module missing, run pip install windows-curses in
terminal.

Contributors:
    Romain
"""

from __future__ import annotations
import logging
import random
import time
from typing import NamedTuple
from common import *
import cuinter
import world

FPS_COUNTER_REFRESH = 1 # Time between each FPS counter update
MOVE_MAP = {
    ord("w"): (-1, 0, "up"),
    ord("s"): (1, 0, "down"),
    ord("a"): (0, -1, "left"),
    ord("d"): (0, 1, "right"),
}
WORLD_OBJECT_CLASSES = (
    world.GridSprite,
    world.GridMultiSprite,
    world.WorldCharacter,
    world.WalkTrigger,
)

############ Code to run on startup

logger = logging.getLogger(__name__)
logging.basicConfig(
    filename="logs\\main.log",
    filemode="w",
    encoding="utf-8",
    level=logging.DEBUG,
)

last_time = time.time()
fps_timer = last_time  # Time of the last FPS update
frame_count = 0

default_box_dimensions = (
    cuinter.screen_height - 12,
    round(cuinter.screen_width / 4),
    10,
    round(cuinter.screen_width / 2),
)

tiles = load_text_dir("assets\\sprites\\tiles")
tileset = remap_dict(tiles, world.TILE_NAME_TO_CHAR)

world_objects = []
new_events = [
    EnumObject(
        EVENT_TYPES.LOAD_ZONE,
        (
            "assets\\zones\\test_zone.pkl",
            3,
            5,
        ),
    ),
    EnumObject(
        EVENT_TYPES.START_DIALOG,
        "assets\\dialogs\\test_dialog.pkl",
    ),
]

grid = world.Grid.new(tileset)
player = world.WorldCharacter.new(
    grid,
    0,
    0,
    Character("Player", load_text_dir("assets\\sprites\\characters\\player")),
    "down",
    -1,
    0,
)

fps_label = cuinter.Label.new(0, 0)

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
    
    events = cuinter.update()
    events += new_events
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
                
                elif value == ord("m"):
                    try_append(
                        new_events,
                        EnumObject(
                            EVENT_TYPES.PROMPT_CHOICE,
                            "assets\\choices\\menu.pkl",
                        ),
                    )
            
            case EVENT_TYPES.LOAD_ZONE:
                if (not isinstance(value, tuple)
                or len(value) != 3
                or not isinstance(value[0], str)
                or not isinstance(value[1], int)
                or not isinstance(value[2], int)):
                    logger.error(f"Expected value of type tuple[str, int, int], got {value}")
                    continue
                
                world_objects.clear()
                zone_path, player_grid_y, player_grid_x = value
                zone: world.Zone = load_pickle(zone_path)
                grid = grid.load_tilemap(zone.tilemap)
                grid = grid.center(cuinter.screen_height, cuinter.screen_width)
                player = player.config(grid=grid, grid_y=player_grid_y, grid_x=player_grid_x)
                
                for world_object_type, constructor_parameters in zone.world_objects:
                    world_object_class = WORLD_OBJECT_CLASSES[world_object_type]
                    try:
                        new_world_object = world_object_class.new(*constructor_parameters)
                        try_append(world_objects, new_world_object)
                    except AttributeError:
                        logger.error(f"Method not implemented : {world_object_class}.new()")
                    
            case EVENT_TYPES.START_DIALOG:
                if not isinstance(value, str):
                    logger.error(f"Expected value of type str, got {value}")
                    continue
                
                cuinter.DialogBox.new(
                    *default_box_dimensions,
                    DialogLine.process_dialog(load_pickle(value)),
                )
            
            case EVENT_TYPES.PROMPT_CHOICE:
                if not isinstance(value, str):
                    logger.error(f"Expected value of type str, got {value}")
                    continue
                
                options, on_confirm_events = load_pickle(value)
                cuinter.ChoiceBox.new(
                    *default_box_dimensions,
                    translated(options),
                    on_confirm_events,
                )
            
            case EVENT_TYPES.QUIT:
                quit()
            
            case EVENT_TYPES.MULTI_EVENT:
                if (not isinstance(value, tuple)
                or not all(isinstance(element, EnumObject) for element in value)):
                    logger.error(f"Expected value of type tuple[EnumObject], got {value}")
                    continue
                
                for event in value:
                    try_append(new_events, event)
