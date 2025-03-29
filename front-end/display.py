"""Système d'affichage d'interface

OUTDATED
OUTDATED
OUTDATED
OUTDATED
OUTDATED

Contributors:
    Romain
"""

from common import Character, DialogLine, move_toward
import copy
import cuinter
import logging
import math
import time
from typing import NamedTuple

logger = logging.getLogger(__name__)
logging.basicConfig(filename='display.log', encoding='utf-8', level=logging.DEBUG)


def main(stdscr) -> None:
    # Initialisation couleurs curses
    curses.start_color()
    curses.use_default_colors()
    for i in range(curses.COLOR_PAIRS - 1):
        curses.init_pair(i + 1, i, -1)

    curses.curs_set(0) # Cache le curseur
    stdscr.nodelay(1) # Pas de blocage d'entrées
    stdscr.timeout(0) # Délai de vérification d'entrée

    screen_height, screen_width = stdscr.getmaxyx()

    empty_buffer = [[None for _ in range(screen_width)] for _ in range(screen_height)]

    last_time = time.time()
    fps_timer = last_time  # Temps de la dernière mise à jour de l'affichage FPS
    frame_count = 0
    average_fps = 0
    
    dialog = (
        DialogLine("LELOLELOELOLEOLEOLEOLEOLEOLOLEOLOEELOmmmmmmmmmmmmmmmmmm    yeseiurrrrrhjsdhdjhsdjhsdhjsdhjdshjsdjhsdjhdsjhdshjsdhjsdhjsdhjdshjdshdsdssjhgfqwè¨qè¨¨èwq¨qwèwq", Character("Idris")),
        DialogLine("bruh"),
        DialogLine("AAAAAAAAAAAAAAAAAAAAAAAAAAAAA"),
        DialogLine("We're no strangers to love You know the rules and so do I A full commitment's what I'm thinkin' of You wouldn't get this from any other guy I just wanna tell you how I'm feeling Gotta make you understand Never gonna give you up, never gonna let you down Never gonna run around and desert you Never gonna make you cry, never gonna say goodbye Never gonna tell a lie and hurt you We've known each other for so long Your heart's been aching, but you're too shy to say it Inside, we both know what's been going on We know the game and we're gonna play it And if you ask me how I'm feeling Don't tell me you're too blind to see Never gonna give you up, never gonna let you down Never gonna run around and desert you Never gonna make you cry, never gonna say goodbye Never gonna tell a lie and hurt you Never gonna give you up, never gonna let you down Never gonna run around and desert you Never gonna make you cry, never gonna say goodbye Never gonna tell a lie and hurt you We've known each other for so long Your heart's been aching, but you're too shy to say it Inside, we both know what's been going on We know the game and we're gonna play it I just wanna tell you how I'm feeling Gotta make you understand Never gonna give you up, never gonna let you down Never gonna run around and desert you Never gonna make you cry, never gonna say goodbye Never gonna tell a lie and hurt you Never gonna give you up, never gonna let you down Never gonna run around and desert you Never gonna make you cry, never gonna say goodbye Never gonna tell a lie and hurt you Never gonna give you up, never gonna let you down Never gonna run around and desert you Never gonna make you cry, never gonna say goodbye Never gonna tell a lie and hurt you", Character("Rick Astley")),
    )
    dialog_box = cuinter.DialogBox.new(
        screen_height,
        50,
        10,
        screen_width - 100,
        dialog,
    )
    
    options = (
        "haram",
        "harambe",
        "PETAH",
        "The honse is here.",
    )
    choice_box = None
    
    float_dialog_y = float(dialog_box.y)

    while 1:
        current_time = time.time()
        delta_time = current_time - last_time # Temps écoulé depuis la dernière frame
        last_time = current_time

        frame_count += 1
        if current_time - fps_timer >= 1.0:
            average_fps = frame_count / (current_time - fps_timer)
            fps_timer = current_time
            frame_count = 0

        key = stdscr.getch()
        if key == ord(" ") or key == ord("\n"):
            if not dialog_box is None:
                dialog_box = dialog_box.next()
                if dialog_box is None:
                    choice_box = cuinter.ChoiceBox.new(
                        screen_height - 12,
                        50,
                        10,
                        screen_width - 100,
                        options,
                    )
        elif key == curses.KEY_UP:
            if not choice_box is None:
                choice_box = choice_box.select_previous()
        elif key == curses.KEY_DOWN:
            if not choice_box is None:
                choice_box = choice_box.select_next()
        elif key == ord("q"):
            break

        stdscr.clear()
        
        buffer = copy.deepcopy(empty_buffer)
        
        if not dialog_box is None:
            dialog_target_y = screen_height if dialog_box.start_time is None else screen_height - 12
            if dialog_box.y != dialog_target_y:
                float_dialog_y = move_toward(float_dialog_y, dialog_target_y, delta_time * 100)
                dialog_box = dialog_box.config(y=round(float_dialog_y))
            dialog_box = dialog_box.draw(buffer)
        
        if not choice_box is None:
            choice_box = choice_box.draw(buffer)
        
        display_buffer(stdscr, buffer)
        stdscr.addstr(0, 0, f"FPS : {round(average_fps)}")

        stdscr.refresh()


cuinter.start()
