import os

from django.contrib.gis.gdal import DataSource
from django.contrib.gis.geos import GEOSGeometry

from atlas import models


class ImportLkiGemeenteTask(object):
    name = "import LKI Gemeente"

    def __init__(self, source_path):
        super().__init__()
        self.source = os.path.join(source_path, 'LKI_Gemeente.shp')

    def execute(self):
        models.LkiGemeente.objects.all().delete()

        ds = DataSource(self.source)
        lyr = ds[0]
        objects = [self.process_feature(feat) for feat in lyr]

        models.LkiGemeente.objects.bulk_create(objects)

    def process_feature(self, feat):
        return models.LkiGemeente(
            pk=feat.get('DIVA_ID'),
            gemeentecode=feat.get('GEM_CODE'),
            gemeentenaam=feat.get('GEM_NAAM'),
            geometrie=GEOSGeometry(feat.geom.wkt)
        )


class ImportLkiKadastraleGemeenteTask(object):
    name = "import LKI Kadastrale gemeente"

    def __init__(self, source_path):
        super().__init__()
        self.source = os.path.join(source_path, 'LKI_Kadastrale_gemeente.shp')

    def execute(self):
        ds = DataSource(self.source)
        lyr = ds[0]
        objects = [self.process_feature(feat) for feat in lyr]

        models.LkiKadastraleGemeente.objects.all().delete()
        models.LkiKadastraleGemeente.objects.bulk_create(objects)

    def process_feature(self, feat):
        wkt = feat.geom.wkt

        # zorgen dat het een multipolygon wordt. Superlelijk! :( TODO!!
        if 'MULTIPOLYGON' not in wkt:
            wkt = wkt.replace('POLYGON ', 'MULTIPOLYGON (')
            wkt += ')'

        return models.LkiKadastraleGemeente(
            pk=(feat.get('DIVA_ID')),
            code=feat.get('KAD_GEM'),
            ingang_cyclus=feat.get('INGANG_CYC'),
            geometrie=GEOSGeometry(wkt)
        )


class ImportLkiSectieTask(object):
    name = "import LKI Sectie"

    def __init__(self, source_path):
        super().__init__()
        self.source = os.path.join(source_path, 'LKI_Sectie.shp')

    def execute(self):
        ds = DataSource(self.source)
        lyr = ds[0]
        objects = [self.process_feature(feat) for feat in lyr]

        models.LkiSectie.objects.all().delete()
        models.LkiSectie.objects.bulk_create(objects)

    def process_feature(self, feat):
        wkt = feat.geom.wkt

        # zorgen dat het een multipolygon wordt. Superlelijk! :( TODO!!
        if 'MULTIPOLYGON' not in wkt:
            wkt = wkt.replace('POLYGON ', 'MULTIPOLYGON (')
            wkt += ')'

        return models.LkiSectie(
            pk=feat.get('DIVA_ID'),
            kadastrale_gemeente_code=feat.get('KAD_GEM'),
            code=feat.get('SECTIE'),
            ingang_cyclus=feat.get('INGANG_CYC'),
            geometrie=GEOSGeometry(wkt)
        )


class ImportLkiKadastraalObjectTask(object):
    name = "import LKI Kadastraal Object"

    def __init__(self, source_path):
        super().__init__()
        self.source = os.path.join(source_path, 'LKI_Perceel.shp')

    def get_kadastrale_aanduiding(self, gem, sec, perc, app, index):
        return '{0}{1}{2:0>5}{3}{4:0>4}'.format(gem, sec, perc, app, index)

    def execute(self):
        ds = DataSource(self.source)
        lyr = ds[0]
        objects = [self.process_feature(feat) for feat in lyr]

        models.LkiKadastraalObject.objects.all().delete()
        models.LkiKadastraalObject.objects.bulk_create(objects)

    def process_feature(self, feat):

        # zorgen dat het een multipolygon wordt. Superlelijk! :( TODO!!
        wkt = feat.geom.wkt
        if 'MULTIPOLYGON' not in wkt:
            wkt = wkt.replace('POLYGON ', 'MULTIPOLYGON (')
            wkt += ')'

        return models.LkiKadastraalObject(
            pk=feat.get('DIVA_ID'),
            kadastrale_gemeente_code=feat.get('KAD_GEM'),
            sectie_code=feat.get('SECTIE'),
            perceelnummer=feat.get('PERCEELNR'),
            indexletter=feat.get('IDX_LETTER'),
            indexnummer=feat.get('IDX_NUMMER'),
            oppervlakte=feat.get('OPP_VLAKTE'),
            ingang_cyclus=feat.get('INGANG_CYC'),
            aanduiding=self.get_kadastrale_aanduiding(feat.get('KAD_GEM'), feat.get('SECTIE'), feat.get('PERCEELNR'),
                                                      feat.get('IDX_LETTER'), feat.get('IDX_NUMMER')),
            geometrie=GEOSGeometry(wkt)
        )
