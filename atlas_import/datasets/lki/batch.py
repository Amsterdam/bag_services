import os

from django.conf import settings
from django.contrib.gis.gdal import DataSource

from . import models
from datasets.generic import kadaster, mixins, database


class ImportGemeenteTask(mixins.GeoMultiPolygonMixin):
    name = "import Gemeente"

    def __init__(self, source_path):
        super().__init__()
        self.source = os.path.join(source_path, 'LKI_Gemeente.shp')

    def execute(self):
        models.Gemeente.objects.all().delete()

        ds = DataSource(self.source)
        lyr = ds[0]
        objects = [self.process_feature(feat) for feat in lyr]

        models.Gemeente.objects.bulk_create(objects, batch_size=database.BATCH_SIZE)

    def process_feature(self, feat):
        return models.Gemeente(
            pk=feat.get('DIVA_ID'),
            gemeentecode=feat.get('GEM_CODE'),
            gemeentenaam=feat.get('GEM_NAAM'),
            geometrie=self.get_multipoly(feat.geom.wkt)
        )


class ImportKadastraleGemeenteTask(mixins.GeoMultiPolygonMixin):
    name = "import Kadastrale gemeente"

    def __init__(self, source_path):
        super().__init__()
        self.source = os.path.join(source_path, 'LKI_Kadastrale_gemeente.shp')

    def execute(self):
        ds = DataSource(self.source)
        lyr = ds[0]
        objects = [self.process_feature(feat) for feat in lyr]

        models.KadastraleGemeente.objects.all().delete()
        models.KadastraleGemeente.objects.bulk_create(objects, batch_size=database.BATCH_SIZE)

    def process_feature(self, feat):
        return models.KadastraleGemeente(
            pk=(feat.get('DIVA_ID')),
            code=feat.get('KAD_GEM'),
            ingang_cyclus=feat.get('INGANG_CYC'),
            geometrie=self.get_multipoly(feat.geom.wkt)
        )


class ImportSectieTask(mixins.GeoMultiPolygonMixin):
    name = "import Sectie"

    def __init__(self, source_path):
        super().__init__()
        self.source = os.path.join(source_path, 'LKI_Sectie.shp')

    def execute(self):
        ds = DataSource(self.source)
        lyr = ds[0]
        objects = [self.process_feature(feat) for feat in lyr]

        models.Sectie.objects.all().delete()
        models.Sectie.objects.bulk_create(objects, batch_size=database.BATCH_SIZE)

    def process_feature(self, feat):
        return models.Sectie(
            pk=feat.get('DIVA_ID'),
            kadastrale_gemeente_code=feat.get('KAD_GEM'),
            code=feat.get('SECTIE'),
            ingang_cyclus=feat.get('INGANG_CYC'),
            geometrie=self.get_multipoly(feat.geom.wkt)
        )


class ImportKadastraalObjectTask(mixins.GeoMultiPolygonMixin):
    name = "import Kadastraal Object"

    def __init__(self, source_path):
        super().__init__()
        self.source = os.path.join(source_path, 'LKI_Perceel.shp')

    def execute(self):
        ds = DataSource(self.source)
        lyr = ds[0]
        objects = [self.process_feature(feat) for feat in lyr]

        models.KadastraalObject.objects.all().delete()
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
            geometrie=self.get_multipoly(feat.geom.wkt)
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
