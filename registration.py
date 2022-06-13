import re as _re
import tkinter as _tk
import tkinter.ttk as _ttk

import dates
import logo
import style
import tableview
import util
import window
from db_sqlite import Database


class Registration(window.Window2):
    def __init__(self, master=None, db=None):
        super().__init__(master, "Регистрация")
        self._db = db
        self._create_widgets()

    def _create_widgets(self):
        frame = _ttk.Frame(self)
        frame.pack(expand=True)
        fields = ["Логин", "Пароль", "ФИО", "Телефон", "Паспорт"]
        self._entries = []
        for l, e in zip(*self._create_labels_entries(frame, fields)):
            l.pack(pady=5)
            e.pack(pady=5)
            if l["text"] == "Пароль":
                e.config(show="*")

            self._entries.append(e)

        self._phone_regex = _re.compile(r"^\+[0-9]{11}$")
        style.Button(
            frame, text="Зарегистрироваться", command=self._on_register, width=20
        ).pack(pady=5)
        style.Button(frame, text="Назад", command=self.close).pack(pady=5)

    def _create_labels_entries(self, master, names):
        labels, entries = [], []
        for n in names:
            label = _ttk.Label(master, text=n)
            entry = style.Entry(master)
            labels.append(label)
            entries.append(entry)

        return labels, entries

    def _validate_data(self):
        data = [e.get_strip() for e in self._entries]
        login, password, name, phone, passport = data

        if not login:
            return util.show_error("Введите логин")
        elif self._db.get_user(login):
            return util.show_error("Логин занят")

        if not password:
            return util.show_error("Введите пароль")
        if not name:
            return util.show_error("Введите имя")
        if not phone or not self._phone_regex.match(phone):
            return util.show_error("Введите номер телефона в формате +XXXXXXXXXXX")
        if not passport:
            return util.show_error(
                "Введите паспортные данные (серия, номер, кем выдан и дата выдачи)"
            )
        return True

    def _on_register(self):
        if not self._validate_data():
            return

        data = [e.get_strip() for e in self._entries]
        if not self._db.register_user(*data):
            return util.show_error("Не удалось зарегистрироваться")
        else:
            return util.show_info("Регистрация успешна")
            self.close()
