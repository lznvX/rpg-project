"""
Système d'affichage de dialogues.
WIP
"""

import copy
import curses
import ctypes
import math
import time
from typing import NamedTuple

X_CORRECTION = 2.6 # Hauteur / largeur d'un caractère
CHARACTER_TIME = 0.025 # Délai d'affichage de chaque caractère dans les textes


class Rectangle(NamedTuple):
    y1: int
    x1: int
    y2: int
    x2: int
    color: int = 255
    
    def draw(self, buffer: list[list[tuple[str, int]]]) -> None:
        """Ajoute le rectangle dans le buffer."""
        if self.y1 == self.y2 or self.x1 == self.x2: return
        y1, y2 = min(self.y1, self.y2), max(self.y1, self.y2)
        x1, x2 = min(self.x1, self.x2), max(self.x1, self.x2)
        
        set_cell(buffer, y1, x1, "┌", self.color)
        set_cell(buffer, y1, x2, "┐", self.color)
        set_cell(buffer, y2, x1, "└", self.color)
        set_cell(buffer, y2, x2, "┘", self.color)
        
        for y in range(y1 + 1, y2):
            set_cell(buffer, y, x1, "│", self.color)
            set_cell(buffer, y, x2, "│", self.color)
            for x in range(x1 + 1, x2):
                set_cell(buffer, y, x, None)
        
        for x in range(x1 + 1, x2):
            set_cell(buffer, y1, x, "─", self.color)
            set_cell(buffer, y2, x, "─", self.color)


class Dialog_box(NamedTuple):
    rectangle: Rectangle
    y_offset: int = 0
    x_offset: int = 0
    text: str | tuple[str, ...] = None
    text_part: int = 0
    start_time: float = None
    
    @property
    def current_text(self) -> str:
        return self.text if isinstance(self.text, str) or self.text is None else self.text[self.text_part]
    
    def set_offset(self, y: int = 0, x: int = 0) -> "Dialog_box":
        return Dialog_box(
            self.rectangle,
            y,
            x,
            self.text,
            self.text_part,
            self.start_time,
        )
    
    def start(self, text: str | tuple[str, ...] = None) -> "Dialog_box":
        if text is None and self.text in None: return self
        return Dialog_box(
            self.rectangle,
            self.y_offset,
            self.x_offset,
            self.text if text is None else text,
            0,
            time.time(),
        )
    
    def next(self) -> "Dialog_box":
        """
        Met à jour tout le texte d'un coup ou passe à la partie d'après si le
        texte est déjà fini.
        """
        if self.start_time is None: return self
        if math.floor((time.time() - self.start_time) / CHARACTER_TIME) <= len(self.current_text):
            return Dialog_box(
                self.rectangle,
                self.y_offset,
                self.x_offset,
                self.text,
                self.text_part,
                0,
            )
        elif isinstance(self.text, str) or self.text_part + 1 >= len(self.text):
            return Dialog_box(
                self.rectangle,
                self.y_offset,
                self.x_offset,
            )
        else:
            return Dialog_box(
                self.rectangle,
                self.y_offset,
                self.x_offset,
                self.text,
                self.text_part + 1,
                time.time(),
            )
    
    def draw(self, buffer: list[list[tuple[str, int]]]) -> None:
        """
        Ajoute le rectangle de la boîte de dialogue et le texte
        (progressivement) dans le buffer.
        """
        if self.y_offset == 0 and self.x_offset == 0:
            self.rectangle.draw(buffer)
        else:
            Rectangle(
                self.rectangle.y1 + self.y_offset,
                self.rectangle.x1 + self.x_offset,
                self.rectangle.y2 + self.y_offset,
                self.rectangle.x2 + self.x_offset,
                self.rectangle.color,
            ).draw(buffer)
        
        if self.start_time is None: return
        
        y1, y2 = min(self.rectangle.y1, self.rectangle.y2), max(self.rectangle.y1, self.rectangle.y2)
        x1, x2 = min(self.rectangle.x1, self.rectangle.x2), max(self.rectangle.x1, self.rectangle.x2)
        
        text_y = y1 + self.y_offset + 2
        text_x = x1 + self.x_offset + 3
        wrap = x2 - x1 - 5
        length_to_draw = min(math.floor((time.time() - self.start_time) / CHARACTER_TIME), len(self.current_text))
        
        for i in range(length_to_draw):
            set_cell(buffer, text_y + i // wrap, text_x + i % wrap, self.current_text[i])


def move_toward(a: int | float, b: int | float, step: int | float = 1) -> int | float:
    return min(a + step, b) if b >= a else max(a - step, b)


def set_cell(buffer: list[list[tuple[str, int]]], y: int, x: int, char: str = "█", color: int = 255) -> None:
    """Remplace la cellule à la position y x du buffer sans erreurs d'index."""
    if 0 <= y < len(buffer) and 0 <= x < len(buffer[0]):
        buffer[y][x] = (char, color) if not char is None else None
    

def display_buffer(stdscr, buffer: tuple[tuple[tuple[str, int]]]) -> None:
    """
    Affiche le buffer par lignes au lieu de caractères individuels pour
    améliorer les performances.
    """
    for y, row in enumerate(buffer):
        row_str = ""
        prev_x = 0
        first_x = None

        for x, cell in enumerate(row):
            if cell is None: continue
            char, color = cell
            
            if first_x is None:
                row_str += char
                first_x = x
            else:
                row_str += " " * (x - prev_x - 1) + char
            
            prev_x = x
        
        if first_x is None: continue
        if y == len(buffer) - 1 and first_x + len(row_str) == len(buffer[0]):
            row_str = row_str[:-1]
        stdscr.move(y, first_x)
        stdscr.addstr(row_str)


def fullscreen() -> None:
    """Simule la pression de la touche F11."""
    user32 = ctypes.windll.user32
    user32.keybd_event(0x7A, 0, 0, 0)
    user32.keybd_event(0x7A, 0, 0x0002, 0)


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
    
    dialog_rectangle = Rectangle(
        screen_height - 12,
        50,
        screen_height - 2,
        screen_width - 50,
    )
    text = (
        "LELOLELOELOLEOLEOLEOLEOLEOLOLEOLOEELOmmmmmmmmmmmmmmmmmm    yeseiurrrrrhjsdhdjhsdjhsdhjsdhjdshjsdjhsdjhdsjhdshjsdhjsdhjsdhjdshjdshdsdssjhgfqwè¨qè¨¨èwq¨qwèwq",
        "bruh",
        "AAAAAAAAAAAAAAAAAAAAAAAAAAAAA",
        "We're no strangers to love You know the rules and so do I A full commitment's what I'm thinkin' of You wouldn't get this from any other guy I just wanna tell you how I'm feeling Gotta make you understand Never gonna give you up, never gonna let you down Never gonna run around and desert you Never gonna make you cry, never gonna say goodbye Never gonna tell a lie and hurt you We've known each other for so long Your heart's been aching, but you're too shy to say it Inside, we both know what's been going on We know the game and we're gonna play it And if you ask me how I'm feeling Don't tell me you're too blind to see Never gonna give you up, never gonna let you down Never gonna run around and desert you Never gonna make you cry, never gonna say goodbye Never gonna tell a lie and hurt you Never gonna give you up, never gonna let you down Never gonna run around and desert you Never gonna make you cry, never gonna say goodbye Never gonna tell a lie and hurt you We've known each other for so long Your heart's been aching, but you're too shy to say it Inside, we both know what's been going on We know the game and we're gonna play it I just wanna tell you how I'm feeling Gotta make you understand Never gonna give you up, never gonna let you down Never gonna run around and desert you Never gonna make you cry, never gonna say goodbye Never gonna tell a lie and hurt you Never gonna give you up, never gonna let you down Never gonna run around and desert you Never gonna make you cry, never gonna say goodbye Never gonna tell a lie and hurt you Never gonna give you up, never gonna let you down Never gonna run around and desert you Never gonna make you cry, never gonna say goodbye Never gonna tell a lie and hurt you",
    )
    dialog_box = Dialog_box(dialog_rectangle, 12).start(text)
    
    float_dialog_y = float(dialog_box.y_offset)

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
            dialog_box = dialog_box.next()
        elif key == ord("q"):
            break

        stdscr.clear()

        buffer = copy.deepcopy(empty_buffer)
        
        dialog_target_y = abs(dialog_box.rectangle.y2 - dialog_box.rectangle.y1) + 2 if dialog_box.start_time is None else 0
        if dialog_box.y_offset != dialog_target_y:
            float_dialog_y = move_toward(float_dialog_y, dialog_target_y, delta_time * 100)
            dialog_box = dialog_box.set_offset(round(float_dialog_y))
        dialog_box.draw(buffer)
        
        display_buffer(stdscr, buffer)
        stdscr.addstr(0, 0, f"FPS : {round(average_fps)}")

        stdscr.refresh()


time.sleep(0.5)
fullscreen()
time.sleep(0.5)
curses.wrapper(main)
