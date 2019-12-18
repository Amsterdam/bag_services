from batch.test import TaskTestCase
from datasets.brk import batch, models
from datasets.brk.tests import factories


class ImportKadastraleGemeenteTaskTest(TaskTestCase):

    def setUp(self):
        super().setUp()
        factories.GemeenteFactory.create(gemeente="Amsterdam")
        self.stash = {}

    def task(self):
        return [
            batch.ImportKadastraleGemeenteTaskLines("gob/brk_shp", self.stash),
            batch.ImportKadastraleGemeenteTask("gob/brk_shp", self.stash)
        ]

    def test_import(self):
        self.run_task()

        kg = models.KadastraleGemeente.objects.get(pk='ASD09')
        self.assertIsNotNone(kg)
        self.assertIsNotNone(kg.gemeente)
        self.assertEqual(kg.gemeente.gemeente, 'Amsterdam')
        self.assertIsNotNone(kg.geometrie)
        self.assertIsNotNone(kg.geometrie_lines)

