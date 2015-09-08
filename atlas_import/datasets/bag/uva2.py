from contextlib import contextmanager
import csv
import datetime
import os

__author__ = 'yigalduppen'


def uva_datum(s):
    if not s:
        return None

    return datetime.datetime.strptime(s, "%Y%m%d").date()


def uva_nummer(s):
    if not s:
        return None

    return int(s, 10)


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
    if not os.path.exists(source):
        raise ValueError("File not found: {}".format(source))

    with open(source, encoding='cp1252') as f:
        rows = csv.reader(f, delimiter=';')
        # skip VAN
        next(rows)
        # skip TM
        next(rows)
        # skip Historie
        next(rows)

        headers = next(rows)

        yield (_wrap_uva_row(r, headers) for r in rows)


def resolve_file(path, code):
    prefix = code + '_'
    matches = [f for f in os.listdir(path) if f.startswith(prefix)]
    if len(matches) != 1:
        raise ValueError("Could not find file starting with {} in {}".format(prefix, path))

    return os.path.join(path, matches[0])


def geldig_tijdvak(r):
    return uva_geldig(r['TijdvakGeldigheid/begindatumTijdvakGeldigheid'],
                      r['TijdvakGeldigheid/einddatumTijdvakGeldigheid'])


def geldige_relatie(row, relatie):
    return uva_geldig(row['{}/TijdvakRelatie/begindatumRelatie'.format(relatie)],
                      row['{}/TijdvakRelatie/einddatumRelatie'.format(relatie)])

def geldige_relaties(row, *relaties):
    for relatie in relaties:
        if not geldige_relatie(row, relatie):
            return False
    return True
