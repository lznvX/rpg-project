"""Classes for map structure and navigation.

Builds on cuinter.SpriteRenderer to add grid-based game objects.

Docstrings partly written by GitHub Copilot (GPT-4.1),
verified and modified when needed by us.

Contributors:
    Romain
"""

from __future__ import annotations
import logging
from typing import NamedTuple
from common import EnumObject
from cuinter import SpriteRenderer
from enums import WORLD_OBJECT_TYPES
from game_classes import Character

logger = logging.getLogger(__name__)

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
    """Renders a grid of tiles and provides mapping between grid and screen coordinates.

    Attributes:
        sprite_renderer (SpriteRenderer): The renderer for the grid.
        tileset (dict[str, str]): Maps tile chars to their sprite strings.
        tilemap (tuple[str]): Each str is a row, and each char a tile.
    """
    sprite_renderer: SpriteRenderer
    tileset: dict[str, str]
    tilemap: tuple[str]

    @staticmethod
    def tilemap_to_sprite(tileset: dict[str, str], tilemap: tuple[str]) -> str:
        """Return a text sprite built from a tilemap.

        Each char is replaced by its corresponding tile sprite given by the tileset.
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
        """Top-left screen y coordinate of the grid."""
        return self.sprite_renderer.y

    @property
    def x(self) -> int:
        """Top-left screen x coordinate of the grid."""
        return self.sprite_renderer.x

    @classmethod
    def new(cls, tileset: dict[str, str], tilemap: tuple[str] = None,
            y: int = 0, x: int = 0) -> Grid:
        """Construct a new Grid at given coordinates, optionally with tilemap."""
        logger.debug("Creating new Grid")

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
        """Return a new Grid with updated attributes."""
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
        """Replace the grid's tilemap and update its sprite."""
        logger.debug("Loading tilemap")
        return self.config(tilemap=tilemap)

    def center(self, screen_height: int, screen_width: int) -> Grid:
        """Return a new Grid centered on the screen."""
        return self.config(
            y=round((screen_height - len(self.tilemap) * TILE_HEIGHT) / 2),
            x=round((screen_width - len(self.tilemap[0]) * TILE_WIDTH) / 2),
        )

    def grid_to_screen(self, y: int = None, x: int = None) -> int | tuple[int, int]:
        """Convert tile-grid coordinates to screen coordinates."""
        if y is not None and x is not None:
            return (
                self.y + TILE_HEIGHT * y,
                self.x + TILE_WIDTH * x,
            )
        if y is not None:
            return self.y + TILE_HEIGHT * y
        if x is not None:
            return self.x + TILE_WIDTH * x

        raise ValueError("grid_to_screen() requires at least one of y or x")

    def screen_to_grid(self, y: int = None, x: int = None) -> int | tuple[int, int]:
        """Convert screen coordinates to grid (tile) coordinates."""
        if y is not None and x is not None:
            return (
                round((y - self.y) / TILE_HEIGHT),
                round((x - self.x) / TILE_WIDTH),
            )
        if y is not None:
            return round((y - self.y) / TILE_HEIGHT)
        if x is not None:
            return round((x - self.x) / TILE_WIDTH)

        raise ValueError("screen_to_grid() requires at least one of y or x")

    def is_walkable(self, y: int, x: int) -> bool:
        """Return whether the tile at (y, x) is walkable."""
        if not (0 <= y < len(self.tilemap) and 0 <= x < len(self.tilemap[y])):
            return False
        return self.tilemap[y][x] in WALKABLE_TILE_CHARS


class GridSprite(NamedTuple):
    """A sprite placed at a specific grid position."""

    sprite_renderer: SpriteRenderer
    grid: Grid
    grid_y: int
    grid_x: int

    @property
    def y_offset(self) -> int:
        """Difference between sprite y and grid y in screen coordinates."""
        return self.sprite_renderer.y - self.grid.grid_to_screen(y=self.grid_y)

    @property
    def x_offset(self) -> int:
        """Difference between sprite x and grid x in screen coordinates."""
        return self.sprite_renderer.x - self.grid.grid_to_screen(x=self.grid_x)

    @classmethod
    def new(cls, grid: Grid, grid_y: int, grid_x: int, sprite: str = None, y_offset: int = 0,
            x_offset: int = 0) -> GridSprite:
        """Create a new GridSprite at a specific grid position (plus optional offset)."""
        logger.debug("Creating new GridSprite")

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
        """Return a new GridSprite with updated attributes."""
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
    """A grid sprite that can switch between multiple sprites (via a sprite_sheet)."""

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
        """Create a new GridMultiSprite, optionally selecting a sprite_key from sprite_sheet."""
        logger.debug("Creating new GridMultiSprite")

        if sprite_sheet:
            if sprite_key is None:
                sprite_key = next(iter(sprite_sheet.keys()))
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
        """Return a new GridMultiSprite with updated attributes and sprite."""
        sprite_sheet = kwargs.get("sprite_sheet", self.sprite_sheet)
        sprite_key = kwargs.get("sprite_key", self.sprite_key)

        return GridMultiSprite(
            self.grid_sprite.config(sprite=sprite_sheet[sprite_key], **kwargs),
            sprite_sheet,
            sprite_key,
        )


class WorldCharacter(NamedTuple):
    """A game character positioned on the grid, with associated sprite."""

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
        """Create a WorldCharacter at a grid position, using the character's sprite sheet."""
        logger.debug("Creating new WorldCharacter")

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
        """Return a new WorldCharacter with updated attributes."""
        character = kwargs.get("character", self.character)
        return WorldCharacter(
            character,
            self.grid_multi_sprite.config(
                sprite_sheet=character.sprite_sheet,
                **kwargs,
            ),
        )

    def move(self, grid_y: int, grid_x: int) -> WorldCharacter:
        """Return a new WorldCharacter moved to (grid_y, grid_x) if walkable, else unchanged."""
        new_grid_y = self.grid_y + grid_y
        new_grid_x = self.grid_x + grid_x
        if not self.grid.is_walkable(new_grid_y, new_grid_x):
            return self
        return self.config(grid_y=new_grid_y, grid_x=new_grid_x)


class WalkTrigger(NamedTuple):
    """Defines an event that triggers when a grid location is entered."""

    grid_y: int
    grid_x: int
    on_trigger_event: EnumObject = None
    key: int = None

    @classmethod
    def new(cls, grid_y: int, grid_x: int, on_trigger_event: EnumObject = None,
            key: int = None, grid: Grid = None) -> WalkTrigger:
        """Create a WalkTrigger at a grid location."""
        logger.debug("Creating new WalkTrigger")
        # Grid argument only to satisfy world_object checks

        return cls(
            grid_y,
            grid_x,
            on_trigger_event,
            key,
        )

    def config(self, **kwargs) -> WalkTrigger:
        """Return a new WalkTrigger with updated attributes."""
        return WalkTrigger(
            kwargs.get("grid_y", self.grid_y),
            kwargs.get("grid_x", self.grid_x),
            kwargs.get("on_trigger_event", self.on_trigger_event),
            kwargs.get("key", self.key),
        )

    def on_walk(self, grid_y: int, grid_x: int):
        """Return the trigger event if the current position matches this trigger."""
        if self.grid_y != grid_y or self.grid_x != grid_x:
            return None
        return self.on_trigger_event


WORLD_OBJECT_CLASSES = {
    WORLD_OBJECT_TYPES.GRID_SPRITE: GridSprite,
    WORLD_OBJECT_TYPES.GRID_MULTI_SPRITE: GridMultiSprite,
    WORLD_OBJECT_TYPES.WORLD_CHARACTER: WorldCharacter,
    WORLD_OBJECT_TYPES.WALK_TRIGGER: WalkTrigger,
}
