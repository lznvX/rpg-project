"""Interface and display for curses

Basically a tkinter clone at this point.

Contributors:
    Romain
"""

from common import DialogLine, UIEvent, move_toward
import copy
import ctypes
import curses
from curses import KEY_UP, KEY_DOWN, KEY_LEFT, KEY_RIGHT
import logging
import math
import time
from typing import NamedTuple
import uuid

PRESSED_KEY = 0
FINISHED_DIALOG = 1
CONFIRMED_CHOICE = 2

X_CORRECTION = 2.6 # Hauteur / largeur d'un caractère
CHARACTER_TIME = 0.025 # Délai d'affichage de chaque caractère dans les textes

logger = logging.getLogger(__name__)
logging.basicConfig(filename='cuinter.log', encoding='utf-8', level=logging.DEBUG)


class Label(NamedTuple):
    pid: int # Persistent identifier, ask Romain
    y: int
    x: int
    text: str = None
    
    @classmethod
    def new(cls, y: int, x: int, text: str = None, is_top_level: bool = True) -> "Label":
        pid = int(uuid.uuid4())
        label = cls(pid, y, x, text)
        
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
        )
        
        if is_top_level: set_element(self.pid, label)
        return label
    
    def delete(self) -> None:
        remove_element(self.pid)
    
    def draw(self) -> None:
        if self.text is None: return
        
        for i, char in enumerate(self.text):
            set_cell(self.y, self.x + i, char)


class Rectangle(NamedTuple):
    pid: int
    y: int
    x: int
    height: int
    width: int
    
    @classmethod
    def new(cls, y: int, x: int, height: int, width: int, is_top_level: bool = True) -> "Rectangle":
        pid = int(uuid.uuid4())
        rectangle = cls(pid, y, x, height, width)
        
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
        )
        
        if is_top_level: set_element(self.pid, rectangle)
        return rectangle
    
    def delete(self) -> None:
        remove_element(self.pid)
    
    def draw(self) -> None:
        if self.height <= 0 or self.width <= 0: return
        
        y1, y2 = self.y, self.y + self.height
        x1, x2 = self.x, self.x + self.width
        
        set_cell(y1, x1, "┌")
        set_cell(y1, x2, "┐")
        set_cell(y2, x1, "└")
        set_cell(y2, x2, "┘")
        
        for y in range(y1 + 1, y2):
            set_cell(y, x1, "│")
            set_cell(y, x2, "│")
            for x in range(x1 + 1, x2):
                set_cell(y, x, " ")
        
        for x in range(x1 + 1, x2):
            set_cell(y1, x, "─")
            set_cell(y2, x, "─")


class SpriteRenderer(NamedTuple):
    pid: int
    y: int
    x: int
    sprite: str = None
    
    @property
    def height(self) -> int:
        if self.sprite is None: return 0
        return len(self.sprite)
    
    @property
    def width(self) -> int:
        if self.sprite is None: return 0
        return max(len(row) for row in self.sprite)
    
    @classmethod
    def new(cls, y: int, x: int, sprite: tuple[str, ...] = None, is_top_level: bool = True) -> "SpriteRenderer":
        pid = int(uuid.uuid4())
        sprite_renderer = cls(pid, y, x, sprite)
        
        if is_top_level:
            set_element(pid, sprite_renderer)
            logger.debug("Created new SpriteRenderer")
        return sprite_renderer
    
    def config(self, is_top_level: bool = True, **kwargs) -> "SpriteRenderer":
        sprite_renderer = SpriteRenderer(
            self.pid,
            kwargs.get("y", self.y),
            kwargs.get("x", self.x),
            kwargs.get("sprite", self.sprite),
        )
        
        if is_top_level: set_element(self.pid, sprite_renderer)
        return sprite_renderer
    
    def delete(self) -> None:
        remove_element(self.pid)
    
    def draw(self) -> None:
        if self.sprite is None: return
        
        for y, row in enumerate(self.sprite.split("\n")):
            for x, char in enumerate(row):
                if char == " ": continue
                set_cell(self.y + y, self.x + x, char)


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
            Rectangle.new(y, x, height, width, False),
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
    
    def draw(self) -> None:
        self.rectangle.draw()
        
        if self.text is None: return
        
        text_y = self.y + 2
        text_x = self.x + 3
        wrap = self.width - 5
        
        for i, char in enumerate(self.text):
            set_cell(text_y + i // wrap, text_x + i % wrap, char)


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
    
    def key_input(self, key: int) -> None:
        if key in (ord(" "), ord("\n")):
            self.next()
    
    def next(self) -> None:
        if math.floor((time.time() - self.start_time) / CHARACTER_TIME) <= len(self.dialog_line.text):
            self.config(start_time=0)
        elif self.line_index + 1 < len(self.dialog):
            self.config(start_time=time.time(), line_index=self.line_index + 1)
        else:
            add_event(FINISHED_DIALOG, self)
            self.delete()
    
    def draw(self) -> None:
        length_to_draw = min(math.floor((time.time() - self.start_time) / CHARACTER_TIME), len(self.dialog_line.text))
        formatted_text = ((f"[{self.dialog_line.character.name}]: " if not self.dialog_line.character is None else "")
                          + self.dialog_line.text[:length_to_draw])
        
        self.config(text=formatted_text)
        get_elements()[self.pid].text_box.draw()


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
    
    def key_input(self, key: int) -> None:
        if key in (curses.KEY_UP, ord("w")):
            self.select_previous()
        
        elif key in (curses.KEY_DOWN, ord("s")):
            self.select_next()
        
        elif key in (ord(" "), ord("\n")):
            self.confirm()
    
    def select_previous(self) -> None:
        self.config(selected_index=move_toward(self.selected_index, 0))
    
    def select_next(self) -> None:
        self.config(selected_index=move_toward(self.selected_index, len(self.options) - 1))
    
    def confirm(self) -> None:
        add_event(CONFIRMED_CHOICE, self)
        self.delete()
    
    def draw(self) -> None:
        formatted_text = ""
        for i, option in enumerate(self.options):
            formatted_line = ("> " if i == self.selected_index else "  ") + option
            formatted_text += formatted_line.ljust((self.width - 5) * 2)
        
        self.config(text=formatted_text)
        get_elements()[self.pid].text_box.draw()


def _fullscreen() -> None:
    """Simulates the F11 key being pressed."""
    user32 = ctypes.windll.user32
    user32.keybd_event(0x7A, 0, 0, 0)
    user32.keybd_event(0x7A, 0, 0x0002, 0)


def _display_buffer(stdscr) -> None:
    """
    Displays the buffer in rows instead of individual characters to improve
    performance.
    """
    for y, row in enumerate(get_buffer()):
        row_str = ""
        prev_x = 0
        first_x = None

        for x, char in enumerate(row):
            if char == " ": continue
            
            if first_x is None:
                row_str += char
                first_x = x
            else:
                row_str += " " * (x - prev_x - 1) + char
            
            prev_x = x
        
        if first_x is None: continue
        if y == screen_height - 1 and first_x + len(row_str) == screen_width:
            row_str = row_str[:-1]
        
        stdscr.move(y, first_x)
        stdscr.addstr(row_str)


def _buffer_manager():
    buffer = copy.deepcopy(empty_buffer)
    
    def get_buffer() -> list[list[str]]:
        return buffer
    
    def set_cell(y: int, x: int, char: str = " ") -> None:
        nonlocal buffer
        if 0 <= y < screen_height and 0 <= x < screen_width:
            buffer[y][x] = char
    
    def clear_buffer() -> None:
        nonlocal buffer
        buffer = copy.deepcopy(empty_buffer)
    
    return get_buffer, set_cell, clear_buffer


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
    
    Doesn't behave like tkinter's mainloop, has to be called within a loop.
    """
    
    clear_events()
    
    # Input updating
    
    key = stdscr.getch()
    
    if not key is None:
        for element in reversed(get_elements().values()):
            try:
                element.key_input(key)
            except AttributeError:
                continue
            else:
                break
        else:
            add_event(PRESSED_KEY, key)
    
    # Display updating
    
    clear_buffer()
    stdscr.clear()

    for element in get_elements().values():
        element.draw()
    
    _display_buffer(stdscr)
    stdscr.refresh()
    
    return get_events()


time.sleep(0.5)
_fullscreen()
time.sleep(0.5)

stdscr = curses.initscr()

curses.curs_set(0) # Cache le curseur
stdscr.nodelay(1) # Pas de blocage d'entrées
stdscr.timeout(0) # Délai de vérification d'entrée

screen_height, screen_width = stdscr.getmaxyx()
empty_buffer = [[" " for _ in range(screen_width)] for _ in range(screen_height)]

get_buffer, set_cell, clear_buffer = _buffer_manager()
get_elements, set_element, remove_element = _element_manager()
get_events, add_event, clear_events = _event_manager()
