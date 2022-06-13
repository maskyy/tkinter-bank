import sqlite3 as _sql

import login as _login

__all__ = ["Database"]

_default_name = "files/bank.sqlite3"

_init_script = """
PRAGMA encoding = "UTF-8";
PRAGMA foreign_keys = 1;

PRAGMA journal_mode = WAL;
PRAGMA synchronous = NORMAL;

CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    login TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL,
    full_name TEXT NOT NULL,
    phone TEXT NOT NULL CHECK(length(phone) = 12),
    passport TEXT NOT NULL,
    last_charged TEXT NOT NULL DEFAULT CURRENT_DATE,
    blocked INTEGER NOT NULL DEFAULT 0
) STRICT;

CREATE TABLE IF NOT EXISTS currencies (
    name TEXT PRIMARY KEY,
    symbol TEXT NOT NULL
) STRICT;

CREATE TABLE IF NOT EXISTS exchange_rates (
    source TEXT NOT NULL,
    target TEXT NOT NULL,
    rate REAL NOT NULL CHECK(rate > 0),
    PRIMARY KEY(source, target),
    FOREIGN KEY(source) REFERENCES currencies(name) ON DELETE CASCADE,
    FOREIGN KEY(target) REFERENCES currencies(name) ON DELETE CASCADE
) STRICT;

CREATE TABLE IF NOT EXISTS accounts (
    id INTEGER PRIMARY KEY,
    owner_id INTEGER NOT NULL,
    name TEXT DEFAULT NULL,
    balance REAL NOT NULL,
    currency TEXT NOT NULL,
    FOREIGN KEY(owner_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY(currency) REFERENCES currencies(name) ON DELETE CASCADE
) STRICT;

CREATE TABLE IF NOT EXISTS cards (
    number TEXT PRIMARY KEY CHECK(length(number) = 16),
    account INTEGER NOT NULL,
    FOREIGN KEY(account) REFERENCES accounts(id) ON DELETE CASCADE
) STRICT;

CREATE TABLE IF NOT EXISTS transactions (
    id INTEGER PRIMARY KEY,
    source TEXT NOT NULL,
    target TEXT NOT NULL,
    amount REAL NOT NULL,
    source_currency TEXT NOT NULL,
    target_currency TEXT NOT NULL,
    time TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(source_currency) REFERENCES currencies(name) ON DELETE CASCADE,
    FOREIGN KEY(target_currency) REFERENCES currencies(name) ON DELETE CASCADE
) STRICT;

CREATE TABLE IF NOT EXISTS logins (
    login TEXT PRIMARY KEY,
    password TEXT NOT NULL,
    role TEXT NOT NULL DEFAULT "cashier"
) STRICT;
"""

_exit_script = """
PRAGMA analysis_limit = 1000;
PRAGMA optimize;
"""


class Database:
    def __init__(self, filename=_default_name):
        self._con = _sql.connect(filename)
        self._cur = self._con.cursor()
        self._cur.executescript(_init_script)

    def __del__(self):
        self._cur.executescript(_exit_script)
        self._cur.close()
        self.save()
        self._con.close()

    def save(self):
        self._con.commit()

    def get_table(self, name):
        return self._cur.execute("SELECT * FROM %s" % name).fetchall()

    def execute(self, *args):
        return self._cur.execute(*args)

    def get_columns(self, table):
        self._cur.execute("SELECT name FROM PRAGMA_TABLE_INFO('%s')" % table)
        return [name[0] for name in self._cur.fetchall()]

    def get_user(self, login):
        self._cur.execute("SELECT * FROM users WHERE login = ?", (login,))
        return self._cur.fetchone()

    def register_user(self, login, password, full_name, phone, passport):
        try:
            password = _login.hash_pwd(password)
            self._cur.execute(
                "INSERT INTO users VALUES (NULL, ?, ?, ?, ?, ?, CURRENT_DATE, 0)",
                (login, password, full_name, phone, passport),
            )
            self.save()
            return True
        except Exception as e:
            print(e)
            return False

    def change_user_password(self, login, new_password):
        self._cur.execute(
            "UPDATE logins SET password = ? WHERE login = ?", (new_password, login)
        )
        self.save()
