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

    def setUp(self):

        bag_factories.OpenbareRuimteFactory.create(
            naam="Anjeliersstraat")

        # weg
        bag_factories.OpenbareRuimteFactory.create(
            naam="Prinsengracht", type='01')

        # water
        bag_factories.OpenbareRuimteFactory.create(
            naam="Prinsengracht", type='02')

        # The actual tested usecases

        self.gsg = bag_factories.GrootstedelijkGebiedFactory.create()
        self.unesco = bag_factories.UnescoFactory.create()
        self.stadsdeel = bag_factories.StadsdeelFactory.create(
            id='testgebied')
        self.ggw = bag_factories.GebiedsgerichtwerkenFactory.create(
            stadsdeel=self.stadsdeel
        )
        self.bb = bag_factories.BouwblokFactory(code='YC01')
        self.bb2 = bag_factories.BouwblokFactory(code='YC00')

        batch.execute(datasets.bag.batch.DeleteIndexGebiedJob())
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

        return first

    def test_grootstedelijk_query(self):
        naam = self.gsg.naam
        gsg = self.find(naam)
        self.assertIn('gebieden/grootstedelijkgebied', gsg['_links']['self']['href'])

    def test_unseco(self):
        naam = self.unesco.naam
        unesco = self.find(naam)
        self.assertIn('gebieden/unesco', unesco['_links']['self']['href'])

    def test_ggw(self):
        naam = self.ggw.naam
        ggw = self.find(naam)
        self.assertIn('gebieden/gebiedsgerichtwerken', ggw['_links']['self']['href'])

    def test_bouwblok(self):
        code = self.bb.code
        response = self.client.get(
            '/atlas/search/gebied/', dict(q=code))
        self.assertEqual(response.status_code, 200)
        self.assertIn('results', response.data)
        self.assertIn('count', response.data)
        first = response.data['results'][0]
        self.assertEqual(first['code'], code)
        self.assertIn('gebieden/bouwblok', first['_links']['self']['href'])

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
        self.assertIn('gebieden/bouwblok', first['_links']['self']['href'])
        self.assertEqual(first['code'], b2_code)
