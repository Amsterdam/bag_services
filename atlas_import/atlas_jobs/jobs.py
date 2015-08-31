import csv
import logging
import os
import datetime

from django.conf import settings
from django.contrib.gis.geos import GEOSGeometry
from django.contrib.gis.gdal import DataSource
from elasticsearch_dsl.connections import connections

from atlas import models, documents
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


# Wkpb

class ImportBeperkingcodeTask(object):
    name = "import Beperkingcode"

    def __init__(self, source_path):
        self.source = os.path.join(source_path, 'wpb_belemmeringcode.dat')

    def execute(self):
        with open(self.source) as f:
            rows = csv.reader(f, delimiter=';')
            for row in rows:
                self.process_row(row)

    def process_row(self, r):
        merge(models.Beperkingcode, r[0], dict(
            omschrijving=r[1],
        ))


class ImportWkpbBroncodeTask(object):
    name = "import Wkpb Broncode"

    def __init__(self, source_path):
        self.source = os.path.join(source_path, 'wpb_broncode.dat')

    def execute(self):
        with open(self.source) as f:
            rows = csv.reader(f, delimiter=';')
            for row in rows:
                self.process_row(row)

    def process_row(self, r):
        merge(models.WkpbBroncode, r[0], dict(
            omschrijving=r[1],
        ))


class ImportWkpbBrondocumentTask(object):
    name = "import Wkpb Brondocument"

    def __init__(self, source_path):
        self.source = os.path.join(source_path, 'wpb_brondocument.dat')
        self.cache = dict()

    def execute(self):
        try:
            with open(self.source) as f:
                rows = csv.reader(f, delimiter=';')
                for row in rows:
                    self.process_row(row)
        finally:
            self.cache.clear()

    def process_row(self, r):
        if r[4] == '0':
            pers_afsch = False
        else:
            pers_afsch = True

        merge(models.WkpbBrondocument, r[0], dict(
            documentnummer=r[0],
            bron_id=foreign_key_id(models.WkpbBroncode, r[2], self.cache),
            documentnaam=r[3][:21],  # afknippen, omdat data corrupt is (zie brondocument: 5820)
            persoonsgegeven_afschermen=pers_afsch,
            soort_besluit=r[5],
        ))


class ImportBeperkingTask(object):
    name = "import Beperking"

    def __init__(self, source_path):
        self.source = os.path.join(source_path, 'wpb_belemmering.dat')
        self.cache = dict()

    def execute(self):
        try:
            with open(self.source) as f:
                rows = csv.reader(f, delimiter=';')
                for row in rows:
                    self.process_row(row)
        finally:
            self.cache.clear()

    def get_date(self, s):
        if s:
            return datetime.datetime.strptime(s, "%Y%m%d").date()
        else:
            return None

    def process_row(self, r):

        merge(models.Beperking, r[0], dict(
            inschrijfnummer=r[1],
            beperkingtype_id=foreign_key_id(models.Beperkingcode, r[2], self.cache),
            datum_in_werking=self.get_date(r[3]),
            datum_einde=self.get_date(r[4]),
        ))


class ImportWkpbBepKadTask(object):
    name = "import Beperking-Percelen"

    def __init__(self, source_path):
        self.source = os.path.join(source_path, 'wpb_belemmering_perceel.dat')
        self.cache = dict()

    def execute(self):
        try:
            with open(self.source) as f:
                rows = csv.reader(f, delimiter=';')
                for row in rows:
                    self.process_row(row)
        finally:
            self.cache.clear()

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

        merge(models.BeperkingKadastraalObject, uid, dict(
            beperking=bp,
            kadastraal_object=ko
        ))


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
