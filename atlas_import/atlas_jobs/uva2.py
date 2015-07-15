from contextlib import contextmanager
import csv
import datetime

__author__ = 'yigalduppen'


def uva_datum(s):
    if not s:
        return None

    return datetime.datetime.strptime(s, "%Y%m%d").date()


def uva_indicatie(s):
    """
    Translates an indicatie (J/N) to True/False
    """
    return {'J': True, 'N': False}.get(s, False)


def uva_geldig(start, eind):
    s = uva_datum(start)
    e = uva_datum(eind)

    now = datetime.date.today()

    return e is None or (s <= now < e)


def _wrap_uva_row(r, headers):
    return dict(zip(headers, r))


@contextmanager
def uva_reader(source):
    with open(source) as f:
        rows = csv.reader(f, delimiter=';')
        # skip VAN
        next(rows)
        # skip TM
        next(rows)
        # skip Historie
        next(rows)

        headers = next(rows)

        yield (_wrap_uva_row(r, headers) for r in rows)