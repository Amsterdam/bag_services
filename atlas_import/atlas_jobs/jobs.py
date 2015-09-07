import logging
import os

from django.conf import settings

from .batch import kadaster, wkpb, elastic

log = logging.getLogger(__name__)


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
