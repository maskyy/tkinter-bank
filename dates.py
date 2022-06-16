import datetime as _dt

_datetime_format = "%Y-%m-%d %H:%M:%S"
_date_format = "%Y-%m-%d"
_show_format = "%d.%m.%Y"


def to_date(s):
    try:
        return _dt.datetime.strptime(s, _date_format).date()
    except ValueError:
        return None


def from_date(date):
    return date.strftime(_date_format)


def from_datetime(date):
    return date.strftime(_datetime_format)


def now():
    return _dt.datetime.now().strftime(_date_format)


def convert_format(s):
    return _dt.datetime.strptime(s, _datetime_format).strftime(_show_format)
