from contextlib import contextmanager
import csv
import os
from atlas import models


@contextmanager
def uva_reader(source):
    with open(source) as f:
        rows = csv.reader(f, delimiter=';')
        for _ in range(4):
            next(rows)

        yield rows


class ImportBrnTask():

    name = "import BRN"

    def __init__(self, source):
        self.source = source

    def execute(self):
        with uva_reader(self.source) as rows:
            for r in rows:
                b, _ = models.Bron.objects.get_or_create(code=r[0])
                b.omschrijving = r[1]
                b.save()


class ImportStsTask(object):

    name = "import STS"

    def __init__(self, source):
        self.source = source

    def execute(self):
        with uva_reader(self.source) as rows:
            for r in rows:
                s, _ = models.Status.objects.get_or_create(code=r[0])
                s.omschrijving = r[1]
                s.save()


class ImportJob(object):

    name = "atlas-import"

    def __init__(self):
        self.base_dir = 'atlas_jobs/fixtures/examplebag'

    def tasks(self):
        return [
            ImportBrnTask(os.path.join(self.base_dir, 'BRN_20071001_J_20000101_20050101.UVA2')),
            ImportStsTask(os.path.join(self.base_dir, 'STS_20071001_J_20000101_20050101.UVA2')),
        ]
