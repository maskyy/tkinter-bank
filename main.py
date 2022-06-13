#!/usr/bin/env python3
import sys

import logo
import registration
import style
import user
import util
import window
from db_sqlite import Database
from login import Login


class MainWindow(window.RootWindow):
    def __init__(self):
        super().__init__("HSBC")
        logo.create_image()
        style.init_style()
        self._db = Database()

        self.create_widgets()

    def create_widgets(self):
        logo.get_label(self).pack()

        login_window = Login(
            self,
            [
                ("Войти", lambda data: user.User(self, self._db, data)),
                ("Регистрация", lambda: registration.Registration(db=self._db)),
                ("Выход", self.destroy),
            ],
            self._db,
        )

        login_window.pack(expand=True)
        login_window.login.focus()
        login_window.password.bind(
            "<Return>", lambda _: login_window.buttons[0].invoke()
        )

        if len(sys.argv) >= 3:
            login_window.login.insert(0, sys.argv[1])
            login_window.password.insert(0, sys.argv[2])
            login_window.buttons[0].invoke()


def run():
    root = MainWindow()
    root.mainloop()


if __name__ == "__main__":
    run()
