import functools as _ft
import tkinter as _tk
import tkinter.ttk as _ttk

import dates
import logo
import style
import tableview
import util
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

        style.Button(self, text="Новый счёт/карта", command=self._new_account).pack(
            pady=25
        )

    def _update_accounts(self, master):
        for widget in list(master.children.values()):
            widget.destroy()

        data = self._db.get_accounts(self._id)
        if len(data) == 0:
            _ttk.Label(master, text="Счетов пока нет").pack()
            return

        for account in data:
            name, balance, currency = account[2:5]
            currency = self._db.get_currency_symbol(currency)
            text = "%.2f %s\n%s" % (balance, currency, name)
            cmd = _ft.partial(self._view_account, account)
            style.Button(master, text=text, command=cmd, width=20).pack(pady=5)

    def _new_account(self):
        self._window = win = window.Window2(self, "Новый счёт/карта")

        self._account_btn = style.Button(
            win,
            text="Счёт",
            command=lambda: self._toggle_type(self._account_btn, self._card_btn, False),
        )
        self._account_btn.pack(pady=5)
        self._card_btn = style.Button(
            win,
            text="Карта",
            command=lambda: self._toggle_type(self._card_btn, self._account_btn, True),
        )
        self._card_btn.pack(pady=5)
        self._is_card = None

        _ttk.Label(win, text="Название").pack(pady=5)
        self._name = style.Entry(win)
        self._name.pack(pady=5)

        _ttk.Label(win, text="Валюта").pack(pady=5)
        self._currency = _ttk.Combobox(
            win, state="readonly", values=self._get_currencies(), font="Roboto 16"
        )
        self._currency.pack(pady=5)

        bottom = _ttk.Frame(win)
        bottom.pack(side="bottom")

        style.Button(bottom, text="Открыть", command=self._add_account).pack(pady=5)
        style.Button(bottom, text="Назад", command=win.close).pack(pady=5)

    def _toggle_type(self, disable, enable, state):
        disable.config(state="disabled")
        enable.config(state="enabled")
        self._is_card = state

    def _get_currencies(self):
        data = self._db.get_table("currencies")
        result = []
        for row in data:
            s = "%s (%s)" % (row[0], row[1])
            result.append(s)
        return result

    def _add_account(self):
        if self._is_card is None:
            return util.show_error("Выберите тип продукта")
        name = self._name.get_strip()
        if not name:
            return util.show_error("Выберите название счёта/карты")
        currency = self._currency.get()
        if not currency:
            return util.show_error("Выберите валюту")

        currency = currency[:3]
        if self._is_card:
            self._db.add_card(self._id, name, currency)
            util.show_info("Карта добавлена")
        else:
            self._db.add_account(self._id, name, currency)
            util.show_info("Счёт добавлен")

        self._window.close()
        self._update_accounts(self._accounts)

    def _view_account(self, account_data):
        self._account_id = account_data[0]
        self._window = win = window.Window2(self, "Счёт")

        name, balance, currency = account_data[2:5]
        currency = self._db.get_currency_symbol(currency)
        text = "%.2f %s\n%s" % (balance, currency, name)
        style.Button(win, text=text, state="disabled", width=20).pack(pady=25)
        sum_ = self._db.sum_transactions(self._account_id)
        style.Button(
            win,
            text="Операции (%.2f %s)" % (sum_, currency),
            command=self._view_history,
            width=20,
        ).pack(pady=15, ipady=10)

        style.Button(win, text="Перевести", command=self._view_transfer, width=15).pack(
            pady=15, ipady=5
        )

        bottom = _ttk.Frame(win)
        bottom.pack(side="bottom")

        style.Button(bottom, text="Назад", command=win.close).pack(pady=5)

    def _view_history(self):
        win = window.Window2(self._window, "История")

    def _view_transfer(self):
        win = window.Window2(self._window, "Перевести")

    def _filter_accounts(self, row):
        if row[1] == self._id:
            return row
        return None
