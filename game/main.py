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
    "blank": "X",
    "grass": " ",
    "path_vertical": "│",
    "path_horizontal": "─",
    "path_up_left": "┘",
    "path_up_right": "└",
    "path_down_left": "┐",
    "path_down_right": "┌",
    "wall_vertical": "║",
    "wall_horizontal": "═",
    "wall_up_left": "╝",
    "wall_up_right": "╚",
    "wall_down_left": "╗",
    "wall_down_right": "╔",
}
WALKABLE_TILE_CHARS = " │─┘└┐┌"

class Player(NamedTuple): # Rename to WorldPlayer or smth if needed
    character: Character
    sprite_renderer: cuinter.SpriteRenderer
    sprite_key: str = "down"
    
    @property
    def y(self) -> int:
        return self.sprite_renderer.y
    
    @property
    def x(self) -> int:
        return self.sprite_renderer.x
    
    @property
    def grid_y(self) -> int:
        return grid.screen_to_grid(self.y, self.x)[0]
    
    @property
    def grid_x(self) -> int:
        return grid.screen_to_grid(self.y, self.x)[1]
    
    @classmethod
    def new(cls, y: int, x: int, character: Character, sprite_key: str = "down") -> Player:
        return cls(
            character,
            cuinter.SpriteRenderer.new(y, x, character.sprite_sheet[sprite_key]),
            sprite_key,
        )
    
    def config(self, **kwargs) -> Player:
        character = kwargs.get("character", self.character)
        sprite_key = kwargs.get("sprite_key", self.sprite_key)
        
        if (sprite_key is not self.sprite_key
        or character.sprite_sheet is not self.character.sprite_sheet):
            sprite = character.sprite_sheet[sprite_key]
        else:
            sprite = self.sprite_renderer.sprite
        
        return Player(
            character, # TODO allow cross Romain-Jakub config
            self.sprite_renderer.config(sprite=sprite, **kwargs),
            sprite_key,
        )
    
    def move(self, y: int, x: int) -> Player:
        new_grid_y, new_grid_x = self.grid_y + y, self.grid_x + x
        if not grid.is_walkable(new_grid_y, new_grid_x): return self
        new_y, new_x = grid.grid_to_screen(new_grid_y, new_grid_x)
        return self.config(y=new_y, x=new_x)


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
    
    @staticmethod
    def tilemap_to_sprite(tilemap: tuple[str], tileset: dict[str, str]) -> str:
        """
        Returns a text sprite of the tilemap with each char replaced by its
        corresponding tile sprite given by the tileset.
        """
        full_sprite = ""
        for row in tilemap:
            for sprite_y in range(TILE_HEIGHT):
                for char in row:
                    full_sprite += tileset[char].split("\n")[sprite_y]
                if sprite_y != TILE_HEIGHT - 1 or row != tilemap[-1]:
                    full_sprite += "\n"
        return full_sprite
    
    @classmethod
    def new(cls, y: int, x: int, tilemap: tuple[str] = None, tileset: dict[str, str] = None) -> Grid:
        return cls(
            cuinter.SpriteRenderer.new(
                y,
                x,
                Grid.tilemap_to_sprite(tilemap, tileset),
            ),
            tilemap,
            tileset,
        )
    
    def config(self, **kwargs) -> Grid:
        tilemap = kwargs.get("tilemap", self.tilemap)
        tileset = kwargs.get("tileset", self.tileset)
        
        if tilemap is not self.tilemap or tileset is not self.tileset:
            sprite = Grid.tilemap_to_sprite(tilemap, tileset)
        else:
            sprite = self.sprite_renderer.sprite
        
        return Grid(
            self.sprite_renderer.config(sprite=sprite, **kwargs),
            tilemap, # TODO should update sprite based on new tilemap and tileset
            tileset,
        )
    
    def grid_to_screen(self, y: int, x: int) -> tuple[int, int]:
        return (
            self.y + TILE_HEIGHT * y,
            self.x + TILE_WIDTH * x,
        )
    
    def screen_to_grid(self, y: int, x: int) -> tuple[int, int]:
        return (
            round((y - self.y) / TILE_HEIGHT),
            round((x - self.x) / TILE_WIDTH),
        )
    
    def is_walkable(self, y: int, x: int) -> bool:
        if not (0 <= y < len(self.tilemap) and 0 <= x < len(self.tilemap[y])):
            return False
        return self.tilemap[y][x] in WALKABLE_TILE_CHARS


############ Code to run on startup

logger = logging.getLogger(__name__)
logging.basicConfig(filename="logs\\main.log", encoding="utf-8", level=logging.DEBUG)

last_time = time.time()
fps_timer = last_time  # Time of the last FPS update
frame_count = 0

tilemap = tuple(load_text("assets\\sprites\\tilemaps\\test_tilemap.txt").split("\n"))
tileset = remap_dict(load_text_dir("assets\\sprites\\tiles"), TILE_NAME_TO_CHAR)
grid = Grid.new(
    round((cuinter.screen_height - len(tilemap) * TILE_HEIGHT) / 2),
    round((cuinter.screen_width - len(tilemap[0]) * TILE_WIDTH) / 2),
    tilemap,
    tileset,
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
                    player = player.move(-1, 0)
                    if player.sprite_key != "up":
                        player = player.config(sprite_key="up")
                
                elif value == ord("s"):
                    player = player.move(1, 0)
                    if player.sprite_key != "down":
                        player = player.config(sprite_key="down")
                
                elif value == ord("a"):
                    player = player.move(0, -1)
                    if player.sprite_key != "left":
                        player = player.config(sprite_key="left")
                
                elif value == ord("d"):
                    player = player.move(0, 1)
                    if player.sprite_key != "right":
                        player = player.config(sprite_key="right")
                    
                elif value == ord("q"):
                    break
            
            case cuinter.FINISHED_DIALOG:
                pass
            
            case cuinter.CONFIRMED_CHOICE:
                pass
