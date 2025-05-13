"""Classes for map structure and navigation

Builds on cuinter.SpriteRenderer to add grid-based game objects.

Contributors:
    Romain
"""

from __future__ import annotations
from typing import NamedTuple, Callable
from common import Character, EnumObject
from cuinter import SpriteRenderer
import logging

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


class _WorldObjectTypes(NamedTuple):
    GRID_SPRITE: int
    GRID_MULTI_SPRITE: int
    WORLD_CHARACTER: int
    WALK_TRIGGER: int

    @classmethod
    def new(cls) -> _WorldObjectTypes:
        return cls(*range(len(cls.__annotations__)))


class Grid(NamedTuple):
    # Could be called TilemapRenderer but Grid is more practical
    sprite_renderer: SpriteRenderer
    tileset: dict[str, str] = None # Maps the chars in tilemap to their text sprites
    tilemap: tuple[str] = None # Each str is a row and each char represents a tile
    
    @staticmethod
    def tilemap_to_sprite(tileset: dict[str, str], tilemap: tuple[str]) -> str:
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
    def new(cls, tileset: dict[str, str], tilemap: tuple[str] = None,
            y: int = 0, x: int = 0) -> Grid:
        if tilemap is not None and tileset is not None:
            sprite = Grid.tilemap_to_sprite(tileset, tilemap)
        else:
            sprite = None
        
        return cls(
            SpriteRenderer.new(
                y,
                x,
                sprite,
            ),
            tileset,
            tilemap,
        )
    
    def config(self, **kwargs) -> Grid:
        tileset = kwargs.get("tileset", self.tileset)
        tilemap = kwargs.get("tilemap", self.tilemap)
        
        if tilemap is not self.tilemap or tileset is not self.tileset:
            sprite = Grid.tilemap_to_sprite(tileset, tilemap)
        else:
            sprite = self.sprite_renderer.sprite
        
        return Grid(
            self.sprite_renderer.config(sprite=sprite, **kwargs),
            tileset,
            tilemap,
        )
    
    def load_tilemap(self, tilemap: tuple[str]) -> Grid:
        return self.config(tilemap=tilemap)
    
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
    sprite_renderer: SpriteRenderer
    grid: Grid
    grid_y: int
    grid_x: int
    
    @property
    def y_offset(self) -> int:
        return self.sprite_renderer.y - self.grid.grid_to_screen(y=self.grid_y)
    
    @property
    def x_offset(self) -> int:
        return self.sprite_renderer.x - self.grid.grid_to_screen(x=self.grid_x)
    
    @classmethod
    def new(cls, grid: Grid, grid_y: int, grid_x: int, sprite: str = None, y_offset: int = 0,
            x_offset: int = 0) -> GridSprite:
        return cls(
            SpriteRenderer.new(
                grid.grid_to_screen(y=grid_y) + y_offset,
                grid.grid_to_screen(x=grid_x) + x_offset,
                sprite,
            ),
            grid,
            grid_y,
            grid_x,
        )
    
    def config(self, **kwargs) -> GridSprite:
        grid = kwargs.get("grid", self.grid)
        grid_y = kwargs.get("grid_y", self.grid_y)
        grid_x = kwargs.get("grid_x", self.grid_x)
        y_offset = kwargs.get("y_offset", self.y_offset)
        x_offset = kwargs.get("x_offset", self.x_offset)
        
        return GridSprite(
            self.sprite_renderer.config(
                y=grid.grid_to_screen(y=grid_y) + y_offset,
                x=grid.grid_to_screen(x=grid_x) + x_offset,
                **kwargs,
            ),
            grid,
            grid_y,
            grid_x,
        )


class GridMultiSprite(NamedTuple):
    grid_sprite: GridSprite
    sprite_sheet: dict[str, str] = None
    sprite_key: str = None
    
    @property
    def grid(self) -> int:
        return self.grid_sprite.grid
    
    @property
    def grid_y(self) -> int:
        return self.grid_sprite.grid_y
    
    @property
    def grid_x(self) -> int:
        return self.grid_sprite.grid_x
    
    @property
    def y_offset(self) -> int:
        return self.grid_sprite.y_offset
    
    @property
    def x_offset(self) -> int:
        return self.grid_sprite.x_offset
    
    @classmethod
    def new(cls, grid: Grid, grid_y: int, grid_x: int, sprite_sheet: dict[str, str] = None,
            sprite_key: str = None, y_offset: int = 0, x_offset: int = 0) -> GridMultiSprite:
        if sprite_sheet:
            if sprite_key is None:
                sprite_key = sprite_sheet.keys()[0]
            sprite = sprite_sheet[sprite_key]
        else:
            sprite = None
        
        return cls(
            GridSprite.new(
                grid,
                grid_y,
                grid_x,
                sprite,
                y_offset,
                x_offset,
            ),
            sprite_sheet,
            sprite_key,
        )
    
    def config(self, **kwargs) -> GridMultiSprite:
        sprite_sheet = kwargs.get("sprite_sheet", self.sprite_sheet)
        sprite_key = kwargs.get("sprite_key", self.sprite_key)
        
        return GridMultiSprite(
            self.grid_sprite.config(sprite=sprite_sheet[sprite_key], **kwargs),
            sprite_sheet,
            sprite_key,
        )


class WorldCharacter(NamedTuple):
    character: Character
    grid_multi_sprite: GridMultiSprite
    
    @property
    def grid(self) -> int:
        return self.grid_multi_sprite.grid
    
    @property
    def grid_y(self) -> int:
        return self.grid_multi_sprite.grid_y
    
    @property
    def grid_x(self) -> int:
        return self.grid_multi_sprite.grid_x
    
    @property
    def y_offset(self) -> int:
        return self.grid_multi_sprite.y_offset
    
    @property
    def x_offset(self) -> int:
        return self.grid_multi_sprite.x_offset
    
    @classmethod
    def new(cls, grid: Grid, grid_y: int, grid_x: int, character: Character,
            sprite_key: str = None, y_offset: int = 0, x_offset: int = 0) -> WorldCharacter:
        return cls(
            character,
            GridMultiSprite.new(
                grid,
                grid_y,
                grid_x,
                character.sprite_sheet,
                sprite_key,
                y_offset,
                x_offset,
            ),
        )
    
    def config(self, **kwargs) -> WorldCharacter:
        character = kwargs.get("character", self.character)
        return WorldCharacter(
            character,
            self.grid_multi_sprite.config(
                sprite_sheet=character.sprite_sheet,
                **kwargs,
            ),
        )
    
    def move(self, grid_y: int, grid_x: int) -> WorldCharacter:
        new_grid_y = self.grid_y + grid_y
        new_grid_x = self.grid_x + grid_x
        if not self.grid.is_walkable(new_grid_y, new_grid_x):
            return self
        return self.config(grid_y=new_grid_y, grid_x=new_grid_x)


class WalkTrigger(NamedTuple):
    grid_y: int
    grid_x: int
    on_trigger_event: EnumObject = None
    key: int = None
    
    @classmethod
    def new(cls, grid_y: int, grid_x: int, on_trigger_event: EnumObject = None,
            key: int = None, grid: Grid = None) -> WalkTrigger:
        return cls(
            grid_y,
            grid_x,
            on_trigger_event,
            key,
        )
    
    def config(self, **kwargs) -> WalkTrigger: 
        return WalkTrigger(
            kwargs.get("grid_y", self.grid_y),
            kwargs.get("grid_x", self.grid_x),
            kwargs.get("on_trigger_event", self.on_trigger_event),
            kwargs.get("key", self.key),
        )
    
    def on_walk(self, grid_y: int, grid_x: int):
        if self.grid_y != grid_y or self.grid_x != grid_x:
            return None
        return self.on_trigger_event


logger = logging.getLogger(__name__)

WORLD_OBJECT_TYPES = _WorldObjectTypes.new()
WORLD_OBJECT_CLASSES = {
    WORLD_OBJECT_TYPES.GRID_SPRITE: GridSprite,
    WORLD_OBJECT_TYPES.GRID_MULTI_SPRITE: GridMultiSprite,
    WORLD_OBJECT_TYPES.WORLD_CHARACTER: WorldCharacter,
    WORLD_OBJECT_TYPES.WALK_TRIGGER: WalkTrigger,
}
