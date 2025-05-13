"""Interface and display for curses

Basically a tkinter clone at this point.

Contributors:
    Romain
"""

from __future__ import annotations
import copy
import ctypes
import curses
import logging
import math
import time
from typing import NamedTuple
import uuid
from common import *

X_CORRECTION = 2.6 # Hauteur / largeur d'un caractère
CHARACTER_TIME = 0.025 # Délai d'affichage de chaque caractère dans les textes


class _UIElementTypes(NamedTuple):
    LABEL: int
    SPRITE_RENDERER: int
    RECTANGLE: int
    TEXT_BOX: int
    DIALOG_BOX: int
    CHOICE_BOX: int

    @classmethod
    def new(cls) -> _UIElementTypes:
        return cls(*range(len(cls.__annotations__)))


class _RectanglePresets(NamedTuple):
    DIALOG: int
    MENU: int

    @classmethod
    def new(cls) -> _UIElementTypes:
        return cls(*range(len(cls.__annotations__)))


class Label(NamedTuple):
    pid: int # Persistent identifier
    y: int
    x: int
    text: str = None
    
    @classmethod
    def new(cls, y: int, x: int, text: str = None, is_top_level: bool = True) -> Label:
        pid = int(uuid.uuid4())
        label = cls(pid, y, x, text)
        
        if is_top_level:
            set_element(pid, label)
            logger.debug("Created new Label")
        return label
    
    def config(self, is_top_level: bool = True, **kwargs) -> Label:
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
    def new(cls, y: int, x: int, sprite: str = None, is_top_level: bool = True) -> SpriteRenderer:
        pid = int(uuid.uuid4())
        sprite_renderer = cls(pid, y, x, sprite)
        
        if is_top_level:
            set_element(pid, sprite_renderer)
            logger.debug("Created new SpriteRenderer")
        return sprite_renderer
    
    def config(self, is_top_level: bool = True, **kwargs) -> SpriteRenderer:
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


class Rectangle(NamedTuple):
    pid: int = None
    y: int = None
    x: int = None
    height: int = None
    width: int = None
    
    @staticmethod
    def get_preset(preset: int = 0):
        
        try:
            screen_height
            screen_width
        except NameError:
            logger.error("Rectangle couldn't access screen dimensions")
            return Rectangle(
                y=0,
                x=0,
                height=20,
                width=20,
            )
        
        match preset:
            case RECTANGLE_PRESETS.DIALOG:
                return Rectangle(
                    y=screen_height - 12,
                    x=round(screen_width / 4),
                    height=10,
                    width=round(screen_width / 2),
                )
            case RECTANGLE_PRESETS.MENU:
                return Rectangle(
                    y=round(screen_height / 4),
                    x=round(screen_width / 4),
                    height=round(screen_height / 2),
                    width=round(screen_width / 2),
                )
            case _:
                logger.error("Rectangle preset enum not found: {preset}")
                return Rectangle(
                    y=screen_height - 12,
                    x=round(screen_width / 4),
                    height=10,
                    width=round(screen_width / 2),
                )
    
    @classmethod
    def new(cls, y: int = None, x: int = None, height: int = None,
            width: int = None, rectangle_preset: int = 0,
            is_top_level: bool = True) -> Rectangle:
        preset = Rectangle.get_preset(rectangle_preset)
        pid = int(uuid.uuid4())
        rectangle = cls(
            pid,
            preset.y if y is None else y,
            preset.x if x is None else x,
            preset.height if height is None else height,
            preset.width if width is None else width,
        )
        
        if is_top_level:
            set_element(pid, rectangle)
            logger.debug("Created new Rectangle")
        return rectangle
    
    def config(self, is_top_level: bool = True, **kwargs) -> Rectangle:
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
    def new(cls, y: int = None, x: int = None, height: int = None,
            width: int = None, text: str = None, rectangle_preset: int = 0,
            is_top_level: bool = True) -> TextBox:
        pid = int(uuid.uuid4())
        text_box = cls(
            pid,
            Rectangle.new(
                y,
                x,
                height,
                width,
                rectangle_preset,
                False,
            ),
            text,
        )
        
        if is_top_level:
            set_element(pid, text_box)
            logger.debug("Created new TextBox")
        return text_box
    
    def config(self, is_top_level: bool = True, **kwargs) -> TextBox:
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
    dialog: tuple[DialogLine | EnumObject, ...]
    start_time: float = 0
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
    def current_line(self) -> DialogLine:
        return self.dialog[self.line_index]
    
    @property
    def current_text(self) -> DialogLine:
        return self.current_line.text
    
    @property
    def length_to_draw(self) -> int:
        uncapped = math.floor((time.time() - self.start_time) / CHARACTER_TIME)
        return min(uncapped, len(self.current_text))
    
    @classmethod
    def new(cls, y: int = None, x: int = None, height: int = None,
            width: int = None,
            dialog: tuple[DialogLine | EnumObject, ...] = None,
            rectangle_preset: int = 0, is_top_level: bool = True) -> DialogBox:
        pid = int(uuid.uuid4())
        dialog_box = cls(
            pid,
            TextBox.new(
                y,
                x,
                height,
                width,
                None,
                rectangle_preset,
                False,
            ),
            dialog,
            time.time(),
            0,
        )
        
        if is_top_level:
            set_element(pid, dialog_box)
            logger.debug("Created new DialogBox")
        return dialog_box
    
    def config(self, is_top_level: bool = True, **kwargs) -> DialogBox:
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
        if self.dialog is None:
            return
        
        if (isinstance(self.current_line, DialogLine)
        and self.length_to_draw < len(self.current_text)):
            self.config(start_time=0)
        
        elif self.line_index + 1 < len(self.dialog):
            new_dialog_box = self.config(
                start_time=time.time(),
                line_index=self.line_index + 1,
            )
            
            if isinstance(new_dialog_box.current_line, EnumObject):
                add_event(new_dialog_box.current_line)
                new_dialog_box.next()
        
        else:
            self.delete()
    
    def draw(self) -> None:
        if self.dialog is None:
            self.text_box.draw()
            return
        
        formatted_name = ""
        if self.current_line.character_name is not None:
            formatted_name = f"[{self.current_line.character_name}]: " 
        formatted_text = formatted_name + self.current_text[:self.length_to_draw]
        
        self.config(text=formatted_text)
        get_elements()[self.pid].text_box.draw()


class ChoiceBox(NamedTuple):
    pid: int
    text_box: TextBox
    options: tuple[str, ...]
    on_confirm_events: dict[int, EnumObject] = {}
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
    def new(cls, y: int = None, x: int = None, height: int = None,
            width: int = None, options: tuple[str, ...] = None,
            on_confirm_events: dict[int, EnumObject] = {},
            selected_index: int = 0, rectangle_preset: int = 0,
            is_top_level: bool = True) -> ChoiceBox:
        pid = int(uuid.uuid4())
        choice_box = cls(
            pid,
            TextBox.new(
                y,
                x,
                height,
                width,
                None,
                rectangle_preset,
                False,
            ),
            options,
            on_confirm_events,
            selected_index,
        )
        
        if is_top_level:
            set_element(pid, choice_box)
            logger.debug("Created new ChoiceBox")
        return choice_box
    
    def config(self, is_top_level: bool = True, **kwargs) -> ChoiceBox:
        choice_box = ChoiceBox(
            self.pid,
            self.text_box.config(False, **kwargs),
            kwargs.get("options", self.options),
            kwargs.get("on_confirm_events", self.on_confirm_events),
            kwargs.get("selected_index", self.selected_index),
        )
        
        if is_top_level: set_element(self.pid, choice_box)
        return choice_box
    
    def delete(self) -> None:
        remove_element(self.pid)
    
    def key_input(self, key: int) -> None:
        if key == ord("w"):
            self.select_previous()
        
        elif key == ord("s"):
            self.select_next()
        
        elif key in (ord(" "), ord("\n")):
            self.confirm()
    
    def select_previous(self) -> None:
        self.config(selected_index=move_toward(self.selected_index, 0))
    
    def select_next(self) -> None:
        self.config(selected_index=move_toward(self.selected_index, len(self.options) - 1))
    
    def confirm(self) -> None:
        if (self.on_confirm_events is not None
        and self.selected_index in self.on_confirm_events
        and self.on_confirm_events[self.selected_index] is not None):
            add_event(self.on_confirm_events[self.selected_index])
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


def _make_buffer_manager():
    cache = copy.deepcopy(empty_buffer)
    
    def get_buffer() -> list[list[str]]:
        return cache
    
    def set_cell(y: int, x: int, char: str = " ") -> None:
        nonlocal cache
        if 0 <= y < screen_height and 0 <= x < screen_width:
            cache[y][x] = char
    
    def clear_buffer() -> None:
        nonlocal cache
        cache = copy.deepcopy(empty_buffer)
    
    return get_buffer, set_cell, clear_buffer


def _make_element_manager():
    cache = {}
    
    def get_elements() -> dict[int, object]:
        return cache
    
    def set_element(pid: int, element: object) -> None:
        nonlocal cache
        cache[pid] = element
    
    def remove_element(pid: int) -> None:
        nonlocal cache
        del cache[pid]
    
    return get_elements, set_element, remove_element


def _make_event_manager():
    cache = []
    
    def get_events() -> list[EnumObject]:
        return cache
    
    def add_event(event: Event) -> None:
        nonlocal cache
        cache.append(event)
    
    def clear_events() -> None:
        nonlocal cache
        cache.clear()
    
    return get_events, add_event, clear_events


def update() -> list[EnumObject]:
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
            add_event(EnumObject(EVENT_TYPES.PRESS_KEY, key))
    
    # Display updating
    
    clear_buffer()
    stdscr.clear()

    for element in get_elements().values():
        element.draw()
    
    _display_buffer(stdscr)
    stdscr.refresh()
    
    return get_events()


logger = logging.getLogger(__name__)

UI_ELEMENT_TYPES = _UIElementTypes.new()
UI_ELEMENT_CLASSES = {
    UI_ELEMENT_TYPES.LABEL: Label,
    UI_ELEMENT_TYPES.SPRITE_RENDERER: SpriteRenderer,
    UI_ELEMENT_TYPES.RECTANGLE: Rectangle,
    UI_ELEMENT_TYPES.TEXT_BOX: TextBox,
    UI_ELEMENT_TYPES.DIALOG_BOX: DialogBox,
    UI_ELEMENT_TYPES.CHOICE_BOX: ChoiceBox,
}
RECTANGLE_PRESETS = _RectanglePresets.new()

time.sleep(0.5)
_fullscreen()
time.sleep(0.5)

stdscr = curses.initscr()

curses.curs_set(0) # Cache le curseur
stdscr.nodelay(1) # Pas de blocage d'entrées
stdscr.timeout(0) # Délai de vérification d'entrée

screen_height, screen_width = stdscr.getmaxyx()
empty_buffer = [[" " for _ in range(screen_width)] for _ in range(screen_height)]

get_buffer, set_cell, clear_buffer = _make_buffer_manager()
get_elements, set_element, remove_element = _make_element_manager()
get_events, add_event, clear_events = _make_event_manager()
