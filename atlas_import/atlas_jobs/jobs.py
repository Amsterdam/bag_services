import csv
import os
from atlas import models


def download_datafiles():
    pass


def import_blah_file():
    pass


class ImportBrnTask():

    name = "import BRN"

    def __init__(self, source):
        self.source = source

    def execute(self):
        with open(self.source) as csv_file:
            rows = csv.reader(csv_file, delimiter=';')
            for _ in range(4):
                next(rows)

            for r in rows:
                b, _ = models.Bron.objects.get_or_create(code=r[0])
                b.omschrijving = r[1]
                b.save()


class ImportJob(object):

    name = "atlas-import"

    def __init__(self):
        self.base_dir = 'atlas_jobs/fixtures/examplebag'

    def tasks(self):
        return [
            ImportBrnTask(os.path.join(self.base_dir, 'BRN_20071001_J_20000101_20050101.UVA2')),
        ]
