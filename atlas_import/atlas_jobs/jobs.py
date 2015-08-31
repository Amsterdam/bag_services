import logging
import os

from django.conf import settings
from django.contrib.gis.geos import GEOSGeometry
from django.contrib.gis.gdal import DataSource
from elasticsearch_dsl.connections import connections

from atlas import models, documents
from atlas_jobs.batch.wkpb import ImportBeperkingcodeTask, ImportWkpbBroncodeTask, ImportWkpbBrondocumentTask, \
    ImportBeperkingTask, ImportWkpbBepKadTask
from .batch import bag

log = logging.getLogger(__name__)


def merge(model, pk, values):
    model.objects.update_or_create(pk=pk, defaults=values)


def merge_existing(model, pk, values):
    model.objects.filter(pk=pk).update(**values)


def foreign_key_id(model, model_id, cache):
    """
    Returns `model_id` if `model_id` identifies a valid instance of `model`; returns None otherwise.
    """
    if not model_id:
        return None

    key = str(model)
    id_set = cache.get(key, None)

    if id_set is None:
        id_set = set(model.objects.values_list('pk', flat=True))
        cache[key] = id_set

    if model_id not in id_set:
        log.warning("Reference to non-existing object of type %s with key %s", model, model_id)
        return None

    return model_id


# Kadaster - LKI

class ImportLkiGemeenteTask(object):
    name = "import LKI Gemeente"

    def __init__(self, source_path):
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

        merge(models.LkiGemeente, diva_id, values)


class ImportLkiKadastraleGemeenteTask(object):
    name = "import LKI Kadastrale gemeente"

    def __init__(self, source_path):
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

        merge(models.LkiKadastraleGemeente, diva_id, values)


class ImportLkiSectieTask(object):
    name = "import LKI Sectie"

    def __init__(self, source_path):
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

        merge(models.LkiSectie, diva_id, values)


class ImportLkiKadastraalObjectTask(object):
    name = "import LKI Kadastraal Object"

    def __init__(self, source_path):
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

        merge(models.LkiKadastraalObject, diva_id, values)


# Elasticsearch

class ImportELLigplaatsTask(object):
    name = "EL: import ligplaatsen"

    def __init__(self):
        connections.create_connection(hosts=settings.ELASTIC_SEARCH_HOSTS)
        documents.Ligplaats.init()

    def execute(self):
        for l in models.Ligplaats.objects.all():
            doc = documents.from_ligplaats(l)
            doc.save()


class ImportELStandplaatsTask(object):
    name = "EL: import standplaatsen"

    def __init__(self):
        connections.create_connection(hosts=settings.ELASTIC_SEARCH_HOSTS)
        documents.Standplaats.init()

    def execute(self):
        for s in models.Standplaats.objects.all():
            doc = documents.from_standplaats(s)
            doc.save()


class ImportELVerblijfsobjectTask(object):
    name = "EL: import verblijfsobjecten"

    def __init__(self):
        connections.create_connection(hosts=settings.ELASTIC_SEARCH_HOSTS)
        documents.Verblijfsobject.init()

    def execute(self):
        for v in models.Verblijfsobject.objects.all():
            doc = documents.from_verblijfsobject(v)
            doc.save()


class ImportBagJob(object):
    name = "atlas-import BAG"

    def __init__(self):
        diva = settings.DIVA_DIR
        if not os.path.exists(diva):
            raise ValueError("DIVA_DIR not found: {}".format(diva))

        self.bag = os.path.join(diva, 'bag')
        self.bag_wkt = os.path.join(diva, 'bag_wkt')
        self.gebieden = os.path.join(diva, 'gebieden')

    def tasks(self):
        return [
            bag.ImportAvrTask(self.bag),
            bag.ImportBrnTask(self.bag),
            bag.ImportEgmTask(self.bag),
            bag.ImportFngTask(self.bag),
            bag.ImportGbkTask(self.bag),
            bag.ImportLggTask(self.bag),
            bag.ImportLocTask(self.bag),
            bag.ImportTggTask(self.bag),
            bag.ImportStsTask(self.bag),

            bag.ImportGmeTask(self.gebieden),
            bag.ImportWplTask(self.bag),
            bag.ImportSdlTask(self.gebieden),
            bag.ImportBrtTask(self.gebieden),
            bag.ImportOprTask(self.bag),
            bag.ImportNumTask(self.bag),

            bag.ImportLigTask(self.bag),
            bag.ImportLigGeoTask(self.bag_wkt),
            bag.ImportNumLigHfdTask(self.bag),

            bag.ImportStaTask(self.bag),
            bag.ImportStaGeoTask(self.bag_wkt),
            bag.ImportNumStaHfdTask(self.bag),

            bag.ImportVboTask(self.bag),
            bag.ImportNumVboHfdTask(self.bag),

            bag.ImportPndTask(self.bag),
            bag.ImportPndGeoTask(self.bag_wkt),
            bag.ImportPndVboTask(self.bag),
        ]


class ImportKadasterJob(object):
    name = "atlas-import Kadaster"

    def __init__(self):
        diva = settings.DIVA_DIR
        if not os.path.exists(diva):
            raise ValueError("DIVA_DIR not found: {}".format(diva))

        self.kadaster_lki = os.path.join(diva, 'kadaster', 'lki')

    def tasks(self):
        return [
            ImportLkiGemeenteTask(self.kadaster_lki),
            ImportLkiKadastraleGemeenteTask(self.kadaster_lki),
            ImportLkiSectieTask(self.kadaster_lki),
            ImportLkiKadastraalObjectTask(self.kadaster_lki),
        ]


class ImportWkpbJob(object):
    name = "atlas-import WKPB"

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


class IndexJob(object):
    name = "atlas-index"

    def tasks(self):
        return [
            ImportELLigplaatsTask(),
            ImportELStandplaatsTask(),
            ImportELVerblijfsobjectTask(),
        ]
