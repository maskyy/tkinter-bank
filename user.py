import tkinter as _tk
import tkinter.ttk as _ttk

import dates
import logo
import style
import tableview
import window
from db_sqlite import Database


class User(window.Window2):
    def __init__(self, master=None, db=None, user_data=None):
        super().__init__(master, "Главная страница")
        self._db = db

        self._id = user_data[0]
        self._name = user_data[3]
        self._blocked = user_data[-1]
        if self._name != "admin":
            self._create_widgets()
        else:
            self._create_admin()

    def _create_admin(self):
        columns = ["ID", "ID владельца", "Название", "Баланс", "Валюта"]
        self._accounts = tableview.TableView(self, self._db, "accounts", columns)
        self._accounts.config(displaycolumns=["Название", "Баланс", "Валюта"])
        self._accounts.pack(fill="x")
        self._accounts.update_data()

        _ttk.Label(self, text="Источник").pack()
        self._source = style.Entry(self)
        self._source.pack()

        _ttk.Label(self, text="Цель").pack()
        self._target = style.Entry(self)
        self._target.pack()

        _ttk.Label(self, text="Сумма").pack()
        self._amount = style.Entry(self)
        self._amount.pack()

        style.Button(self, text="Добавить", command=self._add_transaction).pack()

    def _add_transaction(self):
        pass

    def _create_widgets(self):
        _ttk.Label(self, text=self._name).pack(pady=25)

        self._accounts = _ttk.Frame(self)
        self._accounts.pack()
        self._update_accounts(self._accounts)

        style.Button(self, text="Новый счёт/карта", command=self._new_account).pack(pady=25)

    def _update_accounts(self, master):
        for widget in list(master.children.values()):
            widget.destroy()

        data = self._db.get_accounts(self._id)
        if len(data) == 0:
            _ttk.Label(master, text="Счетов пока нет").pack()
            return

        for account in data:
            return

    def _new_account(self):
        self._window = win = window.Window2(self, "Новый счёт/карта")

        self._account_btn = style.Button(win, text="Счёт", command=lambda: self._toggle_type(self._account_btn, self._card_btn, False))
        self._account_btn.pack(pady=5)
        self._card_btn = style.Button(win, text="Карта", command=lambda: self._toggle_type(self._card_btn, self._account_btn, True))
        self._card_btn.pack(pady=5)
        self._is_card = None

    def _toggle_type(self, disable, enable, state):
        disable.config(state="disabled")
        enable.config(state="enabled")
        self._is_card = state

    def _filter_accounts(self, row):
        if row[1] == self._id:
            return row
        return None