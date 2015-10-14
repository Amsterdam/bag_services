import csv
import logging
import os
import datetime

from django.conf import settings
from django.db.models import Q
from datasets.generic import kadaster

import datasets.lki.models as lki
import datasets.akr.models as akr
from . import models

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

        models.Broncode.objects.all().delete()
        models.Broncode.objects.bulk_create(objects)

    def process_row(self, r):
        return models.Broncode(
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
            self.cache = set(models.Broncode.objects.values_list('pk', flat=True))

            with open(self.source) as f:
                rows = csv.reader(f, delimiter=';')
                objects = (self.process_row(r) for r in rows)
                object_dict = dict((o.pk, o) for o in objects)  # make unique; input contains duplicate IDs

            models.Brondocument.objects.all().delete()
            models.Brondocument.objects.bulk_create(object_dict.values())

        finally:
            self.cache.clear()

    def process_row(self, r):
        if r[4] == '0':
            pers_afsch = False
        else:
            pers_afsch = True

        bron_id = r[2] if r[2] in self.cache else None
        return models.Brondocument(
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
            self.lki_cache = dict(lki.KadastraalObject.objects.values_list('aanduiding', 'pk'))

            with open(self.source) as f:
                rows = csv.reader(f, delimiter=';')
                objects = [o for o in (self.process_row(r) for r in rows) if o]

            models.BeperkingKadastraalObject.objects.all().delete()
            models.BeperkingKadastraalObject.objects.bulk_create(objects)

        finally:
            self.beperkingen_cache.clear()
            self.lki_cache.clear()

    def process_row(self, r):
        aanduiding = kadaster.get_aanduiding(r[0], r[1], r[2], r[3], r[4])
        beperking_id = int(r[5])

        if beperking_id not in self.beperkingen_cache:
            log.warning('Non-existing Beperking: {0}'.format(beperking_id))
            return None

        kadastraal_objecten = lki.KadastraalObject.objects.filter(aanduiding=aanduiding)
        if not len(kadastraal_objecten):
            if settings.IMPORT_USE_FAKE_DATA:
                kadastraal_object_lki = lki.KadastraalObject.objects.filter(~Q(aanduiding=aanduiding))[0]
                kadastraal_object_lki.aanduiding = aanduiding
                kadastraal_object_lki.save()
            else:
                log.warning('kadastraal object not found in lki: %s' % aanduiding)
                return
        else:
            if len(kadastraal_objecten) > 1:
                log.warning('more than one lki kadastraal object found (%s)' % len(kadastraal_objecten))
            kadastraal_object_lki = kadastraal_objecten[0]

        try:
            kadastraal_object_akr = akr.KadastraalObject.objects.get(id=aanduiding)
        except akr.KadastraalObject.DoesNotExist:
            if settings.IMPORT_USE_FAKE_DATA:
                kadastraal_object_akr = akr.KadastraalObject.objects.filter(~Q(id=aanduiding))[0]
                kadastraal_object_akr.id = aanduiding
                kadastraal_object_akr.save()
            else:
                log.warning('kadastraal object not found in akr: %s' % aanduiding)
                return

        uid = '{0}_{1}'.format(beperking_id, aanduiding)

        return models.BeperkingKadastraalObject(
            pk=uid,
            beperking_id=beperking_id,
            kadastraal_object=kadastraal_object_lki,
            kadastraal_object_akr=kadastraal_object_akr
        )


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
            ImportWkpbBrondocumentTask(self.beperkingen),
            ImportBeperkingTask(self.beperkingen),
            ImportWkpbBepKadTask(self.beperkingen),
        ]
