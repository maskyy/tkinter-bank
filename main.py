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
        logo.get_label(self).pack(pady=10)

        check_credentials = lambda d, l, p: Login.check_credentials(
            d, l, p, self.open_window
        )

        login_window = Login(
            self,
            [
                # ("Зарегистрироваться", Login.register),
                ("Войти", lambda: self._create_window(user.User)),
                ("Регистрация", lambda: self._create_window(registration.Registration)),
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

    def _create_window(self, func):
        win = func()
        util.set_close_handler(win, lambda: self._close_handler(win))
        self.withdraw()

    def _close_handler(self, win):
        win.destroy()
        self.deiconify()


def run():
    root = MainWindow()
    root.mainloop()


if __name__ == "__main__":
    run()
