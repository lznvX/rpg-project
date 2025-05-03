"""Utility script to create and edit ressource pickle files

Run in terminal, Thonny doesn't work for me.

Contributors:
    Romain
"""

import pickle
from common import *
import world

objects = {
    "assets\\dialogs\\test_dialog.pkl": (
        DialogLine("LELOLELOELOLEOLEOLEOLEOLEOLOLEOLOEELOmmmmmmmmmmmmmmmmmm    yeseiurrrrrhjsdhdjhsdjhsdhjsdhjdshjsdjhsdjhdsjhdshjsdhjsdhjsdhjdshjdshdsdssjhgfqwè¨qè¨¨èwq¨qwèwq", Character("Idris")),
        DialogLine("bruh"),
        EnumObject(
            EVENT_TYPES.START_DIALOG,
            "assets\\dialogs\\test_dialog_2.pkl",
        ),
        DialogLine("AAAAAAAAAAAAAAAAAAAAAAAAAAAAA"),
        DialogLine("We're no strangers to love You know the rules and so do I A full commitment's what I'm thinkin' of You wouldn't get this from any other guy I just wanna tell you how I'm feeling Gotta make you understand Never gonna give you up, never gonna let you down Never gonna run around and desert you Never gonna make you cry, never gonna say goodbye Never gonna tell a lie and hurt you We've known each other for so long Your heart's been aching, but you're too shy to say it Inside, we both know what's been going on We know the game and we're gonna play it And if you ask me how I'm feeling Don't tell me you're too blind to see Never gonna give you up, never gonna let you down Never gonna run around and desert you Never gonna make you cry, never gonna say goodbye Never gonna tell a lie and hurt you Never gonna give you up, never gonna let you down Never gonna run around and desert you Never gonna make you cry, never gonna say goodbye Never gonna tell a lie and hurt you We've known each other for so long Your heart's been aching, but you're too shy to say it Inside, we both know what's been going on We know the game and we're gonna play it I just wanna tell you how I'm feeling Gotta make you understand Never gonna give you up, never gonna let you down Never gonna run around and desert you Never gonna make you cry, never gonna say goodbye Never gonna tell a lie and hurt you Never gonna give you up, never gonna let you down Never gonna run around and desert you Never gonna make you cry, never gonna say goodbye Never gonna tell a lie and hurt you Never gonna give you up, never gonna let you down Never gonna run around and desert you Never gonna make you cry, never gonna say goodbye Never gonna tell a lie and hurt you", Character("Rick Astley")),
        DialogLine("I am now going to move your character up with my mind.", Character("Romain")),
        EnumObject(
            EVENT_TYPES.PRESS_KEY,
            ord("w"),
        ),
    ),
    "assets\\dialogs\\test_dialog_2.pkl": (
        DialogLine("DIALOG INTERRUPTION"),
        DialogLine("ok you can go back now"),
    ),
    "assets\\dialogs\\test_dialog_3.pkl": (
        DialogLine("DID YOU JUST SEND BOTH A LOAD_ZONE AND A START_DIALOG EVENT WITH A SINGLE WALKTRIGGER ???"),
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
                                "assets\\dialogs\\test_dialog_3.pkl",
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
