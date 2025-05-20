"""Interface and display for curses.

Basically a tkinter clone at this point.

Docstrings partly written by GitHub Copilot (GPT-4.1),
verified and modified when needed by us.

Contributors:
    Romain
"""

from __future__ import annotations
from copy import deepcopy
import ctypes
import curses
import logging
import math
import time
from typing import Callable, NamedTuple
from uuid import uuid4
from common import EnumObject, move_toward
from enums import EVENT_TYPES, RECTANGLE_PRESETS, UI_ELEMENT_TYPES
from lang import DialogLine

logger = logging.getLogger(__name__)

X_CORRECTION = 2.6  # Hauteur / largeur d'un caractère
CHARACTER_TIME = 0.025  # Délai d'affichage de chaque caractère dans les textes
STDSCR_INIT_ERROR_MSG = "Stdscr not initialized"


class Label(NamedTuple):
    """Displays single line text in the curses UI.

    Attributes:
        pid (int): Persistent identifier.
        y (int): Y position.
        x (int): X position.
        text (str): Text to display.
    """
    pid: int
    y: int
    x: int
    text: str

    @classmethod
    def new(cls, y: int, x: int, text: str = None, is_top_level: bool = True) -> Label:
        """Create a new Label.

        Initialize its identifier and add it to cuinter's active UI elements
        if is_top_level, meaning if it is not the "child" of another element.
        """
        logger.debug("Creating new Label")

        pid = int(uuid4())
        label = cls(pid, y, x, text)

        if is_top_level:
            set_element(pid, label)

        return label

    def config(self, is_top_level: bool = True, **kwargs) -> Label:
        """Clone the Label with attributes in kwargs changed.

        Replace the old Label in cuinter's active UI elements if is_top_level,
        meaning if it is not the "child" of another element.
        """
        label = Label(
            self.pid,
            kwargs.get("y", self.y),
            kwargs.get("x", self.x),
            kwargs.get("text", self.text),
        )

        if is_top_level:
            set_element(self.pid, label)

        return label

    def delete(self) -> None:
        """Remove the Label from cuinter's active UI elements."""
        remove_element(self.pid)

    def draw(self) -> None:
        """Draw the Label in the display buffer."""
        if self.text is None:
            return

        for i, char in enumerate(self.text):
            set_cell(self.y, self.x + i, char)


class SpriteRenderer(NamedTuple):
    """Displays an ASCII sprite at a given position.

    Attributes:
        pid (int): Persistent identifier.
        y (int): Y position.
        x (int): X position.
        sprite (str): The ASCII sprite as a string.
    """
    pid: int
    y: int
    x: int
    sprite: str

    @property
    def height(self) -> int:
        """Return the height of the sprite."""
        if self.sprite is None:
            return 0
        return len(self.sprite)

    @property
    def width(self) -> int:
        """Return the width of the sprite."""
        if self.sprite is None:
            return 0
        return max(len(row) for row in self.sprite)

    @classmethod
    def new(cls, y: int, x: int, sprite: str = None, is_top_level: bool = True) -> SpriteRenderer:
        """Create a new SpriteRenderer and optionally register it as a top-level UI element."""
        logger.debug("Creating new SpriteRenderer")

        pid = int(uuid4())
        sprite_renderer = cls(pid, y, x, sprite)

        if is_top_level:
            set_element(pid, sprite_renderer)

        return sprite_renderer

    def config(self, is_top_level: bool = True, **kwargs) -> SpriteRenderer:
        """Clone the SpriteRenderer with updated attributes and optionally update in UI elements."""
        sprite_renderer = SpriteRenderer(
            self.pid,
            kwargs.get("y", self.y),
            kwargs.get("x", self.x),
            kwargs.get("sprite", self.sprite),
        )

        if is_top_level:
            set_element(self.pid, sprite_renderer)

        return sprite_renderer

    def delete(self) -> None:
        """Remove the SpriteRenderer from cuinter's active UI elements."""
        remove_element(self.pid)

    def draw(self) -> None:
        """Draw the sprite in the display buffer."""
        if self.sprite is None:
            return

        for y, row in enumerate(self.sprite.split("\n")):
            for x, char in enumerate(row):
                if char == " ":
                    continue
                set_cell(self.y + y, self.x + x, char)


class Rectangle(NamedTuple):
    """Draws a rectangle (box) on the UI."""

    pid: int
    y: int
    x: int
    height: int
    width: int

    @staticmethod
    def get_preset(preset: int = 0):
        """Return a Rectangle with dimensions set from a preset."""
        screen_height = get_screen_height()
        screen_width = get_screen_width()
        match preset:
            case RECTANGLE_PRESETS.DIALOG:
                return Rectangle(
                    pid=None,
                    y=screen_height - 12,
                    x=round(screen_width / 4),
                    height=10,
                    width=round(screen_width / 2),
                )
            case RECTANGLE_PRESETS.MENU:
                return Rectangle(
                    pid=None,
                    y=round(screen_height / 4),
                    x=round(screen_width / 4),
                    height=round(screen_height / 2),
                    width=round(screen_width / 2),
                )
            case _:
                logger.error("Rectangle preset enum not found: {preset}")
                return Rectangle(
                    pid=None,
                    y=screen_height - 12,
                    x=round(screen_width / 4),
                    height=10,
                    width=round(screen_width / 2),
                )

    @classmethod
    def new(cls, y: int = None, x: int = None, height: int = None,
            width: int = None, rectangle_preset: int = 0,
            is_top_level: bool = True) -> Rectangle:
        """Create a new Rectangle and optionally register as a top-level UI element."""
        logger.debug("Creating new Rectangle")

        preset = Rectangle.get_preset(rectangle_preset)
        pid = int(uuid4())
        rectangle = cls(
            pid,
            preset.y if y is None else y,
            preset.x if x is None else x,
            preset.height if height is None else height,
            preset.width if width is None else width,
        )

        if is_top_level:
            set_element(pid, rectangle)

        return rectangle

    def config(self, is_top_level: bool = True, **kwargs) -> Rectangle:
        """Clone the Rectangle with updated attributes and optionally update in UI elements."""
        rectangle = Rectangle(
            self.pid,
            kwargs.get("y", self.y),
            kwargs.get("x", self.x),
            kwargs.get("height", self.height),
            kwargs.get("width", self.width),
        )

        if is_top_level:
            set_element(self.pid, rectangle)

        return rectangle

    def delete(self) -> None:
        """Remove the Rectangle from cuinter's active UI elements."""
        remove_element(self.pid)

    def draw(self) -> None:
        """Draw the Rectangle in the display buffer."""
        if self.height <= 0 or self.width <= 0:
            return

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
    """Displays a rectangle with wrapped text inside."""

    pid: int
    rectangle: Rectangle
    text: str

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
        """Create a new TextBox and optionally register as a top-level UI element."""
        logger.debug("Creating new TextBox")

        pid = int(uuid4())
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

        return text_box

    def config(self, is_top_level: bool = True, **kwargs) -> TextBox:
        """Clone the TextBox with updated attributes and optionally update in UI elements."""
        text_box = TextBox(
            self.pid,
            self.rectangle.config(False, **kwargs),
            kwargs.get("text", self.text),
        )

        if is_top_level:
            set_element(self.pid, text_box)

        return text_box

    def delete(self) -> None:
        """Remove the TextBox from cuinter's active UI elements."""
        remove_element(self.pid)

    def draw(self) -> None:
        """Draw the TextBox with wrapped text."""
        self.rectangle.draw()

        if self.text is None:
            return

        text_y = self.y + 2
        text_x = self.x + 3
        wrap = self.width - 5
        current_y = text_y

        for line in self.text.split("\n"):
            for i, char in enumerate(line):
                row = current_y + i // wrap
                col = text_x + i % wrap
                set_cell(row, col, char)
            current_y += (len(line) + wrap - 1) // wrap or 1


class DialogBox(NamedTuple):
    """Displays a dialog box with animated lines of text."""

    pid: int
    text_box: TextBox
    dialog: tuple[DialogLine | EnumObject, ...]
    start_time: float
    line_index: int

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
        """Return the current line in dialog."""
        return self.dialog[self.line_index]

    @property
    def current_text(self) -> str:
        """Return the text of the current line."""
        return self.current_line.text

    @property
    def length_to_draw(self) -> int:
        """Return the number of characters to display for animation."""
        uncapped = math.floor((time.time() - self.start_time) / CHARACTER_TIME)
        return min(uncapped, len(self.current_text))

    @classmethod
    def new(cls, y: int = None, x: int = None, height: int = None,
            width: int = None,
            dialog: tuple[DialogLine | EnumObject, ...] = None,
            rectangle_preset: int = 0, is_top_level: bool = True) -> DialogBox:
        """Create a new DialogBox and optionally register as a top-level UI element."""
        logger.debug("Creating new DialogBox")

        pid = int(uuid4())
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

        if isinstance(dialog_box.current_line, EnumObject):
            add_event(dialog_box.current_line)
            dialog_box.next()

        return dialog_box

    def config(self, is_top_level: bool = True, **kwargs) -> DialogBox:
        """Clone the DialogBox with updated attributes and optionally update in UI elements."""
        dialog_box = DialogBox(
            self.pid,
            self.text_box.config(False, **kwargs),
            kwargs.get("dialog", self.dialog),
            kwargs.get("start_time", self.start_time),
            kwargs.get("line_index", self.line_index),
        )

        if is_top_level:
            set_element(self.pid, dialog_box)

        return dialog_box

    def delete(self) -> None:
        """Remove the DialogBox from cuinter's active UI elements."""
        remove_element(self.pid)

    def key_input(self, key: int) -> None:
        """Handle key input for dialog advancement."""
        if key in (ord(" "), ord("\n")):
            self.next()

    def next(self) -> None:
        """Advance to the next line or close the DialogBox."""
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
        """Draw the dialog box with the current line animated."""
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
    """Displays a selectable list of options in a box."""

    pid: int
    text_box: TextBox
    options: tuple[str, ...]
    on_confirm_events: dict[int, EnumObject]
    selected_index: int

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
        """Return the currently selected option."""
        return self.options[self.selected_index]

    @classmethod
    def new(cls, y: int = None, x: int = None, height: int = None,
            width: int = None, options: tuple[str, ...] = None,
            on_confirm_events: dict[int, EnumObject] = {},
            selected_index: int = 0, rectangle_preset: int = 0,
            is_top_level: bool = True) -> 'ChoiceBox':
        """Create a new ChoiceBox and optionally register as a top-level UI element."""
        logger.debug("Creating new ChoiceBox")

        pid = int(uuid4())
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

        return choice_box

    def config(self, is_top_level: bool = True, **kwargs) -> ChoiceBox:
        """Clone the ChoiceBox with updated attributes and optionally update in UI elements."""
        choice_box = ChoiceBox(
            self.pid,
            self.text_box.config(False, **kwargs),
            kwargs.get("options", self.options),
            kwargs.get("on_confirm_events", self.on_confirm_events),
            kwargs.get("selected_index", self.selected_index),
        )

        if is_top_level:
            set_element(self.pid, choice_box)

        return choice_box

    def delete(self) -> None:
        """Remove the ChoiceBox from cuinter's active UI elements."""
        remove_element(self.pid)

    def key_input(self, key: int) -> None:
        """Handle key input for navigating/selecting options."""
        if key == ord("w"):
            self.select_previous()

        elif key == ord("s"):
            self.select_next()

        elif key in (ord(" "), ord("\n")):
            self.confirm()

    def select_previous(self) -> None:
        """Move selection to the previous option."""
        self.config(selected_index=move_toward(self.selected_index, 0))

    def select_next(self) -> None:
        """Move selection to the next option."""
        self.config(selected_index=move_toward(self.selected_index, len(self.options) - 1))

    def confirm(self) -> None:
        """Confirm the selected option and execute its event."""
        if (self.on_confirm_events is not None
        and self.selected_index in self.on_confirm_events
        and self.on_confirm_events[self.selected_index] is not None):
            add_event(self.on_confirm_events[self.selected_index])
        self.delete()

    def draw(self) -> None:
        """Draw the ChoiceBox with the current selection highlighted."""
        formatted_text = ""
        for i, option in enumerate(self.options):
            formatted_line = ("> " if i == self.selected_index else "  ") + option
            formatted_text += formatted_line.ljust((self.width - 5) * 2)

        self.config(text=formatted_text)
        get_elements()[self.pid].text_box.draw()


def _make_stdscr_manager() -> tuple[Callable, ...]:
    """Creates getter/setter functions for the curses stdscr object and its properties."""
    cache = None

    def get_cache() -> object:
        if cache is None:
            logger.error(STDSCR_INIT_ERROR_MSG)
        return cache

    def set_cache(stdscr: object) -> None:
        nonlocal cache
        cache = stdscr

    def get_cache_height() -> int:
        if cache is None:
            logger.error(STDSCR_INIT_ERROR_MSG)
            return 0
        return cache.getmaxyx()[0]

    def get_cache_width() -> int:
        if cache is None:
            logger.error(STDSCR_INIT_ERROR_MSG)
            return 0
        return cache.getmaxyx()[1]

    def get_cache_empty_buffer() -> list[list[str]]:
        return [[" " for _ in range(get_cache_width())] for _ in range(get_cache_height())]

    return get_cache, set_cache, get_cache_height, get_cache_width, get_cache_empty_buffer


def _make_buffer_manager() -> tuple[Callable, ...]:
    """Creates functions to manage the display buffer."""
    cache = deepcopy(get_empty_buffer())

    def get_cache() -> list[list[str]]:
        return cache

    def set_item(y: int, x: int, char: str = " ") -> None:
        nonlocal cache
        if 0 <= y < get_screen_height() and 0 <= x < get_screen_width():
            cache[y][x] = char

    def clear_cache() -> None:
        nonlocal cache
        cache = deepcopy(get_empty_buffer())

    return get_cache, set_item, clear_cache


def _make_element_manager() -> tuple[Callable, ...]:
    """Creates functions to manage active UI elements."""
    cache = {}

    def get_cache() -> dict[int, object]:
        return cache

    def set_item(pid: int, element: object) -> None:
        nonlocal cache
        cache[pid] = element

    def remove_item(pid: int) -> None:
        nonlocal cache
        del cache[pid]

    return get_cache, set_item, remove_item


def _make_event_manager() -> tuple[Callable, ...]:
    """Creates functions to manage UI events."""
    cache = []

    def get_cache() -> list[EnumObject]:
        return cache

    def add_item(event: EnumObject) -> None:
        nonlocal cache
        cache.append(event)

    def clear_cache() -> None:
        nonlocal cache
        cache.clear()

    return get_cache, add_item, clear_cache


def _draw() -> None:
    """Display the buffer in rows instead of individual characters to improve performance."""
    stdscr = get_stdscr()
    if stdscr is None:
        return

    clear_buffer()
    stdscr.clear()

    for element in get_elements().values():
        element.draw()

    for y, row in enumerate(get_buffer()):
        row_str = ""
        prev_x = 0
        first_x = None

        for x, char in enumerate(row):
            if char == " ":
                continue

            if first_x is None:
                row_str += char
                first_x = x
            else:
                row_str += " " * (x - prev_x - 1) + char

            prev_x = x

        if first_x is None:
            continue

        if (
            y == stdscr.getmaxyx()[0] - 1
            and first_x + len(row_str) == stdscr.getmaxyx()[1]
        ):
            row_str = row_str[:-1]

        stdscr.move(y, first_x)
        stdscr.addstr(row_str)

    stdscr.refresh()


def fullscreen() -> None:
    """Simulate the F11 key being pressed to toggle fullscreen mode."""
    logger.debug("Toggling fullscreen")

    user32 = ctypes.windll.user32
    user32.keybd_event(0x7A, 0, 0, 0)
    user32.keybd_event(0x7A, 0, 0x0002, 0)


def setup() -> None:
    """Initialize the curses window and configure the UI."""
    time.sleep(0.5)
    fullscreen()
    time.sleep(0.5)

    stdscr = curses.initscr()

    curses.curs_set(0)  # Hide cursor
    stdscr.nodelay(1)   # No input blocking
    stdscr.timeout(0)   # No input timeout

    set_stdscr(stdscr)


def update() -> list[EnumObject]:
    """Process inputs and draw active UI elements.

    Returns a dictionary of events for main.py to handle.
    Doesn't behave like tkinter's mainloop, has to be called within a loop.
    """
    stdscr = get_stdscr()
    if stdscr is None:
        return []

    clear_events()
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

    _draw()

    return get_events()


UI_ELEMENT_CLASSES = {
    UI_ELEMENT_TYPES.LABEL: Label,
    UI_ELEMENT_TYPES.SPRITE_RENDERER: SpriteRenderer,
    UI_ELEMENT_TYPES.RECTANGLE: Rectangle,
    UI_ELEMENT_TYPES.TEXT_BOX: TextBox,
    UI_ELEMENT_TYPES.DIALOG_BOX: DialogBox,
    UI_ELEMENT_TYPES.CHOICE_BOX: ChoiceBox,
}

(
    get_stdscr,
    set_stdscr,
    get_screen_height,
    get_screen_width,
    get_empty_buffer,
) = _make_stdscr_manager()
(
    get_buffer,
    set_cell,
    clear_buffer,
) = _make_buffer_manager()
(
    get_elements,
    set_element,
    remove_element,
) = _make_element_manager()
(
    get_events,
    add_event,
    clear_events
) = _make_event_manager()
