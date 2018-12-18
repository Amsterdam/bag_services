from batch.test import TaskTestCase
from datasets.brk import batch, models
from datasets.brk.tests import factories


class ImportKadastraleSectieTaskTest(TaskTestCase):

    def setUp(self):
        super().setUp()
        factories.KadastraleGemeenteFactory.create(pk="ASD15")
        self.stash = {}

    def task(self):
        return [
            batch.ImportKadastraleSectieTaskLines("diva/brk_shp", self.stash),
            batch.ImportKadastraleSectieTask("diva/brk_shp", self.stash)
        ]

    def test_import(self):
        self.run_task()

        s = models.KadastraleSectie.objects.get(pk='ASD15S')
        self.assertIsNotNone(s)
        self.assertIsNotNone(s.kadastrale_gemeente)

        self.assertEqual(s.sectie, 'S')
        self.assertEqual(s.kadastrale_gemeente.pk, 'ASD15')
        self.assertIsNotNone(s.geometrie)
        self.assertIsNotNone(s.geometrie_lines)

