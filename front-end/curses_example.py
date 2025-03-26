import curses
import math

def draw_circle(win, cy, cx, r, char="O"):
    """Draws a circle using ASCII characters on the screen."""
    for angle in range(0, 360, 10):  # Increase step size for performance
        rad = math.radians(angle)
        y = int(cy + r * math.sin(rad))
        x = int(cx + r * math.cos(rad))
        if 0 <= y < curses.LINES and 0 <= x < curses.COLS:
            win.addch(y, x, char)

def main(stdscr):
    curses.curs_set(0)  # Hide cursor
    stdscr.nodelay(1)   # Non-blocking input
    stdscr.timeout(100) # Refresh rate

    h, w = stdscr.getmaxyx()
    cx, cy = w // 2, h // 2  # Start position in center
    r = 5  # Circle radius

    while True:
        stdscr.clear()  # Clear screen before drawing
        draw_circle(stdscr, cy, cx, r)

        stdscr.refresh()

        key = stdscr.getch()
        if key == ord('q'):  # Quit when 'q' is pressed
            break
        elif key == curses.KEY_UP and cy > r:
            cy -= 1
        elif key == curses.KEY_DOWN and cy < h - r:
            cy += 1
        elif key == curses.KEY_LEFT and cx > r:
            cx -= 1
        elif key == curses.KEY_RIGHT and cx < w - r:
            cx += 1

curses.wrapper(main)
