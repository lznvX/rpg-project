"""
Système de gestion d'interface pour curses.

Contributors:
    Romain
"""

from common import DialogLine, move_toward
import copy
import ctypes
import curses
import logger
import math
import time
from typing import NamedTuple

X_CORRECTION = 2.6 # Hauteur / largeur d'un caractère
CHARACTER_TIME = 0.025 # Délai d'affichage de chaque caractère dans les textes
EMPTY_BUFFER = [[None for _ in range(screen_width)] for _ in range(screen_height)]

logger = logging.getLogger(__name__)
logging.basicConfig(filename='cuinter.log', encoding='utf-8', level=logging.DEBUG)

stdscr = None
screen_height = None
screen_width = None

class Rectangle(NamedTuple):
    y: int
    x: int
    height: int
    width: int
    color: int = 255
    
    @classmethod
    def new(cls, y: int, x: int, height: int, width: int, color: int = 255) -> "Rectangle":
        logger.debug("Created new Rectangle")
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
        logger.debug("Created new TextBox")
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
            logger.debug("Created new DialogBox")
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
        logger.debug("Created new ChoiceBox")
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


def set_cell(buffer: list[list[tuple[str, int]]], y: int, x: int, char: str = "█", color: int = 255) -> None:
    """Remplace la cellule à la position y x du buffer sans erreurs d'index."""
    if 0 <= y < len(buffer) and 0 <= x < len(buffer[0]):
        buffer[y][x] = (char, color) if not char is None else None


def fullscreen() -> None:
    """Simule la pression de la touche F11."""
    user32 = ctypes.windll.user32
    user32.keybd_event(0x7A, 0, 0, 0)
    user32.keybd_event(0x7A, 0, 0x0002, 0)


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


def start() -> None:
    time.sleep(0.5)
    fullscreen()
    time.sleep(0.5)
    curses.wrapper(_main)


def update(delta_time: float) -> None:
    


def _main(stdscr_instance) -> None:
    global stdscr
    stdscr = stdscr_instance
    
    
