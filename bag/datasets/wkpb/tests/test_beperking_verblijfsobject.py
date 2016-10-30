from batch.test import TaskTestCase
from datasets.bag.tests import factories as bag_factories
from datasets.brk import models as brk
from datasets.brk.tests import factories as brk_factories
from datasets.wkpb import batch, models
from datasets.wkpb.tests import factories


class ImportBeperkingVerblijfsobjectTaskTest(TaskTestCase):
    def setUp(self):
        self.vbo1 = bag_factories.VerblijfsobjectFactory.create()
        self.vbo2 = bag_factories.VerblijfsobjectFactory.create()

        kot1 = brk_factories.KadastraalObjectFactory.create()
        kot2a = brk_factories.KadastraalObjectFactory.create()
        kot2b = brk_factories.KadastraalObjectFactory.create()

        brk.KadastraalObjectVerblijfsobjectRelatie.objects.create(
            verblijfsobject=self.vbo1,
            kadastraal_object=kot1,
        )
        brk.KadastraalObjectVerblijfsobjectRelatie.objects.create(
            verblijfsobject=self.vbo2,
            kadastraal_object=kot2a,
        )
        brk.KadastraalObjectVerblijfsobjectRelatie.objects.create(
            verblijfsobject=self.vbo2,
            kadastraal_object=kot2b,
        )

        self.bep1 = factories.BeperkingFactory.create()
        self.bep2a = factories.BeperkingFactory.create()
        self.bep2b1 = factories.BeperkingFactory.create()
        self.bep2b2 = factories.BeperkingFactory.create()

        models.BeperkingKadastraalObject.objects.create(id='a',
                                                        kadastraal_object=kot1,
                                                        beperking=self.bep1)
        models.BeperkingKadastraalObject.objects.create(id='b',
                                                        kadastraal_object=kot2a,
                                                        beperking=self.bep2a)
        models.BeperkingKadastraalObject.objects.create(id='c',
                                                        kadastraal_object=kot2b,
                                                        beperking=self.bep2b1)
        models.BeperkingKadastraalObject.objects.create(id='d',
                                                        kadastraal_object=kot2b,
                                                        beperking=self.bep2b2)

    def task(self):
        return batch.ImportBeperkingVerblijfsobjectTask()

    def test_import(self):
        self.run_task()

        self.vbo1.refresh_from_db()
        self.vbo2.refresh_from_db()

        vbo1_beperkingen = set([obj.id for obj in self.vbo1.beperkingen.all()])
        vbo2_beperkingen = set([obj.id for obj in self.vbo2.beperkingen.all()])

        self.assertEqual(vbo1_beperkingen, {self.bep1.id})
        self.assertEqual(vbo2_beperkingen,
                         {self.bep2a.id, self.bep2b1.id, self.bep2b2.id})
