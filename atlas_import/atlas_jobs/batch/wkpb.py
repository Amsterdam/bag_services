import csv
import datetime
import logging
import os

from atlas import models
from atlas_jobs import batch

log = logging.getLogger(__name__)


class ImportBeperkingcodeTask(object):
    name = "import Beperkingcode"

    def __init__(self, source_path):
        super().__init__()
        self.source = os.path.join(source_path, 'wpb_belemmeringcode.dat')

    def execute(self):
        with open(self.source) as f:
            rows = csv.reader(f, delimiter=';')
            objects = [self.process_row(row) for row in rows]

        models.Beperkingcode.objects.all().delete()
        models.Beperkingcode.objects.bulk_create(objects)

    def process_row(self, r):
        return models.Beperkingcode(
            pk=r[0],
            omschrijving=r[1],
        )


class ImportWkpbBroncodeTask(object):
    name = "import Wkpb Broncode"

    def __init__(self, source_path):
        super().__init__()
        self.source = os.path.join(source_path, 'wpb_broncode.dat')

    def execute(self):
        with open(self.source) as f:
            rows = csv.reader(f, delimiter=';')
            objects = [self.process_row(r) for r in rows]

        models.WkpbBroncode.objects.all().delete()
        models.WkpbBroncode.objects.bulk_create(objects)

    def process_row(self, r):
        return models.WkpbBroncode(
            pk=r[0],
            omschrijving=r[1],
        )


class ImportWkpbBrondocumentTask(object):
    name = "import Wkpb Brondocument"

    def __init__(self, source_path):
        super().__init__()
        self.source = os.path.join(source_path, 'wpb_brondocument.dat')
        self.cache = set()

    def execute(self):
        try:
            self.cache = set(models.WkpbBroncode.objects.values_list('pk', flat=True))

            with open(self.source) as f:
                rows = csv.reader(f, delimiter=';')
                objects = (self.process_row(r) for r in rows)
                object_dict = dict((o.pk, o) for o in objects)  # make unique; input contains duplicate IDs

            models.WkpbBrondocument.objects.all().delete()
            models.WkpbBrondocument.objects.bulk_create(object_dict.values())

        finally:
            self.cache.clear()

    def process_row(self, r):
        if r[4] == '0':
            pers_afsch = False
        else:
            pers_afsch = True

        bron_id = r[2] if r[2] in self.cache else None
        return models.WkpbBrondocument(
            pk=r[0],
            documentnummer=r[0],
            bron_id=bron_id,
            documentnaam=r[3][:21],  # afknippen, omdat data corrupt is (zie brondocument: 5820)
            persoonsgegeven_afschermen=pers_afsch,
            soort_besluit=r[5],
        )


class ImportBeperkingTask(object):
    name = "import Beperking"

    def __init__(self, source_path):
        super().__init__()
        self.source = os.path.join(source_path, 'wpb_belemmering.dat')
        self.cache = set()

    def execute(self):
        try:
            self.cache = set(models.Beperkingcode.objects.values_list('pk', flat=True))

            with open(self.source) as f:
                rows = csv.reader(f, delimiter=';')
                objects = [self.process_row(r) for r in rows]

            models.Beperking.objects.all().delete()
            models.Beperking.objects.bulk_create(objects)

        finally:
            self.cache.clear()

    def get_date(self, s):
        if s:
            return datetime.datetime.strptime(s, "%Y%m%d").date()
        else:
            return None

    def process_row(self, r):
        code_id = r[2] if r[2] in self.cache else None
        return models.Beperking(
            pk=r[0],
            inschrijfnummer=r[1],
            beperkingtype_id=code_id,
            datum_in_werking=self.get_date(r[3]),
            datum_einde=self.get_date(r[4]),
        )


class ImportWkpbBepKadTask(object):
    name = "import Beperking-Percelen"

    def __init__(self, source_path):
        super().__init__()
        self.source = os.path.join(source_path, 'wpb_belemmering_perceel.dat')
        self.beperkingen_cache = set()
        self.lki_cache = dict()

    def execute(self):
        try:
            self.beperkingen_cache = set(models.Beperking.objects.values_list('pk', flat=True))
            self.lki_cache = dict(models.LkiKadastraalObject.objects.values_list('aanduiding', 'pk'))

            with open(self.source) as f:
                rows = csv.reader(f, delimiter=';')
                objects = [o for o in (self.process_row(r) for r in rows) if o]

            models.BeperkingKadastraalObject.objects.all().delete()
            models.BeperkingKadastraalObject.objects.bulk_create(objects)

        finally:
            self.beperkingen_cache.clear()
            self.lki_cache.clear()

    def get_kadastrale_aanduiding(self, gem, sec, perc, app, index):
        return '{0}{1}{2:0>5}{3}{4:0>4}'.format(gem, sec, perc, app, index)

    def process_row(self, r):
        aanduiding = self.get_kadastrale_aanduiding(r[0], r[1], r[2], r[3], r[4])
        kadastraal_object_id = self.lki_cache.get(aanduiding)
        beperking_id = int(r[5])

        if beperking_id not in self.beperkingen_cache:
            log.warning('Non-existing Beperking: {0}'.format(beperking_id))
            return None

        if not kadastraal_object_id:
            log.warning("Unknown kadastraal object: %s", aanduiding)
            return None

        uid = '{0}_{1}'.format(beperking_id, aanduiding)

        return models.BeperkingKadastraalObject(
            pk=uid,
            beperking_id=beperking_id,
            kadastraal_object_id=kadastraal_object_id
        )
