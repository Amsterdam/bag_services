from contextlib import contextmanager
import csv
import os

from atlas import models
from . import uva2


@contextmanager
def uva_reader(source):
    with open(source) as f:
        rows = csv.reader(f, delimiter=';')
        for _ in range(4):
            next(rows)

        yield rows


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
        b, _ = models.Bron.objects.get_or_create(code=r[0])
        b.omschrijving = r[1]
        b.save()


class ImportStsTask(RowBasedUvaTask):

    name = "import STS"

    def process_row(self, r):
        s, _ = models.Status.objects.get_or_create(code=r[0])
        s.omschrijving = r[1]
        s.save()


class ImportGmeTask(RowBasedUvaTask):

    name = "import GMT"

    def process_row(self, r):
        if not uva2.uva_geldig(r[8], r[9]):
            return

        id = r[0]
        code = r[1]
        naam = r[2]
        verzorgingsgebied = uva2.uva_indicatie(r[4])
        vervallen = uva2.uva_indicatie(r[7])

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
        if not uva2.uva_geldig(r[8], r[9]):
            return

        if not uva2.uva_geldig(r[12], r[13]):
            return

        id = r[0]
        code = r[1]
        naam = r[2]
        gemeente = models.Gemeente.objects.get(pk=r[10])

        s, _ = models.Stadsdeel.objects.get_or_create(pk=id, defaults=dict(
            code=code,
            naam=naam,
            gemeente=gemeente,
        ))
        s.code = code
        s.naam = naam
        s.gemeente = gemeente
        s.save()


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
        ]


