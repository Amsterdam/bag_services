import csv
import datetime
import logging
import os
import re
from contextlib import contextmanager

log = logging.getLogger(__name__)

uva2_date_re = re.compile(r'^.*/[a-zA-Z]+_(\d{8})_N_\d{8}_\d{8}\.uva2$', re.IGNORECASE)
one_date_re = re.compile(r'^.*?_(\d{8})\.[a-z]{3}$', re.IGNORECASE)


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
    return {'j': True, 'n': False}.get(s.lower(), None)


def uva_geldig(start, eind):
    s = uva_datum(start)
    e = uva_datum(eind)

    now = datetime.date.today()

    return e is None or s is None or (s <= now < e)


def _wrap_row(r, headers):
    return dict(zip(headers, r))


@contextmanager
def _context_reader(
        source, skip=3, quotechar=None, quoting=csv.QUOTE_NONE,
        with_header=True):
    if not os.path.exists(source):
        raise ValueError("File not found: {}".format(source))

    with open(source, encoding='cp1252') as f:
        rows = csv.reader(f, delimiter=';', quotechar=quotechar, quoting=quoting)
        for i in range(skip):
            next(rows)

        if with_header:
            headers = next(rows)
            yield (_wrap_row(r, headers) for r in rows)
        else:
            yield (r for r in rows)


def resolve_file(path, code, extension='UVA2'):
    if not code:
        raise ValueError("No code specified")

    prefix = code + '_'
    matches = [os.path.join(path, f) for f in os.listdir(path) if f.startswith(prefix) and f.endswith(extension)]
    if not matches:
        raise ValueError("Could not find file starting with {} in {}".format(prefix, path))
    matches_with_mtime = [(os.path.getmtime(f), f) for f in matches]
    match = sorted(matches_with_mtime)[-1]
    return match[1]


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


def logging_callback(source_path, original_callback):

    def result(r):
        try:
            return original_callback(r)
        except:
            log.error("Could not process row while parsing %s", source_path)
            for k, v in r.items():
                log.error("%s: '%s'", k, v)
            raise

    return result


def get_uva2_filedate(path, file_code):
    """
    Extract date from uva2 filename
    :param path: filename
    :param file_code: uva2 filename code
    :return: datetime.date or None
    """
    source = resolve_file(path, file_code)

    m = re.match(uva2_date_re, source)
    if m and len(m.groups()):
        return uva_datum(m.groups()[0])


def get_filedate(path, file_code):
    """
    Extract date from csv filename
    :param path:  filename
    :param file_code: csv filename code
    :return: datetime.date or None
    """
    source = resolve_file(path, file_code, extension='csv')

    m = re.match(one_date_re, source)
    if m and len(m.groups()):
        return uva_datum(m.groups()[0])


def process_uva2(path, file_code, process_row_callback):
    """
    Process a UVA2 file

    :param path: path containing the UVA2 file
    :param file_code: three-letter code identifying the file
    :param process_row_callback: function taking one parameter that is called on every row
    :return: an iterable over the results of process_row_callback
    """
    source = resolve_file(path, file_code)

    cb = logging_callback(source, process_row_callback)

    with _context_reader(source) as rows:
        for row in rows:
            result = cb(row)
            if result:
                yield result


def process_csv(path, file_code, process_row_callback, with_header=True):
    source = resolve_file(path, file_code, extension='csv')

    cb = logging_callback(source, process_row_callback)

    with _context_reader(
            source, skip=0, quotechar='"',
            quoting=csv.QUOTE_MINIMAL, with_header=with_header) as rows:
        for row in rows:
            result = cb(row)
            if result:
                yield result


def read_landelijk_id_mapping(path, file_code):
    source = resolve_file(path, file_code, extension='dat')
    result = dict()
    with open(source) as f:
        reader = csv.reader(f, delimiter=';')
        next(reader)  # skip header
        for row in reader:
            if len(row) >= 2:
                result[row[0]] = row[1]

    return result


def read_indicaties(path):
    """
    Read landelijk BAG id to (indicatie geconstateerd, in onderzoek) mapping.

    :param path: path containing the CSV file
    """
    file_code = 'VBO_geconstateerd-inonderzoek'
    filename = resolve_file(path, file_code, extension='csv')

    with open(filename, encoding='cp1252') as f:
        rows = csv.reader(f, delimiter=';')

        mapping = {}
        for _id, geconst, inonderz in rows:
            mapping[_id] = (uva_indicatie(geconst), uva_indicatie(inonderz))

        return mapping


def read_gebruiksdoelen(path):
    """
    Read CSV file with gebruiksdoel, gebruiksdoel plus data.

    :param path: path containing the CSV file
    """
    file_code = 'VBO_gebruiksdoelen'
    filename = resolve_file(path, file_code, extension='csv')

    out = []
    with open(filename, encoding='cp1252') as f:
        rows = csv.reader(f, delimiter=';')
        out = list(rows)

    return out
