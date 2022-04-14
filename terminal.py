"""terminal.py

manage terminal session
"""

import curses

class terminal:
    def __init__(self):
        self.stdscr = None
        self.insert = False

    def __enter__(self):
        self.stdscr = curses.initscr()
        curses.cbreak()
        self.stdscr.keypad(True)
        curses.noecho()
        return self

    def __exit__(self, *args):
        curses.nocbreak()
        self.stdscr.keypad(False)
        curses.echo()
        curses.endwin()

    def pause(self):
        """Wait for input

        Parameters
        ----------
        None

        Returns
        -------
        None
        """
        self.stdscr.addstr("Press any key to continue . . . ")
        self.stdscr.refresh()
        self.stdscr.getkey()
        self.stdscr.addstr("\n")
        self.stdscr.refresh()

    def print(self, text):
        """Print input to terminal

        Parameters
        ----------
        text : str
            String to print on the terminal

        Returns
        -------
        None
        """
        self.stdscr.addstr(text)
        self.stdscr.refresh()

    def clear(self):
        """Clear termial

        Parameters
        ----------
        None

        Returns
        -------
        None
        """
        self.stdscr.clear()
        self.stdscr.refresh()

    def input(self, prompt, tabcomplete=None):
        """Get user input

        Parameters
        ----------
        prompt : sting
            The prompt to display
        tabcomplete : function(string)
            The callback for tab completion. If None, then tab is ignored.

        Returns
        -------
        string
            The user input string
        """
        # print prompt
        self.stdscr.addstr(prompt)
        self.stdscr.refresh()

        # get reply
        string = ""
        index = 0
        while True:
            key = self.stdscr.getkey()
            if not key.startswith("KEY_"): # if not special key
                if key not in ["\n", "\t"]: # if not tab or enter
                    # add or insert key to string
                    self.stdscr.addstr(key)
                    if index > len(string) - 1:
                        string = string + key
                    else:
                        if self.insert:
                            string = string[:index] + key + string[index:]
                            y, x = self.stdscr.getyx()
                            self.stdscr.addstr(y, x, string[index + 1:])
                            self.stdscr.move(y, x)
                        else:
                            string = string[:index] + key + string[index + 1:]
                    index += 1
                elif key == "\t": # auto complete
                    if tabcomplete is not None:
                        text, tips = tabcomplete(string)
                        y, x = self.stdscr.getyx()
                        self.stdscr.move(y + 1, 0)
                        self.stdscr.clrtobot()
                        self.stdscr.move(y, x)

                        if len(text) != 0:
                            string = string[:index] + text + string[index:]
                            y, x = self.stdscr.getyx()
                            self.stdscr.addstr(y, x, string[index:])
                            self.stdscr.move(y, x + len(text))
                            index = index + len(text)
                        else:
                            y, x = self.stdscr.getyx()
                            self.stdscr.addstr(y + 1, 0, tips)
                            self.stdscr.move(y, x)
                else: # save input and move to next line
                    y, x = self.stdscr.getyx()
                    self.stdscr.move(y + 1, 0)
                    break
            elif key == "KEY_BACKSPACE": # remove character before cursor
                if index > 0:
                    if index > len(string) - 1:
                        string = string[:-1]
                        index -= 1
                        y, x = self.stdscr.getyx()
                        self.stdscr.addstr(y, x - 1, " ")
                        self.stdscr.move(y, x - 1)
                    else:
                        string = string[:index - 1] + string[index:]
                        index -= 1
                        y, x = self.stdscr.getyx()
                        x -= 1
                        self.stdscr.addstr(y, x + (len(string) - index), " ")
                        self.stdscr.addstr(y, x, string[index:])
                        self.stdscr.move(y, x)
            elif key == "KEY_DC": # remove character under curser
                if index < len(string):
                    string = string[:index] + string[index + 1:]
                    y, x = self.stdscr.getyx()
                    self.stdscr.addstr(y, x + (len(string) - index), " ")
                    self.stdscr.addstr(y, x, string[index:])
                    self.stdscr.move(y, x)
            elif key == "KEY_IC": # change insert mode
                self.insert = not self.insert
            elif key == "KEY_LEFT": # move cursor
                if index > 0:
                    index -= 1
                    y, x = self.stdscr.getyx()
                    self.stdscr.move(y, x - 1)
            elif key == "KEY_RIGHT": # move cursor
                if index < len(string):
                    index += 1
                    y, x = self.stdscr.getyx()
                    self.stdscr.move(y, x + 1)
        return string
