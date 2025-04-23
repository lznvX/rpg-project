"""Classes for map navigation and structure

Contributors:
    Romain
"""

from __future__ import annotations
from typing import NamedTuple
from common import Character
from cuinter import SpriteRenderer

TILE_HEIGHT = 8
TILE_WIDTH = 16
TILE_NAME_TO_CHAR = {
    "blank": "X",
    "grass": " ",
    "grass_solid": "/",
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


class Player(NamedTuple):
    character: Character
    sprite_renderer: SpriteRenderer
    sprite_key: str = "down"
    
    @property
    def y(self) -> int:
        return self.sprite_renderer.y
    
    @property
    def x(self) -> int:
        return self.sprite_renderer.x
    
    @classmethod
    def new(cls, y: int, x: int, character: Character, sprite_key: str = "down") -> Player:
        return cls(
            character,
            SpriteRenderer.new(y, x, character.sprite_sheet[sprite_key]),
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
    
    def move(self, grid: Grid, y: int, x: int) -> Player:
        new_grid_y = grid.screen_to_grid(y=self.y) + y
        new_grid_x = grid.screen_to_grid(x=self.x) + x
        if not grid.is_walkable(new_grid_y, new_grid_x): return self
        new_y, new_x = grid.grid_to_screen(new_grid_y, new_grid_x)
        return self.config(y=new_y, x=new_x)


class Grid(NamedTuple):
    # Could be called TilemapRenderer (more explicit) but Grid is more practical
    sprite_renderer: SpriteRenderer
    tilemap: tuple[str] = None # Each str is a row and each char represents a tile
    tileset: dict[str, str] = None # Maps the chars in tilemap to their text sprites
    
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
    
    @property
    def y(self) -> int:
        return self.sprite_renderer.y
    
    @property
    def x(self) -> int:
        return self.sprite_renderer.x
    
    @classmethod
    def new(cls, tileset: dict[str, str], tilemap: tuple[str] = None, y: int = 0, x: int = 0) -> Grid:
        if tilemap is not None and tileset is not None:
            sprite = Grid.tilemap_to_sprite(tilemap, tileset)
        else:
            sprite = None
        
        return cls(
            SpriteRenderer.new(
                y,
                x,
                sprite,
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
            tilemap,
            tileset,
        )
    
    def load_zone(self, zone: Zone) -> Grid:
        return self.config(tilemap=zone.tilemap)
    
    def center(self, screen_height: int, screen_width: int) -> Grid:
        return self.config(
            y=round((screen_height - len(self.tilemap) * TILE_HEIGHT) / 2),
            x=round((screen_width - len(self.tilemap[0]) * TILE_WIDTH) / 2),
        )
    
    def grid_to_screen(self, y: int = None, x: int = None) -> int | tuple[int, int]:
        if y is not None and x is not None:
            return (
                self.y + TILE_HEIGHT * y,
                self.x + TILE_WIDTH * x,
            )
        elif y is not None:
            return self.y + TILE_HEIGHT * y
        elif x is not None:
            return self.x + TILE_WIDTH * x
        else:
            raise ValueError("grid_to_screen() requires at least one of y or x")
    
    def screen_to_grid(self, y: int = None, x: int = None) -> int | tuple[int, int]:
        if y is not None and x is not None:
            return (
                round((y - self.y) / TILE_HEIGHT),
                round((x - self.x) / TILE_WIDTH),
            )
        elif y is not None:
            return round((y - self.y) / TILE_HEIGHT)
        elif x is not None:
            return round((x - self.x) / TILE_WIDTH)
        else:
            raise ValueError("screen_to_grid() requires at least one of y or x")
    
    def is_walkable(self, y: int, x: int) -> bool:
        if not (0 <= y < len(self.tilemap) and 0 <= x < len(self.tilemap[y])):
            return False
        return self.tilemap[y][x] in WALKABLE_TILE_CHARS


class GridSprite(NamedTuple):
    grid_y: int
    grid_x: int
    sprite_renderer: SpriteRenderer


class Interactable(NamedTuple):
    grid_y: int
    grid_x: int


class Portal(NamedTuple):
    grid_y: int
    grid_x: int


class Zone(NamedTuple):
    tilemap: tuple[str]
    world_objects: tuple[object, ...] = ()
