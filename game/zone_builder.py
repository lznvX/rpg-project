"""Utility script to create and edit zone pickle files

Run in terminal, Thonny doesn't work for me.

Contributors:
    Romain
"""

import pickle
from common import EnumObject, EVENT_TYPES, WORLD_OBJECT_TYPES
import world

zones = {
    "test_zone": world.Zone(
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
    "test_zone_2": world.Zone(
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

for zone_name, zone in zones.items():
    with open(f"assets\\zones\\{zone_name}.pkl", "wb") as file:
        pickle.dump(zone, file)

print(f"{len(zones)} zones built and saved successfully")
