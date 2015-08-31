import logging
import os

from django.conf import settings
from elasticsearch_dsl.connections import connections

from atlas import models, documents
from .batch import bag, kadaster, wkpb

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
            kadaster.ImportLkiGemeenteTask(self.kadaster_lki),
            kadaster.ImportLkiKadastraleGemeenteTask(self.kadaster_lki),
            kadaster.ImportLkiSectieTask(self.kadaster_lki),
            kadaster.ImportLkiKadastraalObjectTask(self.kadaster_lki),
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
            wkpb.ImportBeperkingcodeTask(self.beperkingen),
            wkpb.ImportWkpbBroncodeTask(self.beperkingen),
            wkpb.ImportWkpbBrondocumentTask(self.beperkingen),
            wkpb.ImportBeperkingTask(self.beperkingen),
            wkpb.ImportWkpbBepKadTask(self.beperkingen),
        ]


class IndexJob(object):
    name = "atlas-index"

    def tasks(self):
        return [
            ImportELLigplaatsTask(),
            ImportELStandplaatsTask(),
            ImportELVerblijfsobjectTask(),
        ]
