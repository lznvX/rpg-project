"""Main game script

Run with CTRL+T (thonny), currently contains game loop setup, utility labels and
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
from common import Character, DialogLine, load_text, load_text_dir, remap_dict
import cuinter
import world

FPS_COUNTER_REFRESH = 1 # Time between each FPS counter update

############ Code to run on startup

logger = logging.getLogger(__name__)
logging.basicConfig(filename="logs\\main.log", encoding="utf-8", level=logging.DEBUG)

last_time = time.time()
fps_timer = last_time  # Time of the last FPS update
frame_count = 0

tiles = load_text_dir("assets\\sprites\\tiles")
tileset = remap_dict(tiles, world.TILE_NAME_TO_CHAR)
text_tilemap = load_text("assets\\sprites\\tilemaps\\test_tilemap.txt")
tilemap = tuple(text_tilemap.split("\n"))

grid = world.Grid.new(tileset)
grid = grid.load_zone(world.Zone(tilemap))
grid = grid.center(cuinter.screen_height, cuinter.screen_width)

player = world.Player.new(
    grid.y,
    grid.x,
    Character("Player", load_text_dir("assets\\sprites\\characters\\player")),
)

# happy_sprite = load_text("assets\\sprites\\happyhappyhappy.txt")
# 
# cuinter.SpriteRenderer.new(
#     0,
#     0,
#     happy_sprite,
# )

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
    
    ############ Cuinter event handling, code to run every frame
    
    events = cuinter.mainloop()
    
    for event_type, value in events:
        match event_type:
            case cuinter.PRESSED_KEY:
                # Key presses only passed to events if they weren't caught by
                # a UI element
                # Match case for the key doesn't work, don't waste your time
                if value == ord("w"):
                    player = player.move(grid, -1, 0)
                    if player.sprite_key != "up":
                        player = player.config(sprite_key="up")
                
                elif value == ord("s"):
                    player = player.move(grid, 1, 0)
                    if player.sprite_key != "down":
                        player = player.config(sprite_key="down")
                
                elif value == ord("a"):
                    player = player.move(grid, 0, -1)
                    if player.sprite_key != "left":
                        player = player.config(sprite_key="left")
                
                elif value == ord("d"):
                    player = player.move(grid, 0, 1)
                    if player.sprite_key != "right":
                        player = player.config(sprite_key="right")
                    
                elif value == ord("q"):
                    break
            
            case cuinter.FINISHED_DIALOG:
                pass
            
            case cuinter.CONFIRMED_CHOICE:
                pass
