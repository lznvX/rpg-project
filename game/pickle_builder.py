"""Utility script to create and edit ressource pickle files

Run in terminal, Thonny doesn't work for me. Purpose is to keep a human readable version of these
ressources to easily modify them.

Contributors:
    Romain
    Alexander
"""

from common import EnumObject
from enums import (
    EVENT_TYPES,
    UI_ELEMENT_TYPES,
    RECTANGLE_PRESETS,
    WORLD_OBJECT_TYPES,
    LANGUAGE_ENUM,
)
from files import save_pickle

objects = {
    "assets\\dialogs\\welcome_dialog.pkl": EnumObject(
        UI_ELEMENT_TYPES.DIALOG_BOX,
        {
            "dialog": (
                "welcome",
                "controls",
            ),
        },
    ),
    "assets\\choices\\menu_choice.pkl": EnumObject(
        UI_ELEMENT_TYPES.CHOICE_BOX,
        {
            "options": (
                "menu.equipment",
                "menu.backpack",
                "menu.settings",
                "menu.save",
                "menu.load",
                "menu.save_quit",
                "menu.test_combat",
                "menu.close",
            ),
            "on_confirm_events": {
                0: EnumObject(
                    EVENT_TYPES.OPEN_EQUIPMENT,
                ),
                1: EnumObject(
                    EVENT_TYPES.OPEN_BACKPACK,
                ),
                2: EnumObject(
                    EVENT_TYPES.LOAD_UI_ELEMENT,
                    "assets\\choices\\settings_choice.pkl",
                ),
                3: EnumObject(
                    EVENT_TYPES.SAVE_GAME,
                ),
                4: EnumObject(
                    EVENT_TYPES.LOAD_GAME,
                ),
                5: EnumObject(
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
                6: EnumObject(
                    EVENT_TYPES.LOAD_BATTLE,
                    "assets\\combats\\test_battle.pkl",
                ),
            },
            "rectangle_preset": RECTANGLE_PRESETS.MENU,
        },
    ),
    "assets\\choices\\settings_choice.pkl": EnumObject(
        UI_ELEMENT_TYPES.CHOICE_BOX,
        {
            "options": (
                "settings_language",
                "menu.back",
            ),
            "on_confirm_events": {
                0: EnumObject(
                    EVENT_TYPES.LOAD_UI_ELEMENT,
                    "assets\\choices\\language_choice.pkl",
                ),
                1: EnumObject(
                    EVENT_TYPES.LOAD_UI_ELEMENT,
                    "assets\\choices\\menu_choice.pkl",
                ),
            },
            "rectangle_preset": RECTANGLE_PRESETS.MENU,
        },
    ),
    "assets\\choices\\language_choice.pkl": EnumObject(
        UI_ELEMENT_TYPES.CHOICE_BOX,
        {
            "options": (
                "English",
                "Français",
                "menu.back",
            ),
            "on_confirm_events": {
                0: EnumObject(
                    EVENT_TYPES.MULTI_EVENT,
                    (
                        EnumObject(
                            EVENT_TYPES.CONFIG_SETTINGS,
                            {"language": LANGUAGE_ENUM.ENGLISH},
                        ),
                        EnumObject(
                            EVENT_TYPES.LOAD_UI_ELEMENT,
                            "assets\\choices\\settings_choice.pkl",
                        ),
                    ),
                ),
                1: EnumObject(
                    EVENT_TYPES.MULTI_EVENT,
                    (
                        EnumObject(
                            EVENT_TYPES.CONFIG_SETTINGS,
                            {"language": LANGUAGE_ENUM.FRENCH},
                        ),
                        EnumObject(
                            EVENT_TYPES.LOAD_UI_ELEMENT,
                            "assets\\choices\\settings_choice.pkl",
                        ),
                    ),
                ),
                2: EnumObject(
                    EVENT_TYPES.LOAD_UI_ELEMENT,
                    "assets\\choices\\settings_choice.pkl",
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
                        EVENT_TYPES.LOAD_ZONE,
                        (
                            "assets\\zones\\test_zone_2.pkl",
                            1,
                            11,
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
            EnumObject(
                WORLD_OBJECT_TYPES.WALK_TRIGGER,
                (
                    0,
                    8,
                    EnumObject(
                        EVENT_TYPES.LOAD_ZONE,
                        (
                            "assets\\zones\\test_zone_box.pkl",
                            6,
                            8,
                        ),
                    ),
                    ord("w"),
                ),
            ),
        ),
    ),
    "assets\\zones\\test_zone_box.pkl": (
        (
            "XXXXXXXXXXXXX",
            "XXX╔═════╗XXX",
            "XXX║     ║XXX",
            "XXX║     ║XXX",
            "XXX║     ║XXX",
            "XXX║     ║XXX",
            "XXX╚═══╗ ║XXX",
        ),
        (
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
        ),
    ),
}


if __name__ == "__main__":
    for path, obj in objects.items():
        save_pickle(obj, path)

    print(f"{len(objects)} objects built and saved successfully")
