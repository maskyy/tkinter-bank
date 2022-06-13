import enum as _enum
import functools as _ft
import hashlib as _hash
import tkinter.messagebox as _msg
import tkinter.ttk as _ttk

import style
import util

__all__ = ["Login"]


def hash_pwd(s):
    return _hash.sha256(s.encode()).hexdigest()


class Login(_ttk.Frame):
    def check_credentials(db, login_entry, password_entry, handler):
        login, password = login_entry.get_strip(), password_entry.get_strip()
        if not login or not password:
            return util.show_error("Введите логин и пароль")

        user_data = db.get_user(login)
        if user_data is None:
            return util.show_error("Логин не существует")

        password2 = user_data[2]
        if hash_pwd(password) != password2:
            return util.show_error("Неверный пароль")

        handler(user_data)
        login_entry.delete(0, "end")
        password_entry.delete(0, "end")
        return True

    def __init__(self, master=None, actions=None, db=None):
        super().__init__(master)
        self.create_widgets(actions, db)

    def create_widgets(self, actions, db):
        _ttk.Label(self, text="Логин").pack()
        self.login = login = style.Entry(self)
        login.pack(pady=5)

        _ttk.Label(self, text="Пароль").pack()
        self.password = password = style.Entry(self, show="*")
        password.pack(pady=5)

        self.buttons = []
        for name, action in actions:
            if name == "Войти":
                func = _ft.partial(Login.check_credentials, db, login, password, action)
            else:
                func = _ft.partial(action)

            btn = style.Button(
                self,
                text=name,
                command=func,
                width=17,
            )
            btn.pack(pady=5)
            self.buttons.append(btn)
