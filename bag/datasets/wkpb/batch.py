import datetime
import logging
import os
from collections import defaultdict

from django import db
from django.conf import settings

import datasets.brk.models as brk
from batch import batch
from datasets.bag.batch import GOB_CSV_ENCODING
from datasets.generic import database, metadata, uva2
from . import models

log = logging.getLogger(__name__)


class ImportBeperkingcodeTask(batch.BasicTask):
    name = "Import Beperkingcode"

    def __init__(self, source_path):
        super().__init__()
        self.source = os.path.join(source_path, 'WKPB_type.csv')

    def before(self):
        pass

    def after(self):
        pass

    def process(self):
        objects = uva2.process_csv(None, None, self.process_row, source=self.source,
                                   encoding=GOB_CSV_ENCODING)
        models.Beperkingcode.objects.bulk_create(objects, batch_size=database.BATCH_SIZE)

    def process_row(self, r):
        return models.Beperkingcode(
            pk=r['typeCode'],
            omschrijving=r['typeOmschrijving'],
        )


class ImportWkpbBroncodeTask(batch.BasicTask):
    name = "Import Wkpb Broncode"

    def __init__(self, source_path):
        super().__init__()
        self.source = os.path.join(source_path, 'WKPB_orgaan.csv')

    def before(self):
        pass

    def after(self):
        log.info(
            '%d WKPB Broncodes Imported',
            models.Broncode.objects.count()
        )
        pass

    def process(self):
        objects = uva2.process_csv(None, None, self.process_row, source=self.source,
                                   encoding=GOB_CSV_ENCODING)

        models.Broncode.objects.all().delete()
        models.Broncode.objects.bulk_create(objects, batch_size=database.BATCH_SIZE)

    def process_row(self, r):

        return models.Broncode(
            pk=r['orgaanCode'],
            omschrijving=r['orgaanOmschrijving'],
        )


class ImportBeperkingTask(batch.BasicTask):
    name = "Import Beperking"

    def __init__(self, source_path):
        super().__init__()
        self.source = os.path.join(source_path, 'WKPB_beperking.csv')
        self.codes = set()

    def before(self):
        self.codes = set(models.Beperkingcode.objects.values_list('pk', flat=True))

    def after(self):
        self.codes.clear()

    def process(self):
        objects = uva2.process_csv(None, None, self.process_row, source=self.source,
                                   encoding=GOB_CSV_ENCODING)
        models.Beperking.objects.bulk_create(objects, batch_size=database.BATCH_SIZE)

    def process_row(self, r):
        code_id = r['typeCode'] if r['typeCode'] in self.codes else None
        datum_in_werking = uva2.iso_datum_tijd(r['beginGeldigheid'])
        datum_einde = uva2.iso_datum_tijd(r['eindGeldigheid'])
        vandaag = datetime.date.today()
        if datum_einde and datum_einde < vandaag:
            log.warning(f'Beperking {code_id} no longer valid; end date {datum_einde} was before {vandaag}')
            return None
        inschrijfnummer = r['identificatie']

        # In GOB no  special id for beperking is given. Only identificatie or inschrijfnummer.
        # But this is unique and can be used as int for primary key
        return models.Beperking(
            pk=inschrijfnummer,
            inschrijfnummer=inschrijfnummer,
            beperkingtype_id=code_id,
            datum_in_werking=datum_in_werking,
            datum_einde=datum_einde,
        )


class ImportWkpbBrondocumentTask(batch.BasicTask):
    name = "Import Wkpb Brondocument"

    def __init__(self, source_path):
        super().__init__()
        self.source = os.path.join(source_path, 'WKPB_brondocument.csv')
        self.codes = set()
        self.beperkingen = set()

    def before(self):
        self.codes = set(models.Broncode.objects.values_list('pk', flat=True))
        self.beperkingen = set(models.Beperking.objects.values_list('pk', flat=True))

    def after(self):
        self.codes.clear()
        self.beperkingen.clear()

    def process(self):
        objects = uva2.process_csv(None, None, self.process_row, source=self.source,
                                   encoding=GOB_CSV_ENCODING)
        object_dict = defaultdict(list)
        for o in objects:
            object_dict[o.pk].append(o)

        for key, value in object_dict.items():
            # Order on  reverse object name . We only need the last name
            object_dict[key].sort(key=lambda o: o.documentnaam, reverse=True)
            object_dict[key] = object_dict[key][0]

        models.Brondocument.objects.bulk_create(object_dict.values(), batch_size=database.BATCH_SIZE)

    def process_row(self, r):
        pers_afsch = {'N': False, 'J': True}.get(r['persoonsgegevensAfschermen'], None)

        bron_id = r['orgaanCode'] if r['orgaanCode'] in self.codes else None

        inschrijfnummer = int(r['identificatie'])
        if inschrijfnummer not in self.beperkingen:
            log.warning(f'Brondocument {inschrijfnummer} references non-existing beperking; ignoring')
            return None

        # soort_besluit = {
        #     'Opleggen': 'beperkingenbesluit',
        #     'Beëindigen': 'beeindigingsbesluit'
        # }.get(r['aard'], r['aard'])

        soort_besluit = r['aard']
        documentnaam = r['documentnummer']
        if len(documentnaam) > 21:
            log.error(f"Invalid documentnaam {documentnaam} at {inschrijfnummer}")
            # Try to fix this for now
            documentnaam = documentnaam.replace("..", ".").rstrip(".")

        return models.Brondocument(
            pk=inschrijfnummer,
            inschrijfnummer=inschrijfnummer,
            bron_id=bron_id,
            documentnaam=documentnaam,
            persoonsgegevens_afschermen=pers_afsch,
            soort_besluit=soort_besluit,
            beperking_id=inschrijfnummer
        )


class ImportWkpbBepKadTask(batch.BasicTask, metadata.UpdateDatasetMixin):
    name = "import Beperking-KadastraalObject"
    dataset_id = 'Wkpb'

    def __init__(self, source_path):
        super().__init__()
        self.source = os.path.join(source_path, 'WKPB_beperking_kadastraalobject.csv')
        self.beperkingen = set()
        self.kot = dict()

    def before(self):
        self.beperkingen = set(models.Beperking.objects.values_list('pk', flat=True))
        self.kot = dict(brk.KadastraalObject.objects.values_list('pk', 'aanduiding'))

    def after(self):
        self.beperkingen.clear()
        self.kot.clear()

        filedate = datetime.date.today() - datetime.timedelta(days=1)
        self.update_metadata_date(filedate)

        log.info(
            '%d Beperking-KadastraalObject Imported',
            models.BeperkingKadastraalObject.objects.count()
        )

    def process(self):
        objects = uva2.process_csv(None, None, self.process_row, source=self.source,
                                   encoding=GOB_CSV_ENCODING)
        models.BeperkingKadastraalObject.objects.bulk_create(objects, batch_size=database.BATCH_SIZE)

    def process_row(self, r):
        kot_id = r['belast:BRK.KOT.identificatie']
        inschrijfnummer = int(r['identificatie'])
        if not kot_id:
            log.warning(f'Beperking {inschrijfnummer} references no kadastraal object; skipping')
            return None

        aanduiding = self.kot.get(kot_id)
        if not aanduiding:
            log.warning(f'Beperking {inschrijfnummer} references non-existing kadastraal object {kot_id}; skipping')
            return None

        if inschrijfnummer not in self.beperkingen:
            log.warning(f'WPB Beperking-KadastraalObject references non-existing beperking for inschrijfnummer {inschrijfnummer}; skipping')
            return None

        uid = '{0}_{1}'.format(inschrijfnummer, aanduiding)

        return models.BeperkingKadastraalObject(
            pk=uid,
            beperking_id=inschrijfnummer,
            kadastraal_object_id=kot_id,
        )


class ImportBeperkingVerblijfsobjectTask(object):
    name = "Import WKPB - Beperking-VBO"

    def before(self):
        pass

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
        gob_dir = settings.GOB_DIR
        if not os.path.exists(gob_dir):
            raise ValueError("GOB_DIR not found: {}".format(gob_dir))

        self.beperkingen = os.path.join(gob_dir, 'wkpb/CSV_Actueel')

    def tasks(self):
        return [
            ImportBeperkingcodeTask(self.beperkingen),
            ImportWkpbBroncodeTask(self.beperkingen),
            ImportBeperkingTask(self.beperkingen),
            ImportWkpbBrondocumentTask(self.beperkingen),
            ImportWkpbBepKadTask(self.beperkingen),
            ImportBeperkingVerblijfsobjectTask(),
        ]
