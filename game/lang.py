"""Language management.

Handles multilingual support, translation lookup, and dialog line processing.

Docstrings partly written by GitHub Copilot (GPT-4.1),
verified and modified when needed by us.

Created on 2025.03.17
Contributors:
    Jakub
    Romain
"""

from __future__ import annotations
import logging
from typing import NamedTuple
from common import EnumObject
from enums import LANGUAGE_ENUM
import settings

logger = logging.getLogger(__name__)

SUB_DICT_SEPARATOR = "."


class DialogLine(NamedTuple):
    """A single line of dialog, optionally with a character name."""
    text: str
    character_name: str = None

    @staticmethod
    def process_dialog_line(
        dialog_line: str | DialogLine | EnumObject
    ) -> DialogLine | EnumObject:
        """Turn any str or tuple into a DialogLine while letting events through.

        Args:
            dialog_line (str | DialogLine | EnumObject): The dialog input.

        Returns:
            DialogLine | EnumObject: A DialogLine, EnumObject, or error string if invalid.
        """
        if isinstance(dialog_line, str):
            return DialogLine(translate(dialog_line))

        if (isinstance(dialog_line, tuple)
        and len(dialog_line) == 2
        and isinstance(dialog_line[0], str)
        and isinstance(dialog_line[1], str)):
            return DialogLine(
                translate(dialog_line[0]),
                translate("character_names." + dialog_line[1]),
            )

        if isinstance(dialog_line, (DialogLine, EnumObject)):
            return dialog_line

        error_msg = f"Expected value of type str | DialogLine | EnumObject, got {dialog_line}"
        logger.error(error_msg)
        return error_msg

    @staticmethod
    def process_dialog(
        dialog: tuple[str | DialogLine | EnumObject, ...]
    ) -> tuple[DialogLine | EnumObject, ...]:
        """Convert a tuple of dialog entries to DialogLine/EnumObject types."""
        return tuple(map(DialogLine.process_dialog_line, dialog))


class _Lang(NamedTuple):
    """Holds all translatable strings and dictionaries for a particular language.

    Attributes correspond to dialog, menu, combat, items, tasks, etc.
    """
    welcome: str = None
    controls: str = None
    settings_language: str = None
    equipment_none: str = None
    item_equip: str = None
    item_unequip: str = None
    item_use: str = None
    menu: dict[str, str] = None
    combat: dict[str, str] = None
    character_names: dict[str, str] = None
    equipment_slots: dict[str, str] = None
    item_names: dict[str, str] = None
    item_descriptions: dict[str, str] = None
    action_names: dict[str, str] = None
    action_descriptions: dict[str, str] = None
    task_names: dict[str, str] = None
    task_descriptions: dict[str, str] = None


def _translate_simple(lang_key: str, sub_dict: dict = None) -> str:
    """Return lang_key translated in the selected language.

    Returns the text for the specified attribute name in the selected language
    from the settings or the provided sub dict.

    Args:
        lang_key: The translation key.
        sub_dict: Optional dictionary to look up the key.

    Returns:
        The translated string or the key itself if not found.
    """
    try:
        if sub_dict is None:
            lang_text = LANGUAGES[settings.get().language]
            lang_value = getattr(lang_text, lang_key)
        else:
            lang_value = sub_dict[lang_key]

        if isinstance(lang_value, str):
            return lang_value
        if isinstance(lang_value, dict):
            logger.error(f"Specify key of sub dict {lang_key} with dotted notation")
        elif lang_value is None:
            raise ValueError
        else:
            logger.error(f"LANGUAGES are made of STRINGS, not {lang_value}, you IDIOT")

    except (AttributeError, KeyError, ValueError):
        logger.warning(f"Selected language doesn't contain {lang_key}, using that instead")

    return lang_key


def _translate_nest(lang_key: str, sub_dict: dict = None) -> str:
    """Return lang_key translated in the selected language, supporting nested keys.

    Use dotted notation (e.g. "item_names.agi_boots") for nested dict lookup.

    Args:
        lang_key: The translation key (may use dotted notation).
        sub_dict: Optional dictionary for nested lookup.

    Returns:
        The translated string.
    """
    if SUB_DICT_SEPARATOR in lang_key:
        sub_dict_name, sub_dict_key = lang_key.split(SUB_DICT_SEPARATOR, 1)
        if sub_dict is None:
            lang_text = LANGUAGES[settings.get().language]
            next_sub_dict = getattr(lang_text, sub_dict_name)
        else:
            next_sub_dict = sub_dict[sub_dict_name]

        return _translate_nest(
            sub_dict_key,
            next_sub_dict,
        )

    return _translate_simple(lang_key, sub_dict)


def translate(lang_key: str | tuple[str]) -> str | tuple[str]:
    """Return lang_key translated in the selected language.

    Supports both single strings and tuples of keys.

    Args:
        lang_key: The translation key or a tuple of keys.

    Returns:
        The translated string or tuple of strings.
    """
    logger.debug(f"Translating {lang_key}")

    if isinstance(lang_key, tuple):
        return tuple(map(translate, lang_key))
    if isinstance(lang_key, str):
        return _translate_nest(lang_key)

    error_msg = f"Expected value of type str | tuple[str], got {lang_key}"
    logger.error(error_msg)
    return error_msg


def f(fstring: str, *args: object) -> str:
    """Shorthand for fstring.format(*args).

    Args:
        fstring: The format string.
        *args: Arguments to be formatted.

    Returns:
        The formatted string.
    """
    return fstring.format(*args)


def _test():
    """Test translations for integrity."""
    assert FRENCH.action_descriptions["slash"] == "Brandissez votre épée sur votre ennemi"
    assert _translate_simple("feet", ENGLISH.equipment_slots) == "Feet"
    print("all Tests passed")


ENGLISH = _Lang(
    # Dialog
    welcome = "Welcome adventurer !\n(press Space or Enter)",
    controls = "Controls:\n\nUp: W    Down: S    Left: A    Right: D\nConfirm: Space/Enter    Menu: M",

    settings_language = "Language",

    equipment_none = "None",

    item_equip = "Equip",
    item_unequip = "Unequip",
    item_use = "Use",

    menu = {
        "back": "Back",
        "equipment": "Equipment",
        "backpack": "Backpack",
        "settings": "Settings",
        "save": "Save",
        "load": "Load",
        "close": "Close menu",
        "save_quit": "Save and quit",
        "test_combat": "Start combat test",
    },

    # Combat
    combat = {
        "begin"    : "You are now in battle!",
        "win"      : "You won the battle!",
        "loss"     : "You lost the battle :(",
        "rewards"  : "You gain {} gold and {} xp!",
        "turn"     : "Turn {} begins!",

        "attack"   : "{} uses {} on {}",
        "damage"   : "{} takes ¤ {} damage! (♥ {} left)",
        "death"    : "{} dies!",
        "ko"       : "{} is knocked out!",
        "action_choice"    : "What should {} do?",
        "target_choice"    : "Choose target for {}:",
    },

    # Characters
    character_names = {
        "player": "Player",
        "goblin": "Goblin",
        "hobgoblin": "Hobgoblin",
        "goblin_chief": "Goblin chieftain",
        "bandit": "Bandit",
    },

    # Slots
    equipment_slots = {
        "mainhand": "Mainhand",
        "offhand": "Offhand",
        "head": "Head",
        "body": "Body",
        "feet": "Feet",
    },

    # Items
    item_names = {
        "agi_boots": "Hermes' Boots",
        "potion_health": "Potion of Healing",
        "str_helmet": "Helmet of Strength",
        "sword": "Sword",
        "dagger": "Dagger",
    },
    item_descriptions = {
        "agi_boots": "A pair of boots with suspicious wings",
        "potion_health": "Heals ♥ 5 when consumed",
        "str_helmet": "A spartan helmet, enchanted with a strength spell",
        "sword": "An elegant weapon, from a more civilised time",
        "dagger": "A pointy little thing",
    },

    # Actions
    action_names = {
        "light_stab": "Light Stab",
        "slash": "Slash",
        "stab": "Stab",
    },
    action_descriptions = {
        "light_stab": "Stab your opponent with your puny dagger",
        "slash": "Swing your sword at your opponent",
        "stab": "Stick 'em with the pointy end",
    },

    # Tasks
    task_names = {
        # "task_name": "Task Name"
    },
    task_descriptions = {
        # "task_name": "Task Description"
    },
)

FRENCH = _Lang(
    # Dialog
    welcome = "Bienvenue aventurier !\n(appuyez sur Espace ou Entrée)",
    controls = "Controles:\n\nHaut: W    Bas: S    Gauche: A    Droite: D\nConfirmer: Space/Enter    Menu: M",

    settings_language = "Langue",

    equipment_none = "Aucun",

    item_equip = "Équiper",
    item_unequip = "Déséquiper",
    item_use = "Utiliser",

    menu = {
        "back": "Retour",
        "equipment": "Équipement",
        "backpack": "Sac à dos",
        "settings": "Options",
        "save": "Sauvegarder",
        "load": "Charger",
        "close": "Fermer le menu",
        "save_quit": "Sauvegarder et quitter",
        "test_combat": "Commencer combat de test",
    },

    # Combat
    combat = {
        "begin"    : "Vous êtes maintenant en combat !",
        "win"      : "Vous avez gagné le combat !",
        "loss"     : "Vous avez perdu le combat :(",
        "rewards"  : "Vous gagnez {} pièces d'or et {} xp !",
        "turn"     : "Le tour {} commence !",

        "attack"   : "{} utilise {} sur {}",
        "damage"   : "{} prend ¤ {} dégats ! (il lui reste ♥ {})",
        "death"    : "{} meurt !",
        "ko"       : "{} est assommé !",
        "action_choice"    : "Que'est-ce que {} devrait faire ?",
        "target_choice"    : "Choisissez la cible de {}:",
    },

    # Characters
    character_names = {
        "player": "Joueur",
        "goblin": "Gobelin",
        "hobgoblin": "Hobgobelin",
        "goblin_chief": "Chef gobelin",
        "bandit": "Bandit",
    },

    # Slots
    equipment_slots = {
        "mainhand": "Main principale",
        "offhand": "Main secondaire",
        "head": "Tête",
        "body": "Corps",
        "feet": "Pieds",
    },

    # Items
    item_names = {
        "agi_boots": "Bottes de Hermes",
        "potion_health": "Potion de Guérison",
        "str_helmet": "Heaume de Force",
        "sword": "Épée",
        "dagger": "Dague",
    },
    item_descriptions = {
        "agi_boots": "Une pair de bottes avec des ailes suspicieuses",
        "potion_health": "Guérit ♥ 5 lors de consommation",
        "str_helmet": "Une heaume spartane, enchantée avec un sort de force",
        "sword": "Un truc pointu",
        "dagger": "Un autre truc pointu",
    },

    # Actions
    action_names = {
        "light_stab": "Coup de couteau",
        "slash": "Coup d'épée",
        "stab": "Coup de pointe",
    },
    action_descriptions = {
        "light_stab": "Poignardez votre ennemi avec votre arme",
        "slash": "Brandissez votre épée sur votre ennemi",
        "stab": "Frappez l'enemi avec la pointe de votre arme",
    },

    # Tasks
    task_names = {
        # "task_name": "Task Name"
    },
    task_descriptions = {
        # "task_name": "Task Description"
    },
)

LANGUAGES = {
    LANGUAGE_ENUM.ENGLISH: ENGLISH,
    LANGUAGE_ENUM.FRENCH: FRENCH,
}

if __name__ == "__main__":
    _test()
