import tkinter as _tk
import tkinter.ttk as _ttk

import dates
import tableview
import window
from db_sqlite import Database


class User(window.Window):
    def __init__(self):
        super().__init__("Главная страница")
        self._create_widgets()

    def _create_widgets(self):
        pass
