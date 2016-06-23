from batch.test import TaskTestCase
from datasets.brk import batch, models
from datasets.brk.tests import factories


class ImportKadastraleGemeenteTaskTest(TaskTestCase):

    def setUp(self):
        super().setUp()
        factories.GemeenteFactory.create(gemeente="Amsterdam")

    def task(self):
        return batch.ImportKadastraleGemeenteTask("diva/brk_shp")

    def test_import(self):
        self.run_task()

        kg = models.KadastraleGemeente.objects.get(pk='ASD09')
        self.assertIsNotNone(kg)
        self.assertIsNotNone(kg.gemeente)
        self.assertEqual(kg.gemeente.gemeente, 'Amsterdam')
        self.assertIsNotNone(kg.geometrie)

