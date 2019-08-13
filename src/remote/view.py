import curses
from view import ViewClientMixin


class CursesView(ViewClientMixin):
    def __init__(self):
        self.stdscr = curses.initscr()

        curses.noecho()
        curses.cbreak()
        self.stdscr.keypad(True)

    def close(self):
        curses.nocbreak()
        self.stdscr.keypad(False)
        curses.echo()
        curses.endwin()

    def render(self):
        pass

