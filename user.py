import tkinter as _tk
import tkinter.ttk as _ttk

import dates
import style
import tableview
import window
from db_sqlite import Database


class User(window.Window2):
    def __init__(self, master=None, db=None, user_data=None):
        super().__init__(master, "Главная страница")
        print(user_data)
        self._create_widgets()

    def _create_widgets(self):
        pass
