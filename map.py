import curses

def main(stdscr):
    # Clear screen
    stdscr.clear()

    # Turn off cursor blinking
    curses.curs_set(0)

    # Initialize colors if supported
    if curses.has_colors():
        curses.start_color()
        curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)

    # Print some text
    stdscr.addstr(0, 0, "Hello, Curses!", curses.color_pair(1))

    # Refresh the screen to apply changes
    stdscr.refresh()

    # Wait for user input
    stdscr.getch()

# Wrap the main function to properly initialize and terminate curses
curses.wrapper(main)
