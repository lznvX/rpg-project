"""Main game script

Run with CTRL+T (thonny), currently contains game loop setup, utility labels and
interface tests. If _curses module missing, run pip install windows-curses in
terminal.

OUTDATED : contains input handling, will be put in cuinter

Contributors:
    Romain
"""

from common import Character, DialogLine, move_toward
import cuinter_old as cuinter
import logging
import random
import time

FPS_COUNTER_REFRESH = 1 # Time between each FPS counter update

############ System init

logger = logging.getLogger(__name__)
logging.basicConfig(filename='main.log', encoding='utf-8', level=logging.DEBUG)

cuinter.start()

last_time = time.time()
fps_timer = last_time  # Time of the last FPS update
frame_count = 0

fps_label = cuinter.Label.new(0, 0)

############ Game constants and variables go here

dialog = (
    DialogLine("LELOLELOELOLEOLEOLEOLEOLEOLOLEOLOEELOmmmmmmmmmmmmmmmmmm    yeseiurrrrrhjsdhdjhsdjhsdhjsdhjdshjsdjhsdjhdsjhdshjsdhjsdhjsdhjdshjdshdsdssjhgfqwè¨qè¨¨èwq¨qwèwq", Character("Idris")),
    DialogLine("bruh"),
    DialogLine("AAAAAAAAAAAAAAAAAAAAAAAAAAAAA"),
    DialogLine("We're no strangers to love You know the rules and so do I A full commitment's what I'm thinkin' of You wouldn't get this from any other guy I just wanna tell you how I'm feeling Gotta make you understand Never gonna give you up, never gonna let you down Never gonna run around and desert you Never gonna make you cry, never gonna say goodbye Never gonna tell a lie and hurt you We've known each other for so long Your heart's been aching, but you're too shy to say it Inside, we both know what's been going on We know the game and we're gonna play it And if you ask me how I'm feeling Don't tell me you're too blind to see Never gonna give you up, never gonna let you down Never gonna run around and desert you Never gonna make you cry, never gonna say goodbye Never gonna tell a lie and hurt you Never gonna give you up, never gonna let you down Never gonna run around and desert you Never gonna make you cry, never gonna say goodbye Never gonna tell a lie and hurt you We've known each other for so long Your heart's been aching, but you're too shy to say it Inside, we both know what's been going on We know the game and we're gonna play it I just wanna tell you how I'm feeling Gotta make you understand Never gonna give you up, never gonna let you down Never gonna run around and desert you Never gonna make you cry, never gonna say goodbye Never gonna tell a lie and hurt you Never gonna give you up, never gonna let you down Never gonna run around and desert you Never gonna make you cry, never gonna say goodbye Never gonna tell a lie and hurt you Never gonna give you up, never gonna let you down Never gonna run around and desert you Never gonna make you cry, never gonna say goodbye Never gonna tell a lie and hurt you", Character("Rick Astley")),
)

options = (
    "haram",
    "harambe",
    "PETAH",
    "The honse is here.",
)

############ Code to run on startup goes here

dialog_boxes = []
for i in range(8):
    dialog_boxes.append(cuinter.DialogBox.new(
        random.randrange(0, cuinter.screen_height),
        random.randrange(0, cuinter.screen_width),
        random.randrange(10, 50),
        random.randrange(10, 50),
        dialog,
    ))

choice_box = cuinter.ChoiceBox.new(
    cuinter.screen_height - 12,
    cuinter.screen_width // 4,
    10,
    cuinter.screen_width // 2,
    options,
)

############

while 1:
    current_time = time.time()
    delta_time = current_time - last_time # Time since last frame
    last_time = current_time
    
    frame_count += 1
    if current_time - fps_timer >= FPS_COUNTER_REFRESH:
        average_fps = frame_count / (current_time - fps_timer)
        fps_label.config(text=f"FPS : {round(average_fps)}")
        fps_timer = current_time
        frame_count = 0
    
    ############ Input handling
    
    # match statement no work and bad idea to put in a function
    
    key = cuinter.get_key()
    
    if key in (ord(" "), ord("\n")):
        if len(dialog_boxes) > 0 and not dialog_boxes[-1] is None:
            dialog_boxes[-1] = dialog_boxes[-1].next()
            if dialog_boxes[-1] is None: del dialog_boxes[-1]
        elif not choice_box is None:
            choice = choice_box.confirm()
            choice_box = None
    
    elif key in (cuinter.curses.KEY_UP, ord("w")):
        if not choice_box is None:
            choice_box = choice_box.select_previous()
    
    elif key in (cuinter.curses.KEY_DOWN, ord("s")):
        if not choice_box is None:
            choice_box = choice_box.select_next()
    
    elif key in (cuinter.curses.KEY_LEFT, ord("a")):
        pass
    
    elif key in (cuinter.curses.KEY_RIGHT, ord("d")):
        pass
        
    elif key == ord("q"):
        break
    
    ############ Code to run every frame goes here
    
    
    
    ############
    
    cuinter.update()
