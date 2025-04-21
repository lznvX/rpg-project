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
from common import Character, DialogLine, load_text, load_text_dir, move_toward, remap_dict
import cuinter

FPS_COUNTER_REFRESH = 1 # Time between each FPS counter update
TILE_HEIGHT = 8
TILE_WIDTH = 16
TILE_NAME_TO_CHAR = {
    "grass": " ",
    "path_vertical": "│",
    "path_horizontal": "─",
    "path_up_left": "┘",
    "path_up_right": "└",
    "path_down_left": "┐",
    "path_down_right": "┌",
}

class Player(NamedTuple):
    character: Character
    sprite_renderer: cuinter.SpriteRenderer
    
    @property
    def y(self) -> int:
        return self.sprite_renderer.y
    
    @property
    def x(self) -> int:
        return self.sprite_renderer.x
    
    @classmethod
    def new(cls, y: int, x: int, character: Character) -> Player:
        return cls(
            character,
            cuinter.SpriteRenderer.new(y, x, character.sprite_sheet["base"]),
        )
    
    def config(self, **kwargs) -> Player:
        return Player(
            self.character, # TODO allow cross Romain-Jakub config
            self.sprite_renderer.config(**kwargs),
        )
    
    def move(self, y: int, x: int) -> Player:
        return self.config(y=self.y + y * TILE_HEIGHT, x=self.x + x * TILE_WIDTH)


class Grid(NamedTuple):
    sprite_renderer: cuinter.SpriteRenderer
    tilemap: tuple[str] # Each str is a row and each char represents a tile
    tileset: dict[str, str] # Maps the chars in tilemap to their text sprites
    
    @property
    def y(self) -> int:
        return self.sprite_renderer.y
    
    @property
    def x(self) -> int:
        return self.sprite_renderer.x
    
    @classmethod
    def new(cls, y: int, x: int, tilemap: tuple[str] = None, tileset: dict[str, str] = None) -> Grid:
        full_sprite = ""
        for row in tile_map:
            for sprite_y in range(TILE_HEIGHT):
                for char in row:
                    full_sprite += tileset[char].split("\n")[sprite_y]
                if sprite_y != TILE_HEIGHT - 1 or row != tile_map[-1]:
                    full_sprite += "\n"
        
        return Grid(
            cuinter.SpriteRenderer.new(y, x, full_sprite),
            tilemap,
            tileset,
        )
    
    def grid_to_screen(self, y: int, x: int) -> tuple[int, int]:
        return (
            self.y + TILE_HEIGHT * y,
            self.x + TILE_WIDTH * x,
        )


############ System init

logger = logging.getLogger(__name__)
logging.basicConfig(filename="logs\\main.log", encoding="utf-8", level=logging.DEBUG)

last_time = time.time()
fps_timer = last_time  # Time of the last FPS update
frame_count = 0

fps_label = cuinter.Label.new(0, 0)

############ Code to run on startup

tile_map = tuple(load_text("assets\\sprites\\tilemaps\\test_tilemap.txt").split("\n"))
grid = Grid.new(
    round((cuinter.screen_height - len(tile_map) * TILE_HEIGHT) / 2),
    round((cuinter.screen_width - len(tile_map[0]) * TILE_WIDTH) / 2),
    tile_map,
    remap_dict(load_text_dir("assets\\sprites\\tiles"), TILE_NAME_TO_CHAR),
)

player = Player.new(
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
                # an UI element
                # Match case for the key doesn't work, don't waste your time
                if value in (cuinter.KEY_UP, ord("w")):
                    player = player.move(-1, 0)
                
                elif value in (cuinter.KEY_DOWN, ord("s")):
                    player = player.move(1, 0)
                
                elif value in (cuinter.KEY_LEFT, ord("a")):
                    player = player.move(0, -1)
                
                elif value in (cuinter.KEY_RIGHT, ord("d")):
                    player = player.move(0, 1)
                    
                elif value == ord("q"):
                    break
            
            case cuinter.FINISHED_DIALOG:
                pass
            
            case cuinter.CONFIRMED_CHOICE:
                pass
