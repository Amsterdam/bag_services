import logging
import os

from django.conf import settings

from .batch import bag, kadaster, wkpb, elastic

log = logging.getLogger(__name__)


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

            bag.ImportLigTask(self.bag),
            bag.ImportLigGeoTask(self.bag_wkt),

            bag.ImportStaTask(self.bag),
            bag.ImportStaGeoTask(self.bag_wkt),

            bag.ImportVboTask(self.bag),

            bag.ImportNumTask(self.bag),
            bag.ImportNumLigHfdTask(self.bag),
            bag.ImportNumStaHfdTask(self.bag),
            bag.ImportNumVboHfdTask(self.bag),
            bag.ImportNumVboNvnTask(self.bag),

            bag.ImportPndTask(self.bag),
            bag.ImportPndGeoTask(self.bag_wkt),
            bag.ImportPndVboTask(self.bag),

            bag.FlushCacheTask(),
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
            elastic.ImportELLigplaatsTask(),
            elastic.ImportELStandplaatsTask(),
            elastic.ImportELVerblijfsobjectTask(),
        ]
