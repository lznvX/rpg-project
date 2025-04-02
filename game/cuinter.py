"""Interface and display for curses

Basically a tkinter clone at this point.

Contributors:
    Romain
"""

from common import DialogLine, UIEvent, move_toward
import copy
import ctypes
import curses
import logging
import math
import time
from typing import NamedTuple
import uuid

X_CORRECTION = 2.6 # Hauteur / largeur d'un caractère
CHARACTER_TIME = 0.025 # Délai d'affichage de chaque caractère dans les textes

logger = logging.getLogger(__name__)
logging.basicConfig(filename='cuinter.log', encoding='utf-8', level=logging.DEBUG)


class Label(NamedTuple):
    pid: int # Persistent identifier, ask Romain
    y: int
    x: int
    text: str = None
    color: int = 255
    
    @classmethod
    def new(cls, y: int, x: int, text: str = None, color: int = 255, is_top_level: bool = True) -> "Label":
        pid = int(uuid.uuid4())
        label = cls(pid, y, x, text, color)
        
        if is_top_level:
            set_element(pid, label)
            logger.debug("Created new Label")
        return label
    
    def config(self, is_top_level: bool = True, **kwargs) -> "Label":
        label = Label(
            self.pid,
            kwargs.get("y", self.y),
            kwargs.get("x", self.x),
            kwargs.get("text", self.text),
            kwargs.get("color", self.color),
        )
        
        if is_top_level: set_element(self.pid, label)
        return label
    
    def delete(self) -> None:
        remove_element(self.pid)
    
    def draw(self, buffer: list[list[tuple[str, int]]]) -> None:
        if self.text is None: return
        
        for i, char in enumerate(self.text):
            _set_cell(buffer, self.y, self.x + i, char)


class Rectangle(NamedTuple):
    pid: int
    y: int
    x: int
    height: int
    width: int
    color: int = 255
    
    @classmethod
    def new(cls, y: int, x: int, height: int, width: int, color: int = 255, is_top_level: bool = True) -> "Rectangle":
        pid = int(uuid.uuid4())
        rectangle = cls(pid, y, x, height, width, color)
        
        if is_top_level:
            set_element(pid, rectangle)
            logger.debug("Created new Rectangle")
        return rectangle
    
    def config(self, is_top_level: bool = True, **kwargs) -> "Rectangle":
        rectangle = Rectangle(
            self.pid,
            kwargs.get("y", self.y),
            kwargs.get("x", self.x),
            kwargs.get("height", self.height),
            kwargs.get("width", self.width),
            kwargs.get("color", self.color),
        )
        
        if is_top_level: set_element(self.pid, rectangle)
        return rectangle
    
    def delete(self) -> None:
        remove_element(self.pid)
    
    def draw(self, buffer: list[list[tuple[str, int]]]) -> None:
        if self.height <= 0 or self.width <= 0: return
        
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
                _set_cell(buffer, y, x, None)
        
        for x in range(x1 + 1, x2):
            _set_cell(buffer, y1, x, "─", self.color)
            _set_cell(buffer, y2, x, "─", self.color)


class TextBox(NamedTuple):
    pid: int
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
        pid = int(uuid.uuid4())
        text_box = cls(
            pid,
            Rectangle.new(y, x, height, width, 255, False),
            text,
        )
        
        if is_top_level:
            set_element(pid, text_box)
            logger.debug("Created new TextBox")
        return text_box
    
    def config(self, is_top_level: bool = True, **kwargs) -> "TextBox":
        text_box = TextBox(
            self.pid,
            self.rectangle.config(False, **kwargs),
            kwargs.get("text", self.text),
        )
        
        if is_top_level: set_element(self.pid, text_box)
        return text_box
    
    def delete(self) -> None:
        remove_element(self.pid)
    
    def draw(self, buffer: list[list[tuple[str, int]]]) -> None:
        self.rectangle.draw(buffer)
        
        if self.text is None: return
        
        text_y = self.y + 2
        text_x = self.x + 3
        wrap = self.width - 5
        
        for i, char in enumerate(self.text):
            _set_cell(buffer, text_y + i // wrap, text_x + i % wrap, char)


class DialogBox(NamedTuple):
    pid: int
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
        pid = int(uuid.uuid4())
        dialog_box = cls(
            pid,
            TextBox.new(y, x, height, width, None, False),
            dialog,
            time.time(),
            0,
        )
        
        if is_top_level:
            set_element(pid, dialog_box)
            logger.debug("Created new DialogBox")
        return dialog_box
    
    def config(self, is_top_level: bool = True, **kwargs) -> "DialogBox":
        dialog_box = DialogBox(
            self.pid,
            self.text_box.config(False, **kwargs),
            kwargs.get("dialog", self.dialog),
            kwargs.get("start_time", self.start_time),
            kwargs.get("line_index", self.line_index),
        )
        
        if is_top_level: set_element(self.pid, dialog_box)
        return dialog_box
    
    def delete(self) -> None:
        remove_element(self.pid)
    
    def next(self) -> None:
        if math.floor((time.time() - self.start_time) / CHARACTER_TIME) <= len(self.dialog_line.text):
            self.config(start_time=0)
        elif self.line_index + 1 < len(self.dialog):
            self.config(start_time=time.time(), line_index=self.line_index + 1)
        else:
            self.delete()
    
    def draw(self, buffer: list[list[tuple[str, int]]]) -> None:
        length_to_draw = min(math.floor((time.time() - self.start_time) / CHARACTER_TIME), len(self.dialog_line.text))
        formatted_text = ((f"[{self.dialog_line.character.name}]: " if not self.dialog_line.character is None else "")
                          + self.dialog_line.text[:length_to_draw])
        
        self.config(text=formatted_text)
        get_elements()[self.pid].text_box.draw(buffer)


class ChoiceBox(NamedTuple):
    pid: int
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
        pid = int(uuid.uuid4())
        choice_box = cls(
            pid,
            TextBox.new(y, x, height, width, None, False),
            options,
            selected_index,
        )
        
        if is_top_level:
            set_element(pid, choice_box)
            logger.debug("Created new ChoiceBox")
        return choice_box
    
    def config(self, is_top_level: bool = True, **kwargs) -> "ChoiceBox":
        choice_box = ChoiceBox(
            self.pid,
            self.text_box.config(False, **kwargs),
            kwargs.get("options", self.options),
            kwargs.get("selected_index", self.selected_index),
        )
        
        if is_top_level: set_element(self.pid, choice_box)
        return choice_box
    
    def delete(self) -> None:
        remove_element(self.pid)
    
    def select_previous(self) -> None:
        self.config(selected_index=move_toward(self.selected_index, 0))
    
    def select_next(self) -> None:
        self.config(selected_index=move_toward(self.selected_index, len(self.options) - 1))
    
    def confirm(self) -> None:
        self.delete()
    
    def draw(self, buffer: list[list[tuple[str, int]]]) -> None:
        formatted_text = ""
        for i, option in enumerate(self.options):
            formatted_line = ("> " if i == self.selected_index else "  ") + option
            formatted_text += formatted_line.ljust((self.width - 5) * 2)
        
        self.config(text=formatted_text)
        get_elements()[self.pid].text_box.draw(buffer)


def _set_cell(buffer: list[list[tuple[str, int]]], y: int, x: int, char: str = "█", color: int = 255) -> None:
    """
    Sets the cell at position y x of the provided buffer without index errors.
    """
    if 0 <= y < len(buffer) and 0 <= x < len(buffer[0]):
        buffer[y][x] = (char, color) if not char is None else None


def _fullscreen() -> None:
    """Simulates the F11 key being pressed."""
    user32 = ctypes.windll.user32
    user32.keybd_event(0x7A, 0, 0, 0)
    user32.keybd_event(0x7A, 0, 0x0002, 0)


def _display_buffer(stdscr, buffer: tuple[tuple[tuple[str, int]]]) -> None:
    """
    Displays the buffer in rows instead of individual characters to improve
    performance.
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


def _element_manager():
    elements = {}
    
    def get_elements() -> dict[int, object]:
        return elements
    
    def set_element(pid: int, element: object) -> None:
        nonlocal elements
        elements[pid] = element
    
    def remove_element(pid: int) -> None:
        nonlocal elements
        del elements[pid]
    
    return get_elements, set_element, remove_element


def _event_manager():
    events = []
    
    def get_events() -> list[UIEvent]:
        return events
    
    def add_event(event_type: str, value: object) -> None:
        nonlocal events
        events.append(UIEvent(event_type, value))
    
    def clear_events() -> None:
        nonlocal events
        events.clear()
    
    return get_events, add_event, clear_events


def mainloop() -> dict[str, object]:
    """
    Draws the ui elements and processes inputs, returns a dictionary of events
    for main.py to handle.
    """
    
    # Input updating
    
    key = stdscr.getch()
    
    if not key is None:
        for element in reversed(get_elements().values()):
            try:
                element.key_pressed(key)
            except AttributeError:
                continue
            else:
                break
        else:
            add_event("key_pressed", key)
    
    # Display updating
    
    buffer = copy.deepcopy(empty_buffer)

    for element in get_elements().values():
        element.draw(buffer)
    
    stdscr.clear()
    _display_buffer(stdscr, buffer)
    stdscr.refresh()
    
    return get_events()


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

get_elements, set_element, remove_element = _element_manager()
get_events, add_event, clear_events = _event_manager()
