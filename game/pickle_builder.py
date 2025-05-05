"""Utility script to create and edit ressource pickle files

Run in terminal, Thonny doesn't work for me. Purpose is to keep a human readable version of these
ressources to easily modify them.

Contributors:
    Romain
"""

import pickle
from common import *
import world

objects = {
    "assets\\dialogs\\test_dialog.pkl": (
        "welcome",
        DialogLine("i_move_u_up", Character("Romain")),
        EnumObject(
            EVENT_TYPES.PRESS_KEY,
            ord("w"),
        ),
    ),
    "assets\\dialogs\\test_dialog_2.pkl": (
        "what",
    ),
    "assets\\zones\\test_zone.pkl": world.Zone(
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
                                EVENT_TYPES.START_DIALOG,
                                "assets\\dialogs\\test_dialog_2.pkl",
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
    "assets\\zones\\test_zone_2.pkl": world.Zone(
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
