# Python
from unittest import skip
# Packages
from rest_framework.test import APITestCase
# Project
from batch import batch
import datasets.bag.batch
from datasets.bag.tests import factories as bag_factories
import datasets.brk.batch


class GebiedSearchTest(APITestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.gsg = bag_factories.GrootstedelijkGebiedFactory.create()
        cls.unesco = bag_factories.UnescoFactory.create()
        cls.ggw = bag_factories.GebiedsgerichtwerkenFactory.create()
        cls.bb = bag_factories.BouwblokFactory(code='YC01')

        batch.execute(datasets.bag.batch.IndexGebiedenJob())

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
