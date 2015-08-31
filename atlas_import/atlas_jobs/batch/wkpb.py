import csv
import datetime
import logging
import os

from atlas import models
from atlas_jobs import batch

log = logging.getLogger(__name__)


class ImportBeperkingcodeTask(batch.AbstractOrmTask):
    name = "import Beperkingcode"

    def __init__(self, source_path):
        super().__init__()
        self.source = os.path.join(source_path, 'wpb_belemmeringcode.dat')

    def execute(self):
        with open(self.source) as f:
            rows = csv.reader(f, delimiter=';')
            for row in rows:
                self.process_row(row)

    def process_row(self, r):
        self.merge(models.Beperkingcode, r[0], dict(
            omschrijving=r[1],
        ))


class ImportWkpbBroncodeTask(batch.AbstractOrmTask):
    name = "import Wkpb Broncode"

    def __init__(self, source_path):
        super().__init__()
        self.source = os.path.join(source_path, 'wpb_broncode.dat')

    def execute(self):
        with open(self.source) as f:
            rows = csv.reader(f, delimiter=';')
            for row in rows:
                self.process_row(row)

    def process_row(self, r):
        self.merge(models.WkpbBroncode, r[0], dict(
            omschrijving=r[1],
        ))


class ImportWkpbBrondocumentTask(batch.AbstractOrmTask):
    name = "import Wkpb Brondocument"

    def __init__(self, source_path):
        super().__init__()
        self.source = os.path.join(source_path, 'wpb_brondocument.dat')

    def execute(self):
        with open(self.source) as f:
            rows = csv.reader(f, delimiter=';')
            for row in rows:
                self.process_row(row)

    def process_row(self, r):
        if r[4] == '0':
            pers_afsch = False
        else:
            pers_afsch = True

        self.merge(models.WkpbBrondocument, r[0], dict(
            documentnummer=r[0],
            bron_id=self.foreign_key_id(models.WkpbBroncode, r[2]),
            documentnaam=r[3][:21],  # afknippen, omdat data corrupt is (zie brondocument: 5820)
            persoonsgegeven_afschermen=pers_afsch,
            soort_besluit=r[5],
        ))


class ImportBeperkingTask(batch.AbstractOrmTask):
    name = "import Beperking"

    def __init__(self, source_path):
        super().__init__()
        self.source = os.path.join(source_path, 'wpb_belemmering.dat')

    def execute(self):
        with open(self.source) as f:
            rows = csv.reader(f, delimiter=';')
            for row in rows:
                self.process_row(row)

    def get_date(self, s):
        if s:
            return datetime.datetime.strptime(s, "%Y%m%d").date()
        else:
            return None

    def process_row(self, r):
        self.merge(models.Beperking, r[0], dict(
            inschrijfnummer=r[1],
            beperkingtype_id=self.foreign_key_id(models.Beperkingcode, r[2]),
            datum_in_werking=self.get_date(r[3]),
            datum_einde=self.get_date(r[4]),
        ))


class ImportWkpbBepKadTask(batch.AbstractOrmTask):
    name = "import Beperking-Percelen"

    def __init__(self, source_path):
        super().__init__()
        self.source = os.path.join(source_path, 'wpb_belemmering_perceel.dat')

    def execute(self):
        with open(self.source) as f:
            rows = csv.reader(f, delimiter=';')
            for row in rows:
                self.process_row(row)

    def get_kadastrale_aanduiding(self, gem, sec, perc, app, index):
        return '{0}{1}{2:0>5}{3}{4:0>4}'.format(gem, sec, perc, app, index)

    def process_row(self, r):
        k = self.get_kadastrale_aanduiding(r[0], r[1], r[2], r[3], r[4])
        uid = '{0}_{1}'.format(r[5], k)

        try:
            bp = models.Beperking.objects.get(pk=r[5])
        except models.Beperking.DoesNotExist:
            log.warning('Non-existing Beperking: {0}'.format(r[5]))
            return

        try:
            ko = models.LkiKadastraalObject.objects.get(aanduiding=k)
        except models.LkiKadastraalObject.DoesNotExist:
            log.warning('Non-existing LkiKadastraalObject: {0}'.format(k))
            return

        self.merge(models.BeperkingKadastraalObject, uid, dict(
            beperking=bp,
            kadastraal_object=ko
        ))
