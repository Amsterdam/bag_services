import os

from django.conf import settings

from . import models
from batch import batch
from datasets.generic import kadaster, database, geo


class ImportGemeenteTask(batch.BasicTask):
    name = "Import Gemeente"

    def __init__(self, source_path):
        self.path = source_path

    def before(self):
        database.clear_models(models.Gemeente)

    def after(self):
        pass

    def process(self):
        gemeentes = geo.process_shp(self.path, 'LKI_Gemeente.shp', self.process_feature)
        models.Gemeente.objects.bulk_create(gemeentes, batch_size=database.BATCH_SIZE)

    def process_feature(self, feat):
        return models.Gemeente(
            pk=feat.get('DIVA_ID'),
            gemeentecode=feat.get('GEM_CODE'),
            gemeentenaam=feat.get('GEM_NAAM'),
            geometrie=geo.get_multipoly(feat.geom.wkt)
        )


class ImportKadastraleGemeenteTask(batch.BasicTask):
    name = "Import Kadastrale gemeente"

    def __init__(self, source_path):
        self.path = source_path

    def before(self):
        database.clear_models(models.KadastraleGemeente)

    def after(self):
        pass

    def process(self):
        objects = geo.process_shp(self.path, 'LKI_Kadastrale_gemeente.shp', self.process_feature)
        models.KadastraleGemeente.objects.bulk_create(objects, batch_size=database.BATCH_SIZE)

    def process_feature(self, feat):
        return models.KadastraleGemeente(
            pk=(feat.get('DIVA_ID')),
            code=feat.get('KAD_GEM'),
            ingang_cyclus=feat.get('INGANG_CYC'),
            geometrie=geo.get_multipoly(feat.geom.wkt)
        )


class ImportSectieTask(batch.BasicTask):
    name = "Import Sectie"

    def __init__(self, source_path):
        self.path = source_path

    def before(self):
        database.clear_models(models.Sectie)

    def after(self):
        pass

    def process(self):
        objects = geo.process_shp(self.path, 'LKI_Sectie.shp', self.process_feature)
        models.Sectie.objects.bulk_create(objects, batch_size=database.BATCH_SIZE)

    def process_feature(self, feat):
        return models.Sectie(
            pk=feat.get('DIVA_ID'),
            kadastrale_gemeente_code=feat.get('KAD_GEM'),
            code=feat.get('SECTIE'),
            ingang_cyclus=feat.get('INGANG_CYC'),
            geometrie=geo.get_multipoly(feat.geom.wkt)
        )


class ImportKadastraalObjectTask(batch.BasicTask):
    name = "Import Kadastraal Object"

    def __init__(self, source_path):
        self.path = source_path

    def before(self):
        database.clear_models(models.KadastraalObject)

    def after(self):
        pass

    def process(self):
        objects = geo.process_shp(self.path, 'LKI_Perceel.shp', self.process_feature)
        models.KadastraalObject.objects.bulk_create(objects, batch_size=database.BATCH_SIZE)

    def process_feature(self, feat):
        return models.KadastraalObject(
            pk=feat.get('DIVA_ID'),
            kadastrale_gemeente_code=feat.get('KAD_GEM'),
            sectie_code=feat.get('SECTIE'),
            perceelnummer=feat.get('PERCEELNR'),
            indexletter=feat.get('IDX_LETTER'),
            indexnummer=feat.get('IDX_NUMMER'),
            oppervlakte=feat.get('OPP_VLAKTE'),
            ingang_cyclus=feat.get('INGANG_CYC'),
            aanduiding=kadaster.get_aanduiding(feat.get('KAD_GEM'), feat.get('SECTIE'), feat.get('PERCEELNR'),
                                               feat.get('IDX_LETTER'), feat.get('IDX_NUMMER')),
            geometrie=geo.get_multipoly(feat.geom.wkt)
        )


class ImportKadasterJob(object):
    name = "Import Kadaster - LKI"

    def __init__(self):
        diva = settings.DIVA_DIR
        if not os.path.exists(diva):
            raise ValueError("DIVA_DIR not found: {}".format(diva))

        self.kadaster_lki = os.path.join(diva, 'kadaster', 'lki')

    def tasks(self):
        return [
            ImportGemeenteTask(self.kadaster_lki),
            ImportKadastraleGemeenteTask(self.kadaster_lki),
            ImportSectieTask(self.kadaster_lki),
            ImportKadastraalObjectTask(self.kadaster_lki),
        ]
