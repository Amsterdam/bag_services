import os

from django.contrib.gis.gdal import DataSource

from django.contrib.gis.geos import GEOSGeometry

from atlas import models
from atlas_jobs import batch


class ImportLkiGemeenteTask(batch.AbstractOrmTask):
    name = "import LKI Gemeente"

    def __init__(self, source_path):
        super().__init__()
        self.source = os.path.join(source_path, 'LKI_Gemeente.shp')

    def execute(self):
        ds = DataSource(self.source)
        lyr = ds[0]
        for feat in lyr:
            self.process_feature(feat)

    def process_feature(self, feat):
        values = dict(
            gemeentecode=feat.get('GEM_CODE'),
            gemeentenaam=feat.get('GEM_NAAM'),
            geometrie=GEOSGeometry(feat.geom.wkt)
        )
        diva_id = feat.get('DIVA_ID')

        self.merge(models.LkiGemeente, diva_id, values)


class ImportLkiKadastraleGemeenteTask(batch.AbstractOrmTask):
    name = "import LKI Kadastrale gemeente"

    def __init__(self, source_path):
        super().__init__()
        self.source = os.path.join(source_path, 'LKI_Kadastrale_gemeente.shp')

    def execute(self):
        ds = DataSource(self.source)
        lyr = ds[0]
        for feat in lyr:
            self.process_feature(feat)

    def process_feature(self, feat):
        wkt = feat.geom.wkt

        # zorgen dat het een multipolygon wordt. Superlelijk! :( TODO!!
        if not 'MULTIPOLYGON' in wkt:
            wkt = wkt.replace('POLYGON ', 'MULTIPOLYGON (')
            wkt += ')'
        values = dict(
            code=feat.get('KAD_GEM'),
            ingang_cyclus=feat.get('INGANG_CYC'),
            geometrie=GEOSGeometry(wkt)
        )
        diva_id = feat.get('DIVA_ID')

        self.merge(models.LkiKadastraleGemeente, diva_id, values)


class ImportLkiSectieTask(batch.AbstractOrmTask):
    name = "import LKI Sectie"

    def __init__(self, source_path):
        super().__init__()
        self.source = os.path.join(source_path, 'LKI_Sectie.shp')

    def execute(self):
        ds = DataSource(self.source)
        lyr = ds[0]
        for feat in lyr:
            self.process_feature(feat)

    def process_feature(self, feat):
        wkt = feat.geom.wkt

        # zorgen dat het een multipolygon wordt. Superlelijk! :( TODO!!
        if not 'MULTIPOLYGON' in wkt:
            wkt = wkt.replace('POLYGON ', 'MULTIPOLYGON (')
            wkt += ')'
        values = dict(
            kadastrale_gemeente_code=feat.get('KAD_GEM'),
            code=feat.get('SECTIE'),
            ingang_cyclus=feat.get('INGANG_CYC'),
            geometrie=GEOSGeometry(wkt)
        )
        diva_id = feat.get('DIVA_ID')

        self.merge(models.LkiSectie, diva_id, values)


class ImportLkiKadastraalObjectTask(batch.AbstractOrmTask):
    name = "import LKI Kadastraal Object"

    def __init__(self, source_path):
        super().__init__()
        self.source = os.path.join(source_path, 'LKI_Perceel.shp')

    def get_kadastrale_aanduiding(self, gem, sec, perc, app, index):
        return '{0}{1}{2:0>5}{3}{4:0>4}'.format(gem, sec, perc, app, index)

    def execute(self):
        ds = DataSource(self.source)
        lyr = ds[0]
        for feat in lyr:
            self.process_feature(feat)

    def process_feature(self, feat):

        # zorgen dat het een multipolygon wordt. Superlelijk! :( TODO!!
        wkt = feat.geom.wkt
        if not 'MULTIPOLYGON' in wkt:
            wkt = wkt.replace('POLYGON ', 'MULTIPOLYGON (')
            wkt += ')'

        values = dict(
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
        diva_id = feat.get('DIVA_ID')

        self.merge(models.LkiKadastraalObject, diva_id, values)
