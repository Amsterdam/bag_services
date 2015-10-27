from contextlib import contextmanager
import csv
import datetime
import os

from datasets.generic.cache import AbstractCacheBasedTask

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

    return e is None or s is None or (s <= now < e)


def _wrap_uva_row(r, headers):
    return dict(zip(headers, r))


@contextmanager
def uva_reader(source):
    if not os.path.exists(source):
        raise ValueError("File not found: {}".format(source))

    with open(source, encoding='cp1252') as f:
        rows = csv.reader(f, delimiter=';', quoting=csv.QUOTE_NONE)
        # skip VAN
        next(rows)
        # skip TM
        next(rows)
        # skip Historie
        next(rows)

        headers = next(rows)

        yield (_wrap_uva_row(r, headers) for r in rows)


def resolve_file(path, code):
    if not code:
        raise ValueError("No code specified")

    prefix = code + '_'
    matches = [f for f in os.listdir(path) if f.startswith(prefix)]
    if len(matches) != 1:
        raise ValueError("Could not find file starting with {} in {}".format(prefix, path))

    return os.path.join(path, matches[0])


def geldig_tijdvak(r):
    return uva_geldig(r['TijdvakGeldigheid/begindatumTijdvakGeldigheid'],
                      r['TijdvakGeldigheid/einddatumTijdvakGeldigheid'])


def geldige_relatie(row, relatie):
    begin = row['{}/TijdvakRelatie/begindatumRelatie'.format(relatie)]

    try:
        end = row['{}/TijdvakRelatie/einddatumRelatie'.format(relatie)]
    except KeyError:
        end = row['{}/TijdvakRelatie/eindatumRelatie'.format(relatie)]  # sic!

    return uva_geldig(begin, end)


def geldige_relaties(row, *relaties):
    for relatie in relaties:
        if not geldige_relatie(row, relatie):
            return False
    return True


class AbstractUvaTask(AbstractCacheBasedTask):
    """
    Basic task for processing UVA2 files
    """
    code = ""

    def __init__(self, source, cache):
        super().__init__(cache)
        self.source = resolve_file(source, self.code)

    def execute(self):
        with uva_reader(self.source) as rows:
            for r in rows:
                self.process_row(r)

    def process_row(self, r):
        raise NotImplementedError()


def process_uva2(path, file_code, process_row_callback):
    """
    Process a UVA2 file

    :param path: path containing the UVA2 file
    :param file_code: three-letter code identifying the file
    :param process_row_callback: function taking one parameter that is called on every row
    :return: an iterable over the results of process_row_callback
    """
    source = resolve_file(path, file_code)
    with uva_reader(source) as rows:
        return [result for result in (process_row_callback(r) for r in rows) if result]