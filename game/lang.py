"""Language management

Created on 2025.03.17
Contributors:
    Jakub
    Romain
"""

from __future__ import annotations
from typing import NamedTuple


class _LanguageEnum(NamedTuple):
    ENGLISH: int
    FRENCH: int

    @classmethod
    def new(cls) -> _LanguageEnum:
        return cls(*range(len(cls.__annotations__)))


class _Lang(NamedTuple):
    # Dialog
    welcome: str = None
    controls: str = None

    # Choice
    menu_back: str = None
    menu_inventory: str = None
    menu_settings: str = None
    menu_save: str = None
    menu_load: str = None
    menu_close: str = None
    menu_save_quit: str = None
    menu_test_combat: str = None

    settings_language: str = None

    # Combat
    battle_begin: str = None
    battle_win: str = None
    battle_loss: str = None
    battle_rewards: str = None
    battle_turn: str = None

    battle_attack: str = None
    battle_damage: str = None
    battle_death: str = None
    battle_ko: str = None
    battle_action_choice: str = None
    battle_target_choice: str = None

    # Characters
    character_names: dict[str, str] = None

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


def get_lang_choice() -> _Lang:
    """Returns the class with text in the relevant language.

    Language is specified in settings.pkl (not implemented)
    If language is not specified, or settings.pkl file is missing, English is
    used by default.
    """
    return ENGLISH


def f(fstring: str, *args: object) -> str:
    """Shorthand for fstring.format(*args)."""
    return fstring.format(*args)


ENGLISH = _Lang(
    # Dialog
    welcome = "Welcome adventurer ! ...asdf. \n(press Space or Enter)",
    controls = "Controls:\n\nUp: W    Down: S    Left: A    Right: D\nConfirm: Space/Enter    Menu: M",

    # Choice
    menu_back = "Back",
    menu_inventory = "Inventory",
    menu_settings = "Settings",
    menu_save = "Save",
    menu_load = "Load",
    menu_close = "Close menu",
    menu_save_quit = "Save and quit",
    menu_test_combat = "Start combat test",

    settings_language = "Language",

    # Combat
    battle_begin    = "You are now in battle!",
    battle_win      = "You won the battle!",
    battle_loss     = "You lost the battle :(",
    battle_rewards  = "You gain {} gold and {} xp!",
    battle_turn     = "Turn {} begins!",

    battle_attack   = "{} uses {} on {}",
    battle_damage   = "{} takes ¤ {} damage! (♥ {} left)",
    battle_death    = "{} dies!",
    battle_ko       = "{} is knocked out!",
    battle_action_choice    = "What should {} do?",
    battle_target_choice    = "Choose target for {}:",

    # Characters
    character_names = {
        "romain": "Romain",
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

    # Choice
    menu_back = "Retour",
    menu_inventory = "Inventaire",
    menu_settings = "Options",
    menu_save = "Sauvegarder",
    menu_load = "Charger",
    menu_close = "Fermer le menu",
    menu_save_quit = "Sauvegarder et quitter",
    menu_test_combat = "Commencer combat de test",

    settings_language = "Langue",

    # Combat
    battle_begin    = "Vous êtes maintenant en combat !",
    battle_win      = "Vous avez gagné le combat !",
    battle_loss     = "Vous avez perdu le combat :(",
    battle_rewards  = "Vous gagnez {} pièces d'or et {} xp !",
    battle_turn     = "Le tour {} commence !",

    battle_attack   = "{} utilise {} sur {}",
    battle_damage   = "{} prend ¤ {} dégats ! (il lui reste ♥ {})",
    battle_death    = "{} meurt !",
    battle_ko       = "{} est assommé !",
    battle_action_choice    = "Que'est-ce que {} devrait faire ?",
    battle_target_choice    = "Choisissez la cible de {}:",

    # Characters
    character_names = {
        "romain": "Romain",
    },

    # Items
    item_names = {
      # "item_name": "Item Name",
        "agi_boots": "Bottes de Hermes",
        "potion_health": "Potion de Gueérisson",
        "str_helmet": "Heaume de Force",
        "sword": "Épée",
    },
    item_descriptions = {
    #   "item_name": "Item Description",
        "agi_boots": "Une pair de bottes avec des ailes suspicieuses",
        "potion_health": "Guérit ♥ 5 lors de consommation",
        "str_helmet": "Une heaume spartane, enchantée avec un sort de force",
        "sword": "Un truc pointu",
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


LANGUAGE_ENUM = _LanguageEnum.new()
LANGUAGES = {
    LANGUAGE_ENUM.ENGLISH: ENGLISH,
    LANGUAGE_ENUM.FRENCH: FRENCH,
}
