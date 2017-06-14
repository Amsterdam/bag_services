# Python
from unittest import skip
# Packages
from rest_framework.test import APITransactionTestCase
# Project
from batch import batch
import datasets.bag.batch
from datasets.bag.tests import factories as bag_factories
import datasets.brk.batch


class GebiedSearchTest(APITransactionTestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        # We need Openbare ruimte objecten
        # becuause opr queries are executed
        # when searching on gebieden if name.raw
        # mapping is missing elastic crashes.
        bag_factories.OpenbareRuimteFactory.create(
            naam="Anjeliersstraat")

        bag_factories.OpenbareRuimteFactory.create(
            naam="Prinsengracht", type='01')

        bag_factories.OpenbareRuimteFactory.create(
            naam="Prinsengracht", type='02')

        batch.execute(datasets.bag.batch.IndexBagJob())

        batch.execute(datasets.brk.batch.IndexKadasterJob())

        # the actual tested usecases

        cls.gsg = bag_factories.GrootstedelijkGebiedFactory.create()
        cls.unesco = bag_factories.UnescoFactory.create()
        cls.stadsdeel = bag_factories.StadsdeelFactory.create(
            id='testgebied')
        cls.ggw = bag_factories.GebiedsgerichtwerkenFactory.create(
            stadsdeel=cls.stadsdeel
        )
        cls.bb = bag_factories.BouwblokFactory(code='YC01')
        cls.bb2 = bag_factories.BouwblokFactory(code='YC00')

        batch.execute(datasets.bag.batch.IndexGebiedenJob())

    @classmethod
    def tearDownClass(cls):
        cls.ggw.delete()
        cls.stadsdeel.delete()
        cls.bb.delete()
        cls.bb2.delete()
        cls.gsg.delete()
        cls.unesco.delete()

    def find(self, naam, tussenhaakjes=None):

        response = self.client.get(
            '/atlas/search/gebied/', dict(q=naam))
        self.assertEqual(response.status_code, 200)
        self.assertIn('results', response.data)
        self.assertIn('count', response.data)
        self.assertEqual(response.data['count'], 1)
        first = response.data['results'][0]

        self.assertEqual(first['naam'], naam)

    def test_grootstedelijk_query(self):
        naam = self.gsg.naam
        self.find(naam)

    def test_unseco(self):
        naam = self.unesco.naam
        self.find(naam)

    def test_ggw(self):
        naam = self.ggw.naam
        self.find(naam)

    def test_bouwblok(self):
        code = self.bb.code
        response = self.client.get(
            '/atlas/search/gebied/', dict(q=code))
        self.assertEqual(response.status_code, 200)
        self.assertIn('results', response.data)
        self.assertIn('count', response.data)
        first = response.data['results'][0]

        self.assertEqual(first['code'], code)

    def test_bouwblok_order(self):
        code = self.bb.code[0:3]  # 'YC0'
        # should find             # 'YC00'
        b2_code = self.bb2.code

        response = self.client.get(
            '/atlas/search/gebied/', dict(q=code))
        self.assertEqual(response.status_code, 200)
        self.assertIn('results', response.data)
        self.assertIn('count', response.data)
        first = response.data['results'][0]

        self.assertEqual(first['code'], b2_code)
