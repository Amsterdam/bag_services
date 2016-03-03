import csv
import datetime
import logging
import os

from django import db
from django.conf import settings

import datasets.brk.models as brk
from batch import batch
from datasets.generic import kadaster, database
from . import models

log = logging.getLogger(__name__)


class ImportBeperkingcodeTask(batch.BasicTask):
    name = "Import Beperkingcode"

    def __init__(self, source_path):
        super().__init__()
        self.source = os.path.join(source_path, 'wpb_belemmeringcode.dat')

    def before(self):
        database.clear_models(models.Beperkingcode)

    def after(self):
        pass

    def process(self):
        with open(self.source) as f:
            rows = csv.reader(f, delimiter=';')
            objects = [self.process_row(row) for row in rows]

        models.Beperkingcode.objects.bulk_create(objects, batch_size=database.BATCH_SIZE)

    def process_row(self, r):
        return models.Beperkingcode(
            pk=r[0],
            omschrijving=r[1],
        )


class ImportWkpbBroncodeTask(batch.BasicTask):
    name = "Import Wkpb Broncode"

    def __init__(self, source_path):
        super().__init__()
        self.source = os.path.join(source_path, 'wpb_broncode.dat')

    def before(self):
        database.clear_models(models.Broncode)

    def after(self):
        pass

    def process(self):
        with open(self.source) as f:
            rows = csv.reader(f, delimiter=';')
            objects = [self.process_row(r) for r in rows]

        models.Broncode.objects.all().delete()
        models.Broncode.objects.bulk_create(objects, batch_size=database.BATCH_SIZE)

    def process_row(self, r):
        return models.Broncode(
            pk=r[0],
            omschrijving=r[1],
        )


class ImportBeperkingTask(batch.BasicTask):
    name = "Import Beperking"

    def __init__(self, source_path):
        super().__init__()
        self.source = os.path.join(source_path, 'wpb_belemmering.dat')
        self.codes = set()

    def before(self):
        database.clear_models(models.Beperking)
        self.codes = set(models.Beperkingcode.objects.values_list('pk', flat=True))

    def after(self):
        self.codes.clear()

    def process(self):
        with open(self.source) as f:
            rows = csv.reader(f, delimiter=';')
            objects = [obj for obj in (self.process_row(r) for r in rows) if obj]

        models.Beperking.objects.bulk_create(objects, batch_size=database.BATCH_SIZE)

    def get_date(self, s):
        if s:
            return datetime.datetime.strptime(s, "%Y%m%d").date()
        else:
            return None

    def process_row(self, r):
        code_id = r[2] if r[2] in self.codes else None
        datum_einde = self.get_date(r[4])
        vandaag = datetime.date.today()
        if datum_einde and datum_einde < vandaag:
            log.warning('Beperking {} no longer valid; end date {} was before {}'.format(datum_einde, vandaag))
            return None

        return models.Beperking(
            pk=r[0],
            inschrijfnummer=r[1],
            beperkingtype_id=code_id,
            datum_in_werking=self.get_date(r[3]),
            datum_einde=datum_einde,
        )


class ImportWkpbBrondocumentTask(batch.BasicTask):
    name = "Import Wkpb Brondocument"

    def __init__(self, source_path):
        super().__init__()
        self.source = os.path.join(source_path, 'wpb_brondocument.dat')
        self.codes = set()
        self.beperkingen = dict()

    def before(self):
        database.clear_models(models.Brondocument)
        self.codes = set(models.Broncode.objects.values_list('pk', flat=True))
        self.beperkingen = dict(models.Beperking.objects.values_list('inschrijfnummer', 'pk'))

    def after(self):
        self.codes.clear()
        self.beperkingen.clear()

    def process(self):
        with open(self.source) as f:
            rows = csv.reader(f, delimiter=';')
            objects = (self.process_row(r) for r in rows)
            object_dict = dict((o.pk, o) for o in objects)  # make unique; input contains duplicate IDs

        models.Brondocument.objects.bulk_create(object_dict.values(), batch_size=database.BATCH_SIZE)

    def process_row(self, r):
        if r[4] == '0':
            pers_afsch = False
        else:
            pers_afsch = True

        bron_id = r[2] if r[2] in self.codes else None

        inschrijfnummer = int(r[0])
        beperking_id = self.beperkingen.get(inschrijfnummer)

        if not beperking_id:
            log.warning('Brondocument {} references non-existing beperking {}; ignoring'.format(inschrijfnummer,
                                                                                                inschrijfnummer))

        return models.Brondocument(
            pk=inschrijfnummer,
            inschrijfnummer=inschrijfnummer,
            bron_id=bron_id,
            documentnaam=r[3][:21],  # afknippen, omdat data corrupt is (zie brondocument: 5820)
            persoonsgegevens_afschermen=pers_afsch,
            soort_besluit=r[5],
            beperking_id=beperking_id
        )


class ImportWkpbBepKadTask(batch.BasicTask):
    name = "import Beperking-Percelen"

    def __init__(self, source_path):
        super().__init__()
        self.source = os.path.join(source_path, 'wpb_belemmering_perceel.dat')
        self.beperkingen = set()
        self.kot = dict()

    def before(self):
        database.clear_models(models.BeperkingKadastraalObject)
        self.beperkingen = set(models.Beperking.objects.values_list('pk', flat=True))
        self.kot = dict(brk.KadastraalObject.objects.values_list('aanduiding', 'pk'))

    def after(self):
        self.beperkingen.clear()
        self.kot.clear()

    def process(self):
        with open(self.source) as f:
            rows = csv.reader(f, delimiter=';')
            objects = [o for o in (self.process_row(r) for r in rows) if o]

        models.BeperkingKadastraalObject.objects.bulk_create(objects, batch_size=database.BATCH_SIZE)

    def process_row(self, r):
        aanduiding = kadaster.get_aanduiding(r[0], r[1], r[2], r[3], r[4])
        beperking_id = int(r[5])

        if beperking_id not in self.beperkingen:
            log.warning('WPB references non-existing beperking {}; skipping'.format(beperking_id))
            return None

        if not aanduiding or aanduiding not in self.kot:
            log.warning('Beperking {} references non-existing kadastraal object {}; skipping'
                        .format(beperking_id, aanduiding))
            return None

        uid = '{0}_{1}'.format(beperking_id, aanduiding)

        return models.BeperkingKadastraalObject(
            pk=uid,
            beperking_id=beperking_id,
            kadastraal_object_id=self.kot[aanduiding],
        )


class ImportBeperkingVerblijfsobjectTask(object):
    name = "Import WKPB - Beperking-VBO"

    def before(self):
        database.clear_models(models.BeperkingVerblijfsobject)

    def execute(self):
        with db.connection.cursor() as c:
            c.execute("""
                INSERT INTO wkpb_beperkingverblijfsobject (verblijfsobject_id, beperking_id)
                  SELECT DISTINCT
                    vbo.id,
                    kot2bep.beperking_id
                  FROM
                    bag_verblijfsobject vbo
                    LEFT JOIN brk_kadastraalobjectverblijfsobjectrelatie vbo2kot
                      ON vbo2kot.verblijfsobject_id = vbo.id
                    LEFT JOIN wkpb_beperkingkadastraalobject kot2bep
                      ON vbo2kot.kadastraal_object_id = kot2bep.kadastraal_object_id
                  WHERE
                    kot2bep.beperking_id IS NOT NULL;
            """)


class ImportWkpbJob(object):
    name = "Import WKPB"

    def __init__(self):
        diva = settings.DIVA_DIR
        if not os.path.exists(diva):
            raise ValueError("DIVA_DIR not found: {}".format(diva))

        self.beperkingen = os.path.join(diva, 'beperkingen')

    def tasks(self):
        return [
            ImportBeperkingcodeTask(self.beperkingen),
            ImportWkpbBroncodeTask(self.beperkingen),
            ImportBeperkingTask(self.beperkingen),
            ImportWkpbBrondocumentTask(self.beperkingen),
            ImportWkpbBepKadTask(self.beperkingen),
            ImportBeperkingVerblijfsobjectTask(),
        ]
