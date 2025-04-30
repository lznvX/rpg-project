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

############ Code to run on startup

logger = logging.getLogger(__name__)
logging.basicConfig(filename="logs\\main.log", encoding="utf-8", level=logging.DEBUG)

last_time = time.time()
fps_timer = last_time  # Time of the last FPS update
frame_count = 0

tiles = load_text_dir("assets\\sprites\\tiles")
tileset = remap_dict(tiles, world.TILE_NAME_TO_CHAR)

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
]

# happy_sprite = load_text("assets\\sprites\\happyhappyhappy.txt")
# 
# cuinter.SpriteRenderer.new(
#     0,
#     0,
#     happy_sprite,
# )
# 
# dialog = (
#     DialogLine("LELOLELOELOLEOLEOLEOLEOLEOLOLEOLOEELOmmmmmmmmmmmmmmmmmm    yeseiurrrrrhjsdhdjhsdjhsdhjsdhjdshjsdjhsdjhdsjhdshjsdhjsdhjsdhjdshjdshdsdssjhgfqwè¨qè¨¨èwq¨qwèwq", Character("Idris")),
#     DialogLine("bruh"),
#     DialogLine("AAAAAAAAAAAAAAAAAAAAAAAAAAAAA"),
#     DialogLine("We're no strangers to love You know the rules and so do I A full commitment's what I'm thinkin' of You wouldn't get this from any other guy I just wanna tell you how I'm feeling Gotta make you understand Never gonna give you up, never gonna let you down Never gonna run around and desert you Never gonna make you cry, never gonna say goodbye Never gonna tell a lie and hurt you We've known each other for so long Your heart's been aching, but you're too shy to say it Inside, we both know what's been going on We know the game and we're gonna play it And if you ask me how I'm feeling Don't tell me you're too blind to see Never gonna give you up, never gonna let you down Never gonna run around and desert you Never gonna make you cry, never gonna say goodbye Never gonna tell a lie and hurt you Never gonna give you up, never gonna let you down Never gonna run around and desert you Never gonna make you cry, never gonna say goodbye Never gonna tell a lie and hurt you We've known each other for so long Your heart's been aching, but you're too shy to say it Inside, we both know what's been going on We know the game and we're gonna play it I just wanna tell you how I'm feeling Gotta make you understand Never gonna give you up, never gonna let you down Never gonna run around and desert you Never gonna make you cry, never gonna say goodbye Never gonna tell a lie and hurt you Never gonna give you up, never gonna let you down Never gonna run around and desert you Never gonna make you cry, never gonna say goodbye Never gonna tell a lie and hurt you Never gonna give you up, never gonna let you down Never gonna run around and desert you Never gonna make you cry, never gonna say goodbye Never gonna tell a lie and hurt you", Character("Rick Astley")),
# )
# 
# for i in range(8):
#     cuinter.DialogBox.new(
#         random.randrange(0, cuinter.screen_height),
#         random.randrange(0, cuinter.screen_width),
#         random.randrange(10, 50),
#         random.randrange(10, 50),
#         dialog,
#     )

options = (
    "haram",
    "harambe",
    "PETAH",
    "The honse is here.",
)

cuinter.ChoiceBox.new(
    cuinter.screen_height - 12,
    round(cuinter.screen_width / 4),
    10,
    round(cuinter.screen_width / 2),
    options,
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
                
                elif value == ord("q"):
                    raise SystemExit
            
            case EVENT_TYPES.LOAD_ZONE:
                if (not isinstance(value, tuple) or len(value) != 3
                or not isinstance(value[0], str)
                or not isinstance(value[1], int)
                or not isinstance(value[2], int)):
                    logger.error(f"Expected value of type (str, int, int), got {value}")
                    continue
                
                world_objects.clear()
                zone_path, player_grid_y, player_grid_x = value
                zone: world.Zone = load_pickle(zone_path)
                grid = grid.load_tilemap(zone.tilemap)
                grid = grid.center(cuinter.screen_height, cuinter.screen_width)
                player = player.config(grid=grid, grid_y=player_grid_y, grid_x=player_grid_x)
                
                for world_object_type, constructor_parameters in zone.world_objects:
                    new_world_object = None
                    match world_object_type:
                        case WORLD_OBJECT_TYPES.GRID_SPRITE:
                            new_world_object = world.GridSprite.new(*constructor_parameters)
                        
                        case WORLD_OBJECT_TYPES.GRID_MULTI_SPRITE:
                            new_world_object = world.GridMultiSprite.new(*constructor_parameters)
                        
                        case WORLD_OBJECT_TYPES.WORLD_CHARACTER:
                            new_world_object = world.WorldCharacter.new(*constructor_parameters)
                        
                        case WORLD_OBJECT_TYPES.WALK_TRIGGER:
                            new_world_object = world.WalkTrigger.new(*constructor_parameters)
                
                    try_append(world_objects, new_world_object)
