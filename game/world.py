"""Classes for map structure and navigation

Builds on cuinter.SpriteRenderer to add grid-based game objects.

Contributors:
    Romain
"""

from __future__ import annotations
from typing import NamedTuple, Callable
from common import Character, Event
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


class Grid(NamedTuple):
    # Could be called TilemapRenderer but Grid is more practical
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
    grid: Grid
    sprite_renderer: SpriteRenderer
    
    @property
    def grid_y(self) -> int:
        return self.grid.screen_to_grid(y=self.sprite_renderer.y)
    
    @property
    def grid_x(self) -> int:
        return self.grid.screen_to_grid(x=self.sprite_renderer.x)
    
    @classmethod
    def new(cls, grid: Grid, grid_y: int, grid_x: int, sprite: str = None) -> GridSprite:
        return cls(
            grid,
            SpriteRenderer.new(
                grid.grid_to_screen(y=grid_y),
                grid.grid_to_screen(x=grid_x),
                sprite,
            ),
        )
    
    def config(self, **kwargs) -> GridSprite:
        grid_y = kwargs.get("grid_y", self.grid_y)
        grid_x = kwargs.get("grid_x", self.grid_x)
        
        return GridSprite(
            self.grid,
            self.sprite_renderer.config(
                y=self.grid.grid_to_screen(y=grid_y),
                x=self.grid.grid_to_screen(x=grid_x),
                **kwargs,
            ),
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
    
    @classmethod
    def new(cls, grid: Grid, grid_y: int, grid_x: int,
            sprite_sheet: dict[str, str] = None, sprite_key: str = None) -> GridMultiSprite:
        if sprite_sheet:
            if sprite_key is None:
                sprite_key = sprite_sheet.keys()[0]
            sprite = sprite_sheet[sprite_key]
        else:
            sprite = None
        
        return cls(
            GridSprite.new(grid, grid_y, grid_x, sprite),
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
    
    @classmethod
    def new(cls, grid: Grid, grid_y: int, grid_x: int, character: Character, sprite_key: str = None) -> WorldCharacter:
        return cls(
            character,
            GridMultiSprite.new(
                grid,
                grid_y,
                grid_x,
                character.sprite_sheet,
                sprite_key,
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
    on_trigger_event: Event = None
    
    @classmethod
    def new(cls, grid_y: int, grid_x: int, on_trigger_event: Event = None) -> WalkTrigger:
        return cls(
            grid_y,
            grid_x,
            on_trigger_event,
        )
    
    def config(self, **kwargs) -> WalkTrigger: 
        return WalkTrigger(
            kwargs.get("grid_y", self.grid_y),
            kwargs.get("grid_x", self.grid_x),
            kwargs.get("on_trigger_event", self.on_trigger_event),
        )
    
    def on_walk(self, grid_y: int, grid_x: int):
        if self.grid_y != grid_y or self.grid_x != grid_x:
            return None
        return self.on_trigger_event


class InteractTrigger(NamedTuple):
    grid_y: int
    grid_x: int
    on_trigger_event: Event = None
    
    @property
    def grid_y(self) -> int:
        return self.walk_trigger.grid_y
    
    @property
    def grid_x(self) -> int:
        return self.walk_trigger.grid_x
    
    @classmethod
    def new(cls, grid_y: int, grid_x: int, on_trigger: Callable = None) -> InteractTrigger:
        return cls(
            WalkTrigger.new(grid_y, grid_x),
            on_trigger,
        )
    
    def config(self, **kwargs) -> InteractTrigger:
        on_trigger = kwargs.pop("on_trigger", self.on_trigger)
        
        return WalkTrigger(
            self.walk_trigger.config(**kwargs),
            on_trigger,
        )
    
    def on_interact(self, grid_y: int, grid_x: int):
        if not self.walk_trigger.on_walk(grid_y, grid_x):
            return False
        if self.on_trigger is not None:
            self.on_trigger()
        return True


class Zone(NamedTuple):
    tilemap: tuple[str]
    world_objects: tuple[object, ...] = ()
