"""Setting management.

Handles the retrieval, modification, and persistence of global game settings.

Docstrings written by GitHub Copilot (GPT-4.1),
verified and modified when needed by us.

Contributors:
    Romain
"""

from __future__ import annotations
import logging
from typing import Callable, NamedTuple
from enums import LANGUAGE_ENUM
from files import save_pickle, load_pickle

logger = logging.getLogger(__name__)

SETTINGS_PATH = "user_data\\settings.pkl"


class Settings(NamedTuple):
    """Stores application settings.

    Attributes:
        first_time (bool): Whether it is the user's first time running the app.
        language (int): The selected language (uses LANGUAGE_ENUM).
    """
    first_time: bool
    language: int

    @classmethod
    def new(cls) -> Settings:
        """Return the default settings."""
        return cls(
            first_time=True,
            language=LANGUAGE_ENUM.ENGLISH,
        )


def _make_setting_manager() -> tuple[Callable, ...]:
    """Create manager functions for getting, modifying, saving, and loading settings.

    Returns:
        Tuple of (get_cache, config_cache, reset_cache, save_cache, load_cache).
    """
    cache = Settings.new()

    def get_cache() -> Settings:
        """Return the current settings."""
        return cache

    def config_cache(**kwargs) -> None:
        """Update settings with provided keyword arguments."""
        logger.debug(f"Changing settings: {kwargs}")

        nonlocal cache
        cache = cache._replace(**kwargs)

    def reset_cache() -> None:
        """Reset settings to default values."""
        logger.debug("Resetting settings")

        nonlocal cache
        cache = Settings.new()

    def save_cache() -> None:
        """Save the current settings to disk."""
        logger.debug("Saving settings")
        save_pickle(cache, SETTINGS_PATH)

    def load_cache() -> None:
        """Load settings from disk, or use defaults if unavailable."""
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
    """Test suite for the settings manager."""
    assert get().language == LANGUAGE_ENUM.ENGLISH
    config(language=LANGUAGE_ENUM.FRENCH)
    assert get().language == LANGUAGE_ENUM.FRENCH
    reset()
    assert get().language == LANGUAGE_ENUM.ENGLISH
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
