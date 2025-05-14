"""Classes and functions shared between several systems

Created on 2025.03.20
Contributors:
    Jakub
    Adrien
    Romain
"""

from __future__ import annotations
import logging
import os
import pickle
from typing import NamedTuple, Callable


class EnumObject(NamedTuple):
    """
    Stores an object with an associated int. Usually used to define how the object is used, such as
    in events and world objects.
    """
    enum: int
    value: object = None


class _EventTypes(NamedTuple):
    PRESS_KEY: int
    MAKE_UI_ELEMENT: int
    MAKE_WORLD_OBJECT: int
    LOAD_UI_ELEMENT: int
    LOAD_ZONE: int
    LOAD_COMBAT: int
    CONFIG_SETTINGS: int
    SAVE_GAME: int
    LOAD_GAME: int
    QUIT: int
    MULTI_EVENT: int

    @classmethod
    def new(cls) -> _EventTypes:
        return cls(*range(len(cls.__annotations__)))


def named_tuple_modifier(data_type: Callable, old_data: NamedTuple, **changes) -> NamedTuple:
    """Generate a new NamedTuple based on an existing one.

    Changes are represented as another NamedTuple of the same type
    """
    changes = data_type(**changes)

    new_data = []
    for old, new in zip(old_data, changes):
        if new is None:
            new_data.append(old)
        else:
            new_data.append(new)
    return data_type(*new_data)


def move_toward(a: int | float, b: int | float, step: int | float = 1) -> int | float:
    """Returns a moved by step towards b without overshooting."""
    return min(a + step, b) if b >= a else max(a - step, b)


def remap_dict(data: dict, key_map: dict) -> dict:
    """
    Returns a new dict with keys of data remapped through key_map and values
    unchanged.
    """
    return {key_map[k]: v for k, v in data.items() if k in key_map}


def try_append(collection: list, item: object) -> None:
    if item is not None:
        collection.append(item)


logger = logging.getLogger(__name__)

EVENT_TYPES = _EventTypes.new()

if __name__ == "__main__":
    # Tests
    Inventory._test()
    Character._test()
