from batch.test import TaskTestCase
from datasets.brk import batch, models


class ImportGemeenteTaskTest(TaskTestCase):
    def task(self):
        return batch.ImportGemeenteTask("diva/brk_shp")

    def test_import(self):
        self.run_task()

        gemeente = models.Gemeente.objects.get(pk='Amsterdam')
        self.assertIsNotNone(gemeente)
        self.assertEqual(gemeente.gemeente, 'Amsterdam')
        self.assertIsNotNone(gemeente.geometrie)
