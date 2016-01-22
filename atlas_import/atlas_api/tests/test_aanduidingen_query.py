
# from unittest import skip

from rest_framework.test import APITestCase

import datasets.bag.batch
from datasets.bag.tests import factories as bag_factories

# from datasets.brk.tests import factories as brk_factories


import datasets.brk.batch
from batch import batch


class SubjectSearchTest(APITestCase):

    @classmethod
    def setUpClass(cls):

        super().setUpClass()

        straat = bag_factories.OpenbareRuimteFactory.create(
            naam="Anjeliersstraat", type='01')

        gracht = bag_factories.OpenbareRuimteFactory.create(
            naam="Prinsengracht", type='01')

        bag_factories.NummeraanduidingFactory.create(
            huisnummer=192,
            huisletter='A',
            type='01',  # Verblijfsobject
            openbare_ruimte=gracht
        )

        bag_factories.NummeraanduidingFactory.create(
            huisnummer=42,
            huisletter='F',
            type='01',  # Verblijfsobject
            openbare_ruimte=straat
        )

        batch.execute(datasets.bag.batch.IndexBagJob())
        batch.execute(datasets.brk.batch.IndexKadasterJob())

    def test_straat_query(self):
        response = self.client.get(
            '/api/atlas/search/adres/', dict(q="anjel"))
        self.assertEqual(response.status_code, 200)
        self.assertIn('results', response.data)
        self.assertIn('count', response.data)
        self.assertEqual(response.data['count'], 1)

        first = response.data['results'][0]
        self.assertEqual(first['straatnaam'], "Anjeliersstraat")

    def test_gracht_query(self):
        response = self.client.get(
            "/api/atlas/search/adres/", dict(q="prinsengracht 192"))
        self.assertEqual(response.status_code, 200)
        self.assertIn('results', response.data)
        self.assertIn('count', response.data)
        self.assertEqual(response.data['count'], 1)

        self.assertEqual(
            response.data['results'][0]['adres'], "Prinsengracht 192A")
