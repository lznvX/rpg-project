"""Setting management

Contributors:
    Romain
"""

from __future__ import annotations
import logging
from typing import NamedTuple
from enums import LANGUAGE_ENUM
from files import save_pickle, load_pickle

logger = logging.getLogger(__name__)

SETTINGS_PATH = "user_data\\settings.pkl"


class Settings(NamedTuple):
    first_time: bool
    language: int

    @classmethod
    def new(cls) -> Settings:
        return cls(
            first_time=True,
            language=LANGUAGE_ENUM.ENGLISH,
        )


def _make_setting_manager():
    cache = Settings.new()

    def get_cache() -> Settings:
        return cache

    def config_cache(**kwargs) -> None:
        logger.debug(f"Changing settings: {kwargs}")

        nonlocal cache
        cache = cache._replace(**kwargs)

    def reset_cache() -> None:
        logger.debug("Resetting settings")

        nonlocal cache
        cache = Settings.new()

    def save_cache() -> None:
        logger.debug("Saving settings")

        save_pickle(cache, SETTINGS_PATH)

    def load_cache() -> None:
        logger.debug("Loading settings")

        nonlocal cache
        stored_settings = load_pickle(SETTINGS_PATH)
        if stored_settings is not None:
            cache = stored_settings
            config(first_time=False)
        else:
            logger.warning("Settings file not found, using default")

    return (
        get_cache,
        config_cache,
        reset_cache,
        save_cache,
        load_cache,
    )


def _test():
    assert get("language") == LANGUAGE_ENUM.ENGLISH
    config(language=LANGUAGE_ENUM.FRENCH)
    assert get("language") == LANGUAGE_ENUM.FRENCH
    reset()
    assert get("language") == LANGUAGE_ENUM.ENGLISH
    print("Test passed")


(
    get,
    config,
    reset,
    save,
    load,
) = _make_setting_manager()

if __name__ == "__main__":
    _test()
