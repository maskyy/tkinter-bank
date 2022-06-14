import tkinter as _tk

import logo as _logo
import util as _util

__all__ = ["RootWindow", "Window", "Window2"]


def _init_window(win, title):
    win.title(title)
    win.resizable(0, 0)
    win.geometry("360x800")


class RootWindow(_tk.Tk):
    def __init__(self, title=None):
        super().__init__()
        _init_window(self, title)
        self.option_add("*TCombobox*Listbox*Font", "Roboto 16")


class Window(_tk.Toplevel):
    def __init__(self, title=None):
        super().__init__()
        _init_window(self, title)


class Window2(_tk.Toplevel):
    def __init__(self, master, title=None):
        super().__init__(master)
        self.master.withdraw()
        _logo.get_label(self).pack()
        _util.set_close_handler(self, self.close)
        _init_window(self, title)

    def close(self):
        self.master.deiconify()
        self.destroy()
