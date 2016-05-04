from batch.test import TaskTestCase
from datasets.brk import batch, models
from datasets.brk.tests import factories
from datasets.bag.tests import factories as bag_factories


class ImportKadastraalObjectTaskTest(TaskTestCase):
    def setUp(self):
        [factories.KadastraalObjectFactory.create(pk=kot_id) for kot_id in [
            'NL.KAD.OnroerendeZaak.11730205570000',
            'NL.KAD.OnroerendeZaak.11430756410009',
        ]]
        [bag_factories.VerblijfsobjectFactory.create(pk=vbo_id) for vbo_id in [
            '03630000740386',
            '03630000984377',
        ]]

    def task(self):
        return batch.ImportKadastraalObjectVerblijfsobjectTask("diva/brk")

    def test_import(self):
        self.run_task()

        kot = models.KadastraalObject.objects.get(pk='NL.KAD.OnroerendeZaak.11730205570000')

        self.assertQuerysetEqual(kot.verblijfsobjecten.all(), transform=lambda vbo: vbo.id, values=['03630000740386'])
