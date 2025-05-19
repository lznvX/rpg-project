from bresenham import bresenham, bresenham_depth
import curses
import ctypes
import time
from typing import NamedTuple
from vectormath import Vector2, Vector3

ASPECT_RATIO = 16 / 9


class Player(NamedTuple):
    position: Vector2
    health: int
    
    def move(self, movement: Vector2) -> "Player":
        return Player(self.position + movement, self.health)


def fullscreen():
    """Simule la pression de la touche f11."""
    user32 = ctypes.windll.user32
    user32.keybd_event(0x7A, 0, 0, 0)
    user32.keybd_event(0x7A, 0, 0x0002, 0)


def main(stdscr):
    # Initialisation couleurs curses
    curses.start_color()
    curses.use_default_colors()
    for i in range(curses.COLOR_PAIRS - 1):
        curses.init_pair(i + 1, i, -1)
    
    curses.curs_set(0) # Cache le curseur
    stdscr.nodelay(1) # Pas de blocage d'entrées
    stdscr.timeout(16) # Délai d'affichage en ms
    
    screen_size = stdscr.getmaxyx()
    screen_size = Vector2(screen_size[1], screen_size[0])
    
    x_correction = ASPECT_RATIO / (screen_size.x / screen_size.y)
    
    player = Player(Vector2(0, 0), 3)
    
    while True:
        key = stdscr.getch()
        if key == ord("a"):
            player = player.move(Vector2(-1, 0))
        if key == ord("d"):
            player = player.move(Vector2(1, 0))
        elif key == ord("q"):
            break
        
        stdscr.clear()
        
        stdscr.addch(player.position.y, player.position.x, "P")
        
        stdscr.refresh()


time.sleep(0.5)
fullscreen()
time.sleep(0.5)
curses.wrapper(main)