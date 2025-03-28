"""
Système de gestion d'interface pour curses.

Contributors:
    Romain
"""

from common import DialogLine, move_toward
import copy
import ctypes
import curses
import logging
import math
import time
from typing import NamedTuple

X_CORRECTION = 2.6 # Hauteur / largeur d'un caractère
CHARACTER_TIME = 0.025 # Délai d'affichage de chaque caractère dans les textes

logger = logging.getLogger(__name__)
logging.basicConfig(filename='cuinter.log', encoding='utf-8', level=logging.DEBUG)

stdscr = None
screen_height = None
screen_width = None
empty_buffer = None

ui_elements = []

class Label(NamedTuple):
    y: int
    x: int
    text: str = None
    color: int = 255
    
    @classmethod
    def new(cls, y: int, x: int, text: str = None, color: int = 255, is_top_level: bool = True) -> "Rectangle":
        label = cls(y, x, text, color)
        
        if is_top_level:
            ui_elements.append(label)
            logger.debug("Created new Label")
        
        return label
    
    def config(self, **kwargs) -> "Label":
        return Label(
            kwargs.get("y", self.y),
            kwargs.get("x", self.x),
            kwargs.get("text", self.text),
            kwargs.get("color", self.color),
        )
    
    def draw(self, buffer: list[list[tuple[str, int]]]) -> "Label":
        if self.text is None: return self
        
        for i, char in enumerate(self.text):
            _set_cell(buffer, self.y, text_x + i, char)
        
        return self


class Rectangle(NamedTuple):
    y: int
    x: int
    height: int
    width: int
    color: int = 255
    
    @classmethod
    def new(cls, y: int, x: int, height: int, width: int, color: int = 255, is_top_level: bool = True) -> "Rectangle":
        rectangle = cls(y, x, height, width, color)
        
        if is_top_level:
            ui_elements.append(rectangle)
            logger.debug("Created new Rectangle")
        
        return rectangle
    
    def config(self, **kwargs) -> "Rectangle":
        return Rectangle(
            kwargs.get("y", self.y),
            kwargs.get("x", self.x),
            kwargs.get("height", self.height),
            kwargs.get("width", self.width),
            kwargs.get("color", self.color),
        )
    
    def draw(self, buffer: list[list[tuple[str, int]]]) -> "Rectangle":
        if self.height <= 0 or self.width <= 0: return self
        
        y1, y2 = self.y, self.y + self.height
        x1, x2 = self.x, self.x + self.width
        
        _set_cell(buffer, y1, x1, "┌", self.color)
        _set_cell(buffer, y1, x2, "┐", self.color)
        _set_cell(buffer, y2, x1, "└", self.color)
        _set_cell(buffer, y2, x2, "┘", self.color)
        
        for y in range(y1 + 1, y2):
            _set_cell(buffer, y, x1, "│", self.color)
            _set_cell(buffer, y, x2, "│", self.color)
        
        for x in range(x1 + 1, x2):
            _set_cell(buffer, y1, x, "─", self.color)
            _set_cell(buffer, y2, x, "─", self.color)
        
        return self

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
    def new(cls, y: int, x: int, height: int, width: int, text: str = None, is_top_level: bool = True) -> "TextBox":
        text_box = cls(
            Rectangle.new(y, x, height, width, 255, False),
            text,
        )
        
        if is_top_level:
            ui_elements.append(text_box)
            logger.debug("Created new TextBox")
        
        return text_box
    
    def config(self, **kwargs) -> "TextBox":
        return TextBox(
            self.rectangle.config(**kwargs),
            kwargs.get("text", self.text),
        )
    
    def draw(self, buffer: list[list[tuple[str, int]]]) -> "TextBox":
        self.rectangle.draw(buffer)
        
        if self.text is None: return self
        
        text_y = self.y + 2
        text_x = self.x + 3
        wrap = self.width - 5
        
        for i, char in enumerate(self.text):
            _set_cell(buffer, text_y + i // wrap, text_x + i % wrap, char)
        
        return self


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
    def new(cls, y: int, x: int, height: int, width: int, dialog: tuple[DialogLine, ...], is_top_level: bool = True) -> "DialogBox":
        dialog_box = cls(
            TextBox.new(y, x, height, width, None, False),
            dialog,
            time.time(),
            0,
        )
        
        if is_top_level:
            ui_elements.append(dialog_box)
            logger.debug("Created new DialogBox")
        
        return dialog_box
    
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
    def new(cls, y: int, x: int, height: int, width: int, options: tuple[str, ...], selected_index: int = 0, is_top_level: bool = True) -> "ChoiceBox":
        choice_box = cls(
            TextBox.new(y, x, height, width, None, False),
            options,
            selected_index,
        )
        
        if is_top_level:
            ui_elements.append(choice_box)
            logger.debug("Created new ChoiceBox")
        
        return choice_box
    
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


def _set_cell(buffer: list[list[tuple[str, int]]], y: int, x: int, char: str = "█", color: int = 255) -> None:
    """Remplace la cellule à la position y x du buffer sans erreurs d'index."""
    if 0 <= y < len(buffer) and 0 <= x < len(buffer[0]):
        buffer[y][x] = (char, color) if not char is None else None


def _fullscreen() -> None:
    """Simule la pression de la touche F11."""
    user32 = ctypes.windll.user32
    user32.keybd_event(0x7A, 0, 0, 0)
    user32.keybd_event(0x7A, 0, 0x0002, 0)


def _display_buffer(stdscr, buffer: tuple[tuple[tuple[str, int]]]) -> None:
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
    global stdscr, screen_height, screen_width, empty_buffer
    
    time.sleep(0.5)
    _fullscreen()
    time.sleep(0.5)
    
    stdscr = curses.initscr()
    
    curses.start_color()
    curses.use_default_colors()
    for i in range(curses.COLOR_PAIRS - 1):
        curses.init_pair(i + 1, i, -1)
    
    curses.curs_set(0) # Cache le curseur
    stdscr.nodelay(1) # Pas de blocage d'entrées
    stdscr.timeout(0) # Délai de vérification d'entrée
    
    screen_height, screen_width = stdscr.getmaxyx()
    empty_buffer = [[None for _ in range(screen_width)] for _ in range(screen_height)]


def update() -> None:
    stdscr.clear()
    buffer = copy.deepcopy(empty_buffer)
    
    for i in range(len(ui_elements)):
        ui_elements[i] = ui_elements[i].draw(buffer)
    
    logger.debug(ui_elements)
    _display_buffer(stdscr, buffer)
    stdscr.refresh()
