from batch.test import TaskTestCase
from datasets.brk import batch, models
from datasets.brk.tests import factories


class ImportKadastraleSectieTaskTest(TaskTestCase):
    def setUp(self):
        super().setUp()
        factories.KadastraleGemeenteFactory.create(pk="ASD15")

    def task(self):
        return batch.ImportKadastraleSectieTask("diva/brk_shp")

    def test_import(self):
        self.run_task()

        s = models.KadastraleSectie.objects.get(pk='ASD15S')
        self.assertIsNotNone(s)
        self.assertIsNotNone(s.kadastrale_gemeente)

        self.assertEqual(s.sectie, 'S')
        self.assertEqual(s.kadastrale_gemeente.pk, 'ASD15')
        self.assertIsNotNone(s.geometrie)
