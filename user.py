import functools as _ft
import tkinter as _tk
import tkinter.messagebox as _msg
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
        entries = [self._source, self._target, self._amount]
        source, target, amount = [e.get_strip() for e in entries]
        if not source or not target or not amount:
            return
        try:
            amount = float(amount)
        except:
            return

        if self._db.make_transaction(source, target, amount):
            util.show_info("Транзакция добавлена")
        else:
            util.show_error("Ошибка")
        self._accounts.update_data()

    def _create_widgets(self):
        _ttk.Label(self, text=self._name).pack(pady=25)

        self._accounts = _ttk.Frame(self)
        self._accounts.pack()
        self._update_accounts(self._accounts)

        style.Button(self, text="Новый счёт/карта", command=self._new_account).pack(
            pady=25
        )

        style.Button(self, text="Выйти", command=self.close, width=15).pack(
            pady=25, side="bottom"
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

    def _add_back_button(self, master, win=None):
        if win is None:
            win = master
        style.Button(master, text="Назад", command=win.close, width=15).pack(
            pady=25, side="bottom"
        )

    def _new_account(self):
        self._window = win = window.Window2(self, "Новый счёт/карта")

        self._account_btn = style.Button(
            win,
            text="Счёт",
            command=lambda: self._toggle_type(self._account_btn, self._card_btn, False),
            width=15,
        )
        self._account_btn.pack(pady=5)
        self._card_btn = style.Button(
            win,
            text="Карта",
            command=lambda: self._toggle_type(self._card_btn, self._account_btn, True),
            width=15,
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

        style.Button(bottom, text="Открыть", command=self._add_account, width=15).pack(
            pady=5
        )
        self._add_back_button(bottom, win)

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
        self._account_data = account_data
        self._currency = account_data[4]
        self._cur_sym = self._db.get_currency_symbol(self._currency)

        self._window = win = window.Window2(self, "Счёт")

        win.card = style.Button(win, state="disabled", width=20)
        win.card.pack(pady=25)
        win.transactions = style.Button(win, command=self._view_history, width=20)
        win.transactions.pack(pady=15, ipady=10)
        self._update_account_buttons(win)

        style.Button(win, text="Перевести", command=self._view_transfer, width=15).pack(
            pady=15, ipady=5
        )

        self._add_back_button(win)

    def _update_account_buttons(self, win):
        account_data = (
            self._account_data[3],
            self._cur_sym,
            self._account_id,
            self._account_data[2],
        )
        account_text = "%.2f %s\n ID %d. %s" % account_data
        card = self._db.get_card(self._account_id)
        if card is not None:
            account_text += "\n%s" % card
        win.card.config(text=account_text)

        sum_ = self._db.sum_transactions(self._account_id, self._currency)
        sum_text = "Операции (%.2f %s)" % (sum_, self._cur_sym)
        win.transactions.config(text=sum_text)

    def _view_history(self):
        win = window.Window2(self._window, "История")
        sum_ = self._db.sum_transactions(self._account_id, self._currency)
        style.Button(
            win,
            text="Операции (%.2f %s)" % (sum_, self._cur_sym),
            width=20,
            state="disabled",
        ).pack(pady=15, ipady=10)

        columns = ["Дата", "Описание", "Сумма"]
        history = tableview.TableView(
            win, self._db, "transactions", columns, row_func=self._format_transaction
        )
        history.config(show="tree")
        history.column("#1", width=75)
        history.column("#2", width=180)
        history.column("#3", width=45)
        history.update_data()
        self._reverse_rows(history)
        history.pack(fill="x")

        self._add_back_button(win)

    def _format_transaction(self, row):
        id_ = str(self._account_id)
        if row[1] != id_ and row[2] != id_:
            return None

        date = dates.convert_format(row[-1])
        if id_ == row[1]:
            description = (
                row[2]
                if not self._db.is_account(row[2])
                else "Перевод\nна счёт %s" % row[2]
            )
        else:
            description = (
                row[1]
                if not self._db.is_account(row[1])
                else "Перевод\nсо счёта %s" % row[1]
            )

        if row[4] != self._currency:
            amount = self._db.convert_currency(float(row[3]), row[4], self._currency)
        else:
            amount = float(row[3])

        if id_ == row[1]:
            sum_ = "-" + str(amount)
        else:
            sum_ = "+" + str(amount)

        return (date, description, sum_)

    def _reverse_rows(self, tree):
        for item in tree.get_children():
            tree.move(item, "", 0)

    def _view_transfer(self):
        win = window.Window2(self._window, "Перевести")

        text = "с %s\n%.2f %s" % (*self._account_data[2:4], self._cur_sym)
        style.Button(win, text=text, state="disabled", width=20).pack(pady=25)

        for account in self._db.get_accounts(self._id):
            if account[0] == self._account_id:
                continue
            name, balance, currency = account[2:5]
            currency = self._db.get_currency_symbol(currency)
            text = "%.2f %s\n%s" % (balance, currency, name)
            cmd = _ft.partial(self._select_account, account[0])
            style.Button(win, text=text, command=cmd, width=20).pack(pady=5)

        _ttk.Label(win, text="ID счёта / карта").pack(pady=5)
        self._target_account = style.Entry(win)
        self._target_account.pack(pady=5)

        _ttk.Label(win, text="Сумма (%s)" % self._cur_sym).pack(pady=5)
        self._target_amount = style.Entry(win)
        self._target_amount.pack(pady=5)

        bottom = _ttk.Frame(win)
        bottom.pack(side="bottom")
        style.Button(
            bottom, text="Перевести", command=self._make_transfer, width=15
        ).pack(pady=5)
        self._add_back_button(bottom, win)

    def _select_account(self, text):
        self._target_account.delete(0, "end")
        self._target_account.insert(0, text)

    def _make_transfer(self):
        target, amount = (
            self._target_account.get_strip(),
            self._target_amount.get_strip(),
        )
        if not target:
            return util.show_error("Введите счёт или карту для перевода")
        if not amount or not util.is_float(amount):
            return util.show_error("Введите сумму для перевода")

        card = self._db.get_card_account(target)
        if card is not None:
            target = card
        elif not self._db.is_account(target):
            return util.show_error("Счёт не найден")

        amount = float(amount)
        if amount < 0 or amount > self._account_data[3]:
            return util.show_error("Введите сумму от 0 до %.2f" % self._account_data[3])

        if not _msg.askyesno("Подтверждение", "Перевести?"):
            return
        print(target, amount)

    def _filter_accounts(self, row):
        if row[1] == self._id:
            return row
        return None
