import logging
import os

from django.conf import settings

from .batch import wkpb

log = logging.getLogger(__name__)


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


