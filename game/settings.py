"""Setting management

Contributors:
    Romain
"""

from __future__ import annotations
import logging
from typing import NamedTuple
from lang import LANGUAGE_ENUM
from files import save_pickle, load_pickle

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

    def get(setting_name: str) -> object:
        try:
            return getattr(cache, setting_name)
        except AttributeError:
            logger.error(f"Settings don't contain {setting_name}")
            return None

    def config(**kwargs) -> None:
        nonlocal cache
        cache = cache._replace(**kwargs)
        logger.info(f"Settings changed: {kwargs}")

    def reset() -> None:
        nonlocal cache
        cache = Settings.new()
        logger.info("Settings reset")

    def save() -> None:
        save_pickle(cache, SETTINGS_PATH)
        logger.info("Settings saved")

    def load() -> None:
        nonlocal cache
        stored_settings = load_pickle(SETTINGS_PATH)
        if stored_settings is not None:
            cache = stored_settings
            logger.info("Settings loaded")
            config(first_time=False)
        else:
            logger.warning("Settings file not found, using default")

    return (
        get,
        config,
        reset,
        save,
        load,
    )


def _test():
    assert get("language") == LANGUAGE_ENUM.ENGLISH
    config(language=LANGUAGE_ENUM.FRENCH)
    assert get("language") == LANGUAGE_ENUM.FRENCH
    reset()
    assert get("language") == LANGUAGE_ENUM.ENGLISH
    print("Test passed")


logger = logging.getLogger(__name__)

(
    get,
    config,
    reset,
    save,
    load,
) = _make_setting_manager()

if __name__ == "__main__":
    _test()
