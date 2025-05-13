"""Setting management

Contributors:
    Romain
"""

from __future__ import annotations
import logging
from typing import NamedTuple
from lang import LANGUAGE_ENUM


class Settings(NamedTuple):
    language: int = None

    @classmethod
    def new(cls) -> Settings:
        return cls(
            language=LANGUAGE_ENUM.ENGLISH,
        )


def _make_setting_manager():
    cache = Settings.new()

    def get_setting(setting_name: str) -> object:
        try:
            return getattr(cache, setting_name)
        except AttributeError:
            logger.error("Settings don't contain {setting_name}")
            return None

    def config_settings(**kwargs) -> Settings:
        nonlocal cache
        cache = cache._replace(**kwargs)
        return cache

    def reset_settings() -> Settings:
        nonlocal cache
        cache = Settings.new()
        return cache

    return get_setting, config_settings, reset_settings


def test():
    assert get_setting("language") == LANGUAGE_ENUM.ENGLISH
    config_settings(language=LANGUAGE_ENUM.FRENCH)
    assert get_setting("language") == LANGUAGE_ENUM.FRENCH
    reset_settings()
    assert get_setting("language") == LANGUAGE_ENUM.ENGLISH
    print("Test passed")


logger = logging.getLogger(__name__)

get_setting, config_settings, reset_settings = _make_setting_manager()

if __name__ == "__main__":
    test()
