from __future__ import annotations
from typing import NamedTuple


class _SettingTypes(NamedTuple):
    LANGUAGE: int

    @classmethod
    def new(cls) -> _SettingTypes:
        return cls(*range(len(cls.__annotations__)))


SETTING_TYPES = _SettingTypes.new()