from contextlib import contextmanager
import csv
import os

from atlas import models
from . import uva2


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


class RowBasedUvaTask(object):

    def __init__(self, source):
        self.source = source

    def execute(self):
        with uva_reader(self.source) as rows:
            for r in rows:
                self.process_row(r)

    def process_row(self, r):
        raise NotImplementedError()



class ImportBrnTask(RowBasedUvaTask):

    name = "import BRN"

    def process_row(self, r):
        b, _ = models.Bron.objects.get_or_create(code=r['Code'])
        b.omschrijving = r['Omschrijving']
        b.save()


class ImportStsTask(RowBasedUvaTask):

    name = "import STS"

    def process_row(self, r):
        s, _ = models.Status.objects.get_or_create(code=r['Code'])
        s.omschrijving = r['Omschrijving']
        s.save()


class ImportGmeTask(RowBasedUvaTask):

    name = "import GMT"

    def process_row(self, r):
        if not uva2.uva_geldig(r['TijdvakGeldigheid/begindatumTijdvakGeldigheid'],
                               r['TijdvakGeldigheid/einddatumTijdvakGeldigheid']):
            return

        id = r['sleutelVerzendend']
        code = r['Gemeentecode']
        naam = r['Gemeentenaam']
        verzorgingsgebied = uva2.uva_indicatie(r['IndicatieVerzorgingsgebied'])
        vervallen = uva2.uva_indicatie(r['Indicatie-vervallen'])

        g, _ = models.Gemeente.objects.get_or_create(pk=id, defaults=dict(
            code=code,
            naam=naam,
        ))
        g.code = code
        g.naam = naam
        g.verzorgingsgebied = verzorgingsgebied
        g.vervallen = vervallen
        g.save()


class ImportSdlTask(RowBasedUvaTask):

    name = "import SDL"

    def process_row(self, r):
        if not uva2.uva_geldig(r['TijdvakGeldigheid/begindatumTijdvakGeldigheid'],
                               r['TijdvakGeldigheid/einddatumTijdvakGeldigheid']):
            return

        if not uva2.uva_geldig(r['SDLGME/TijdvakRelatie/begindatumRelatie'],
                               r['SDLGME/TijdvakRelatie/einddatumRelatie']):
            return

        id = r['sleutelVerzendend']
        code = r['Stadsdeelcode']
        naam = r['Stadsdeelnaam']
        gemeente = models.Gemeente.objects.get(pk=r['SDLGME/GME/sleutelVerzendend'])

        s, _ = models.Stadsdeel.objects.get_or_create(pk=id, defaults=dict(
            code=code,
            naam=naam,
            gemeente=gemeente,
        ))
        s.code = code
        s.naam = naam
        s.vervallen = uva2.uva_indicatie(r['Indicatie-vervallen'])
        s.gemeente = gemeente
        s.save()


class ImportBrtTask(RowBasedUvaTask):

    name = "import BRT"

    def process_row(self, r):
        if not uva2.uva_geldig(r['TijdvakGeldigheid/begindatumTijdvakGeldigheid'],
                               r['TijdvakGeldigheid/einddatumTijdvakGeldigheid']):
            return

        if not uva2.uva_geldig(r['BRTSDL/TijdvakRelatie/begindatumRelatie'],
                               r['BRTSDL/TijdvakRelatie/einddatumRelatie']):
            return

        id = r['sleutelVerzendend']
        code = r['Buurtcode']
        naam = r['Buurtnaam']
        stadsdeel = models.Stadsdeel.objects.get(pk=r['BRTSDL/SDL/sleutelVerzendend'])

        b, _ = models.Buurt.objects.get_or_create(pk=id, defaults=dict(
            code=code,
            naam=naam,
            stadsdeel=stadsdeel,
        ))
        b.code = code
        b.naam = naam
        b.stadsdeel = stadsdeel
        b.vervallen = uva2.uva_indicatie(r['Indicatie-vervallen'])
        b.save()


class ImportJob(object):

    name = "atlas-import"

    def __init__(self):
        self.base_dir = 'atlas_jobs/fixtures/examplebag'

    def tasks(self):
        return [
            ImportBrnTask(os.path.join(self.base_dir, 'BRN_20071001_J_20000101_20050101.UVA2')),
            ImportStsTask(os.path.join(self.base_dir, 'STS_20071001_J_20000101_20050101.UVA2')),
            ImportGmeTask(os.path.join(self.base_dir, 'GME_20071001_J_20000101_20050101.UVA2')),
            ImportSdlTask(os.path.join(self.base_dir, 'SDL_20071001_J_20000101_20050101.UVA2')),
            ImportBrtTask(os.path.join(self.base_dir, 'BRT_20071001_J_20000101_20050101.UVA2')),
        ]


