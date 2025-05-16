"""Various pseudo enums

We can't use actual enums, so have fun with NamedTuples.

Created on 2025.05.14
Contributors:
    Romain
"""

from __future__ import annotations
from typing import NamedTuple


class _EventTypes(NamedTuple):
    PRESS_KEY: int
    MAKE_UI_ELEMENT: int
    MAKE_WORLD_OBJECT: int
    LOAD_UI_ELEMENT: int
    LOAD_ZONE: int
    LOAD_COMBAT: int
    OPEN_ITEM: int
    OPEN_EQUIPMENT: int
    OPEN_BACKPACK: int
    CONFIG_SETTINGS: int
    SAVE_GAME: int
    LOAD_GAME: int
    QUIT: int
    MULTI_EVENT: int

    @classmethod
    def new(cls) -> _EventTypes:
        return cls(*range(len(cls.__annotations__)))


class _LanguageEnum(NamedTuple):
    ENGLISH: int
    FRENCH: int

    @classmethod
    def new(cls) -> _LanguageEnum:
        return cls(*range(len(cls.__annotations__)))


class _UIElementTypes(NamedTuple):
    LABEL: int
    SPRITE_RENDERER: int
    RECTANGLE: int
    TEXT_BOX: int
    DIALOG_BOX: int
    CHOICE_BOX: int

    @classmethod
    def new(cls) -> _UIElementTypes:
        return cls(*range(len(cls.__annotations__)))


class _RectanglePresets(NamedTuple):
    DIALOG: int
    MENU: int

    @classmethod
    def new(cls) -> _RectanglePresets:
        return cls(*range(len(cls.__annotations__)))


class _WorldObjectTypes(NamedTuple):
    GRID_SPRITE: int
    GRID_MULTI_SPRITE: int
    WORLD_CHARACTER: int
    WALK_TRIGGER: int

    @classmethod
    def new(cls) -> _WorldObjectTypes:
        return cls(*range(len(cls.__annotations__)))


EVENT_TYPES = _EventTypes.new()
LANGUAGE_ENUM = _LanguageEnum.new()
UI_ELEMENT_TYPES = _UIElementTypes.new()
RECTANGLE_PRESETS = _RectanglePresets.new()
WORLD_OBJECT_TYPES = _WorldObjectTypes.new()
