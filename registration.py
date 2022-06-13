import tkinter as _tk
import tkinter.ttk as _ttk

import dates
import tableview
import window
from db_sqlite import Database


class Registration(window.Window):
    def __init__(self):
        super().__init__("Регистрация")
        self._create_widgets()

    def _create_widgets(self):
        pass
