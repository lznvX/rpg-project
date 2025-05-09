"""Utility script to create and edit ressource pickle files

Run in terminal, Thonny doesn't work for me. Purpose is to keep a human readable version of these
ressources to easily modify them.

Contributors:
    Romain
"""

import pickle
from common import Character, EnumObject, EVENT_TYPES
from world import WORLD_OBJECT_TYPES
from cuinter import UI_ELEMENT_TYPES, RECTANGLE_PRESETS
from settings import SETTING_TYPES
from lang import LANGUAGE_ENUM

objects = {
    "assets\\ui_elements\\dialogs\\welcome_dialog.pkl": EnumObject(
        UI_ELEMENT_TYPES.DIALOG_BOX,
        {
            "dialog": (
                "welcome",
                ("i_move_u_up", "romain"),
                EnumObject(
                    EVENT_TYPES.PRESS_KEY,
                    ord("w"),
                ),
            ),
        },
    ),
    "assets\\ui_elements\\dialogs\\what_dialog.pkl": EnumObject(
        UI_ELEMENT_TYPES.DIALOG_BOX,
        {
            "dialog": (
                "what",
            ),
        },
    ),
    "assets\\ui_elements\\choices\\menu_choice.pkl": EnumObject(
        UI_ELEMENT_TYPES.CHOICE_BOX,
        {
            "options": (
                "menu_inventory",
                "menu_settings",
                "menu_save",
                "menu_load",
                "menu_save_quit",
                "menu_test_combat",
                "menu_close",
            ),
            "on_confirm_events": {
                0: EnumObject(
                    EVENT_TYPES.LOAD_UI_ELEMENT,
                    "assets\\ui_elements\\choices\\inventory_choice.pkl",
                ),
                1: EnumObject(
                    EVENT_TYPES.LOAD_UI_ELEMENT,
                    "assets\\ui_elements\\choices\\settings_choice.pkl",
                ),
                2: EnumObject(
                    EVENT_TYPES.SAVE_GAME,
                ),
                3: EnumObject(
                    EVENT_TYPES.LOAD_GAME,
                ),
                4: EnumObject(
                    EVENT_TYPES.MULTI_EVENT,
                    (
                        EnumObject(
                            EVENT_TYPES.SAVE_GAME,
                        ),
                        EnumObject(
                            EVENT_TYPES.QUIT,
                        ),
                    ),
                ),
                5: EnumObject(
                    EVENT_TYPES.LOAD_COMBAT,
                    "assets\\combats\\test_combat.pkl",
                ),
            },
            "rectangle_preset": RECTANGLE_PRESETS.MENU,
        },
    ),
    "assets\\ui_elements\\choices\\settings_choice.pkl": EnumObject(
        UI_ELEMENT_TYPES.CHOICE_BOX,
        {
            "options": (
                "settings_language",
                "settings_1",
                "settings_2",
                "menu_back",
            ),
            "on_confirm_events": {
                0: EnumObject(
                    EVENT_TYPES.LOAD_UI_ELEMENT,
                    "assets\\ui_elements\\choices\\language_choice.pkl",
                ),
                3: EnumObject(
                    EVENT_TYPES.LOAD_UI_ELEMENT,
                    "assets\\ui_elements\\choices\\menu_choice.pkl",
                ),
            },
            "rectangle_preset": RECTANGLE_PRESETS.MENU,
        },
    ),
    "assets\\ui_elements\\choices\\language_choice.pkl": EnumObject(
        UI_ELEMENT_TYPES.CHOICE_BOX,
        {
            "options": (
                "English",
                "Français",
                "menu_back",
            ),
            "on_confirm_events": {
                0: EnumObject(
                    EVENT_TYPES.SET_SETTING,
                    EnumObject(
                        SETTING_TYPES.LANGUAGE,
                        LANGUAGE_ENUM.ENGLISH,
                    ),
                ),
                1: EnumObject(
                    EVENT_TYPES.SET_SETTING,
                    EnumObject(
                        SETTING_TYPES.LANGUAGE,
                        LANGUAGE_ENUM.FRENCH,
                    ),
                ),
                2: EnumObject(
                    EVENT_TYPES.LOAD_UI_ELEMENT,
                    "assets\\ui_elements\\choices\\settings_choice.pkl",
                ),
            },
            "rectangle_preset": RECTANGLE_PRESETS.MENU,
        },
    ),
    "assets\\zones\\test_zone.pkl": (
        (
            "╝│ │ │╚╗XXXX",
            "─┘ │ │ ║XXXX",
            "╗┌─┘ │ ╚═══╗",
            "╝└┐  └────┐║",
            "──┘┌───┐  │║",
            "╗  │   │┌─┘║",
            "╚═╗│╔═╗││╔═╝",
        ),
        (
            EnumObject(
                WORLD_OBJECT_TYPES.WALK_TRIGGER,
                (
                    0,
                    3,
                    EnumObject(
                        EVENT_TYPES.LOAD_ZONE,
                        (
                            "assets\\zones\\test_zone.pkl",
                            6,
                            3,
                        ),
                    ),
                    ord("w"),
                ),
            ),
            EnumObject(
                WORLD_OBJECT_TYPES.WALK_TRIGGER,
                (
                    6,
                    3,
                    EnumObject(
                        EVENT_TYPES.LOAD_ZONE,
                        (
                            "assets\\zones\\test_zone.pkl",
                            0,
                            3,
                        ),
                    ),
                    ord("s"),
                ),
            ),
            EnumObject(
                WORLD_OBJECT_TYPES.WALK_TRIGGER,
                (
                    1,
                    0,
                    EnumObject(
                        EVENT_TYPES.MULTI_EVENT,
                        (
                            EnumObject(
                                EVENT_TYPES.LOAD_ZONE,
                                (
                                    "assets\\zones\\test_zone_2.pkl",
                                    1,
                                    11,
                                ),
                            ),
                            EnumObject(
                                EVENT_TYPES.LOAD_UI_ELEMENT,
                                "assets\\ui_elements\\dialogs\\what_dialog.pkl",
                            ),
                        ),
                    ),
                    ord("a"),
                ),
            ),
            EnumObject(
                WORLD_OBJECT_TYPES.WALK_TRIGGER,
                (
                    4,
                    0,
                    EnumObject(
                        EVENT_TYPES.LOAD_ZONE,
                        (
                            "assets\\zones\\test_zone_2.pkl",
                            4,
                            11,
                        ),
                    ),
                    ord("a"),
                ),
            ),
        ),
    ),
    "assets\\zones\\test_zone_2.pkl": (
        (
            "XXXX╔╝│ │ │╚",
            "XXXX║ │ │ └─",
            "╔═══╝ │ └─┐╔",
            "║┌────┘  ┌┘╚",
            "║│  ┌───┐└──",
            "║└─┐│   │  ╔",
            "╚═╗││╔═╗│╔═╝",
        ),
        (
            EnumObject(
                WORLD_OBJECT_TYPES.WALK_TRIGGER,
                (
                    0,
                    8,
                    EnumObject(
                        EVENT_TYPES.LOAD_ZONE,
                        (
                            "assets\\zones\\test_zone_2.pkl",
                            6,
                            8,
                        ),
                    ),
                    ord("w"),
                ),
            ),
            EnumObject(
                WORLD_OBJECT_TYPES.WALK_TRIGGER,
                (
                    6,
                    8,
                    EnumObject(
                        EVENT_TYPES.LOAD_ZONE,
                        (
                            "assets\\zones\\test_zone_2.pkl",
                            0,
                            8,
                        ),
                    ),
                    ord("s"),
                ),
            ),
            EnumObject(
                WORLD_OBJECT_TYPES.WALK_TRIGGER,
                (
                    1,
                    11,
                    EnumObject(
                        EVENT_TYPES.LOAD_ZONE,
                        (
                            "assets\\zones\\test_zone.pkl",
                            1,
                            0,
                        ),
                    ),
                    ord("d"),
                ),
            ),
            EnumObject(
                WORLD_OBJECT_TYPES.WALK_TRIGGER,
                (
                    4,
                    11,
                    EnumObject(
                        EVENT_TYPES.LOAD_ZONE,
                        (
                            "assets\\zones\\test_zone.pkl",
                            4,
                            0,
                        ),
                    ),
                    ord("d"),
                ),
            ),
        ),
    ),
}

for path, object_to_save in objects.items():
    with open(path, "wb") as file:
        pickle.dump(object_to_save, file)

print(f"{len(objects)} objects built and saved successfully")
