from batch.test import TaskTestCase
from datasets.akr.models import KadastraalObject
from datasets.wkpb import batch, models
from datasets.wkpb.tests.test_batch import BEPERKINGEN
from datasets.brk.tests import factories as brk_factories


class ImportWkpbBepKad(TaskTestCase):

    def setUp(self):
        super().setUp()
        brk_factories.KadastraalObjectFactory.create(
            pk='NL.Blah.KadastraalObject.3423423',
            aanduiding='ASD12P03580A0061',
        )

    def requires(self):
        return [
            batch.ImportBeperkingcodeTask(BEPERKINGEN),
            batch.ImportBeperkingTask(BEPERKINGEN),
            batch.ImportWkpbBroncodeTask(BEPERKINGEN),
            batch.ImportWkpbBrondocumentTask(BEPERKINGEN),
        ]

    def task(self):
        return batch.ImportWkpbBepKadTask(BEPERKINGEN)

    def test_import(self):
        self.run_task()

        bk = models.BeperkingKadastraalObject.objects.get(pk='1001730_ASD12P03580A0061')
        self.assertEqual(bk.beperking.id, 1001730)
        self.assertIsNotNone(bk.kadastraal_object)
        self.assertEqual(bk.kadastraal_object.aanduiding, 'ASD12P03580A0061')
