from batch.test import TaskTestCase
from datasets.bag.tests import factories as bag_factories
from datasets.brk import batch, models
from datasets.brk.tests import factories


class ImportZakelijkRechtVerblijfsobjectTaskTest(TaskTestCase):
    def setUp(self):
        self.vbo1 = bag_factories.VerblijfsobjectFactory.create()
        self.vbo2 = bag_factories.VerblijfsobjectFactory.create()

        kot1 = factories.KadastraalObjectFactory.create()
        kot2a = factories.KadastraalObjectFactory.create()
        kot2b = factories.KadastraalObjectFactory.create()

        models.KadastraalObjectVerblijfsobjectRelatie.objects.create(
            verblijfsobject=self.vbo1,
            kadastraal_object=kot1,
        )
        models.KadastraalObjectVerblijfsobjectRelatie.objects.create(
            verblijfsobject=self.vbo2,
            kadastraal_object=kot2a,
        )
        models.KadastraalObjectVerblijfsobjectRelatie.objects.create(
            verblijfsobject=self.vbo2,
            kadastraal_object=kot2b,
        )

        self.zrt1 = factories.ZakelijkRechtFactory.create(
            kadastraal_object=kot1)
        self.zrt2a = factories.ZakelijkRechtFactory.create(
            kadastraal_object=kot2a)
        self.zrt2b1 = factories.ZakelijkRechtFactory.create(
            kadastraal_object=kot2b)
        self.zrt2b2 = factories.ZakelijkRechtFactory.create(
            kadastraal_object=kot2b)

    def task(self):
        return batch.ImportZakelijkRechtVerblijfsobjectTask()

    def test_import(self):
        self.run_task()

        self.vbo1.refresh_from_db()
        self.vbo2.refresh_from_db()

        vbo1_rechten = set([obj.id for obj in self.vbo1.rechten.all()])
        vbo2_rechten = set([obj.id for obj in self.vbo2.rechten.all()])

        self.assertEqual(vbo1_rechten, {self.zrt1.id})
        self.assertEqual(vbo2_rechten,
                         {self.zrt2a.id, self.zrt2b1.id, self.zrt2b2.id})
