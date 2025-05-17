"""Language management

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

SUB_DICT_SEPARATOR = "."


class DialogLine(NamedTuple):
    text: str
    character_name: str = None

    @staticmethod
    def process_dialog_line(
        dialog_line: str | DialogLine | EnumObject
    ) -> DialogLine | EnumObject:
        """
        Turns any str or tuple into a DialogLine while letting events through and logging any
        unexpected types.
        """
        if isinstance(dialog_line, str):
            return DialogLine(translate(dialog_line))

        elif (isinstance(dialog_line, tuple)
        and len(dialog_line) == 2
        and isinstance(dialog_line[0], str)
        and isinstance(dialog_line[1], str)):
            return DialogLine(
                translate(dialog_line[0]),
                lang_text.character_names[dialog_line[1]],
            )

        elif isinstance(dialog_line, (DialogLine, EnumObject)):
            return dialog_line

        else:
            error_msg = "Expected value of type str | DialogLine | EnumObject, got {dialog_line}"
            logger.error(error_msg)
            return error_msg

    @staticmethod
    def process_dialog(
        dialog: tuple[str | DialogLine | EnumObject, ...]
    ) -> tuple[DialogLine | EnumObject, ...]:
        return tuple(map(DialogLine.process_dialog_line, dialog))


class _Lang(NamedTuple):
    # Dialog
    welcome: str = None
    controls: str = None

    # Choice
    settings_language: str = None
    
    equipment_none: str = None
    
    item_equip: str = None
    item_unequip: str = None
    item_use: str = None

    # Menu
    menu: dict[str, str] = None

    # Combat
    combat: dict[str, str] = None

    # Characters
    character_names: dict[str, str] = None

    # Slots
    equipment_slots: dict[str, str] = None

    # Items
    item_names: dict[str, str] = None
    # item_names = {
    #     "item_name": "Item Name"
    # }
    item_descriptions: dict[str, str] = None
    # item_descriptions = {
    #     "item_name": "Item Description"
    # }

    # Actions
    action_names: dict[str, str] = None
    # action_names = {
    #     "action_name": "Action Name"
    # }
    action_descriptions: dict[str, str] = None
    # action_descriptions = {
    #     "action_name": "Action Description"
    # }

    # Tasks
    task_names: dict[str, str] = None
    # task_names = {
    #     "task_name": "Task Name"
    # }
    task_descriptions: dict[str, str] = None
    # task_descriptions = {
    #     "task_name": "Task Description"
    # }


def _translate_simple(lang_key: str, sub_dict: dict = None) -> str:
    """
    Returns the text with the specified attribute name in the selected language
    from the settings or the provided sub dict.
    """
    try:
        if sub_dict is None:
            lang_text = LANGUAGES[settings.get("language")]
            lang_value = getattr(lang_text, lang_key)
        else:
            lang_value = sub_dict[lang_key]

        if isinstance(lang_value, str):
            return lang_value
        elif isinstance(lang_value, dict):
            logger.error(f"Specify key of sub dict {lang_key} with dotted notation")
        elif lang_value is None:
            raise ValueError
        else:
            logger.error(f"LANGUAGES are made of STRINGS, not {lang_value}, you IDIOT")

    except (AttributeError, KeyError, ValueError):
        logger.warning(f"Selected language doesn't contain {lang_key}, using that instead")

    return lang_key


def _translate_nest(lang_key: str, sub_dict: dict = None) -> str:
    """
    Calls _translate_simple recursively (if it has to) for dicts in lang by
    using dotted notation in the lang key, like
    _translate_nest("item_names.agi_boots").
    """
    logger.debug(f"Translating {lang_key}")
    
    if SUB_DICT_SEPARATOR in lang_key:
        sub_dict_name, sub_dict_key = lang_key.split(SUB_DICT_SEPARATOR, 1)
        if sub_dict is None:
            lang_text = LANGUAGES[settings.get("language")]
            next_sub_dict = getattr(lang_text, sub_dict_name)
        else:
            next_sub_dict = sub_dict[sub_dict_name]


        return _translate_nest(
            sub_dict_key,
            next_sub_dict,
        )

    else:
        return _translate_simple(lang_key, sub_dict)


def translate(lang_key: str | tuple[str]) -> str | tuple[str]:
    """
    Calls _translate_nest recursively (if it has too) for tuples of lang keys.
    """
    if isinstance(lang_key, tuple):
        return tuple(map(translate, lang_key))
    elif isinstance(lang_key, str):
        return _translate_nest(lang_key)


def f(fstring: str, *args: object) -> str:
    """Shorthand for fstring.format(*args)."""
    return fstring.format(*args)


logger = logging.getLogger(__name__)

ENGLISH = _Lang(
    # Dialog
    welcome = "Welcome adventurer ! ...asdf. \n(press Space or Enter)",
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
        "goblin_chieftain": "Goblin chieftain",
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
      # "item_name": "Item Name",
        "agi_boots": "Hermes' Boots",
        "potion_health": "Potion of Healing",
        "str_helmet": "Helmet of Strength",
        "sword": "Sword",
        "dagger": "Dagger",
    },
    item_descriptions = {
    #   "item_name": "Item Description",
        "agi_boots": "A pair of boots with suspicious wings",
        "potion_health": "Heals ♥ 5 when consumed",
        "str_helmet": "A spartan helmet, enchanted with a strength spell",
        "sword": "An elegant weapon, from a more civilised time",
        "dagger": "A pointy little thing",
    },

    # Actions
    action_names = {
      # "action_name": "Action Name",
        "light_stab": "Light Stab",
        "slash": "Slash",
        "stab": "Stab",
    },
    action_descriptions = {
      # "action_name": "Action Description",
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
    welcome = "Bienvenue aventurier ! ...asdf. \n(appuyez sur Espace ou Entrée)",
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
        "goblin": "Goblin",
        "hobgoblin": "Hobgoblin",
        "goblin_chieftain": "Chef goblin",
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
      # "item_name": "Item Name",
        "agi_boots": "Bottes de Hermes",
        "potion_health": "Potion de Guérison",
        "str_helmet": "Heaume de Force",
        "sword": "Épée",
        "dagger": "Dague",
    },
    item_descriptions = {
    #   "item_name": "Item Description",
        "agi_boots": "Une pair de bottes avec des ailes suspicieuses",
        "potion_health": "Guérit ♥ 5 lors de consommation",
        "str_helmet": "Une heaume spartane, enchantée avec un sort de force",
        "sword": "Un truc pointu",
        "dagger": "Un autre truc pointu",
    },

    # Actions
    action_names = {
      # "action_name": "Action Name",
        "light_stab": "Coup de couteau",
        "slash": "Coup d'épée",
        "stab": "Coup de pointe",
    },
    action_descriptions = {
      # "action_name": "Action Description",
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
