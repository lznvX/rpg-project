"""
Système d'affichage d'interface.

Contributors:
    Romain
"""

from common import Stats, DamageInstance, Character, Action
import copy
import curses
import ctypes
import logging
import math
import time
from typing import NamedTuple

X_CORRECTION = 2.6 # Hauteur / largeur d'un caractère
CHARACTER_TIME = 0.025 # Délai d'affichage de chaque caractère dans les textes


class DialogLine(NamedTuple):
    text: str
    character: Character = None


class Rectangle(NamedTuple):
    y: int
    x: int
    height: int
    width: int
    color: int = 255
    
    @classmethod
    def new(cls, y: int, x: int, height: int, width: int, color: int = 255) -> "Rectangle":
        return cls(y, x, height, width, color)
    
    def config(self, **kwargs) -> "Rectangle":
        return Rectangle(
            kwargs.get("y", self.y),
            kwargs.get("x", self.x),
            kwargs.get("height", self.height),
            kwargs.get("width", self.width),
            kwargs.get("color", self.color),
        )
    
    def draw(self, buffer: list[list[tuple[str, int]]]) -> None:
        if self.height <= 0 or self.width <= 0:
            return
        
        y1, y2 = self.y, self.y + self.height
        x1, x2 = self.x, self.x + self.width
        
        set_cell(buffer, y1, x1, "┌", self.color)
        set_cell(buffer, y1, x2, "┐", self.color)
        set_cell(buffer, y2, x1, "└", self.color)
        set_cell(buffer, y2, x2, "┘", self.color)
        
        for y in range(y1 + 1, y2):
            set_cell(buffer, y, x1, "│", self.color)
            set_cell(buffer, y, x2, "│", self.color)
        
        for x in range(x1 + 1, x2):
            set_cell(buffer, y1, x, "─", self.color)
            set_cell(buffer, y2, x, "─", self.color)


class TextBox(NamedTuple):
    rectangle: Rectangle
    text: str = None
    
    @property
    def y(self) -> int:
        return self.rectangle.y
    
    @property
    def x(self) -> int:
        return self.rectangle.x
    
    @property
    def height(self) -> int:
        return self.rectangle.height
    
    @property
    def width(self) -> int:
        return self.rectangle.width
    
    @classmethod
    def new(cls, y: int, x: int, height: int, width: int, text: str = None) -> "TextBox":
        return cls(
            Rectangle(y, x, height, width),
            text,
        )
    
    def config(self, **kwargs) -> "TextBox":
        return TextBox(
            self.rectangle.config(**kwargs),
            kwargs.get("text", self.text),
        )
    
    def draw(self, buffer: list[list[tuple[str, int]]]) -> None:
        self.rectangle.draw(buffer)
        
        if self.text is None: return
        
        text_y = self.y + 2
        text_x = self.x + 3
        wrap = self.width - 5
        
        for i in range(len(self.text)):
            set_cell(buffer, text_y + i // wrap, text_x + i % wrap, self.text[i])


class DialogBox(NamedTuple):
    text_box: TextBox
    dialog: tuple[DialogLine, ...]
    start_time: float
    line_index: int = 0
    
    @property
    def y(self) -> int:
        return self.text_box.y
    
    @property
    def x(self) -> int:
        return self.text_box.x
    
    @property
    def height(self) -> int:
        return self.text_box.height
    
    @property
    def width(self) -> int:
        return self.text_box.width
    
    @property
    def dialog_line(self) -> DialogLine:
        return self.dialog[self.line_index]
    
    @classmethod
    def new(cls, y: int, x: int, height: int, width: int, dialog: tuple[DialogLine, ...]) -> "DialogBox":
        return cls(
            TextBox.new(y, x, height, width),
            dialog,
            time.time(),
            0,
        )
    
    def config(self, **kwargs) -> "DialogBox":
        return DialogBox(
            self.text_box.config(**kwargs),
            kwargs.get("dialog", self.dialog),
            kwargs.get("start_time", self.start_time),
            kwargs.get("line_index", self.line_index),
        )
    
    def next(self) -> "DialogBox":
        if math.floor((time.time() - self.start_time) / CHARACTER_TIME) <= len(self.dialog[self.line_index].text):
            return DialogBox(
                self.text_box,
                self.dialog,
                0,
                self.line_index,
            )
        elif self.line_index + 1 < len(self.dialog):
            return DialogBox(
                self.text_box,
                self.dialog,
                time.time(),
                self.line_index + 1,
            )
        else:
            return None
    
    def draw(self, buffer: list[list[tuple[str, int]]]) -> "DialogBox":
        length_to_draw = min(math.floor((time.time() - self.start_time) / CHARACTER_TIME), len(self.dialog[self.line_index].text))
        formatted_text = ((f"[{self.dialog_line.character.name}]: " if not self.dialog_line.character is None else "")
            + self.dialog[self.line_index].text[:length_to_draw])
        
        updated_self = self.config(text=formatted_text)
        updated_self.text_box.draw(buffer)
        return updated_self


class ChoiceBox(NamedTuple):
    text_box: TextBox
    options: tuple[str, ...]
    selected_index: int = 0
    
    @property
    def y(self) -> int:
        return self.text_box.y
    
    @property
    def x(self) -> int:
        return self.text_box.x
    
    @property
    def height(self) -> int:
        return self.text_box.height
    
    @property
    def width(self) -> int:
        return self.text_box.width
    
    @property
    def selected_option(self) -> str:
        return self.options[self.selected_index]
    
    @classmethod
    def new(cls, y: int, x: int, height: int, width: int, options: tuple[str, ...], selected_index: int = 0) -> "ChoiceBox":
        return cls(
            TextBox.new(y, x, height, width),
            options,
            selected_index,
        )
    
    def config(self, **kwargs) -> "ChoiceBox":
        return ChoiceBox(
            self.text_box.config(**kwargs),
            kwargs.get("options", self.options),
            kwargs.get("selected_index", self.selected_index),
        )
    
    def select_previous(self) -> "ChoiceBox":
        return ChoiceBox(
            self.text_box,
            self.options,
            move_toward(self.selected_index, 0),
        )
    
    def select_next(self) -> "ChoiceBox":
        return ChoiceBox(
            self.text_box,
            self.options,
            move_toward(self.selected_index, len(self.options) - 1),
        )
    
    def confirm(self) -> int:
        return self.selected_option
    
    def draw(self, buffer: list[list[tuple[str, int]]]) -> "ChoiceBox":
        formatted_text = ""
        for i, option in enumerate(self.options):
            formatted_line = ("> " if i == self.selected_index else "  ") + option
            formatted_text += formatted_line.ljust((self.width - 5) * 2)
        
        updated_self = self.config(text=formatted_text)
        updated_self.text_box.draw(buffer)
        return updated_self


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
    
    dialog = (
        DialogLine("LELOLELOELOLEOLEOLEOLEOLEOLOLEOLOEELOmmmmmmmmmmmmmmmmmm    yeseiurrrrrhjsdhdjhsdjhsdhjsdhjdshjsdjhsdjhdsjhdshjsdhjsdhjsdhjdshjdshdsdssjhgfqwè¨qè¨¨èwq¨qwèwq", Character("Idris")),
        DialogLine("bruh"),
        DialogLine("AAAAAAAAAAAAAAAAAAAAAAAAAAAAA"),
        DialogLine("We're no strangers to love You know the rules and so do I A full commitment's what I'm thinkin' of You wouldn't get this from any other guy I just wanna tell you how I'm feeling Gotta make you understand Never gonna give you up, never gonna let you down Never gonna run around and desert you Never gonna make you cry, never gonna say goodbye Never gonna tell a lie and hurt you We've known each other for so long Your heart's been aching, but you're too shy to say it Inside, we both know what's been going on We know the game and we're gonna play it And if you ask me how I'm feeling Don't tell me you're too blind to see Never gonna give you up, never gonna let you down Never gonna run around and desert you Never gonna make you cry, never gonna say goodbye Never gonna tell a lie and hurt you Never gonna give you up, never gonna let you down Never gonna run around and desert you Never gonna make you cry, never gonna say goodbye Never gonna tell a lie and hurt you We've known each other for so long Your heart's been aching, but you're too shy to say it Inside, we both know what's been going on We know the game and we're gonna play it I just wanna tell you how I'm feeling Gotta make you understand Never gonna give you up, never gonna let you down Never gonna run around and desert you Never gonna make you cry, never gonna say goodbye Never gonna tell a lie and hurt you Never gonna give you up, never gonna let you down Never gonna run around and desert you Never gonna make you cry, never gonna say goodbye Never gonna tell a lie and hurt you Never gonna give you up, never gonna let you down Never gonna run around and desert you Never gonna make you cry, never gonna say goodbye Never gonna tell a lie and hurt you", Character("Rick Astley")),
    )
    dialog_box = DialogBox.new(
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
                    choice_box = ChoiceBox.new(
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


time.sleep(0.5)
fullscreen()
time.sleep(0.5)
logger = logging.getLogger(__name__)
logging.basicConfig(filename='dialog.log', encoding='utf-8', level=logging.DEBUG)
curses.wrapper(main)
