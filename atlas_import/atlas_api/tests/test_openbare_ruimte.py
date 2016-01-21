import time
from unittest import skip

from rest_framework.test import APITestCase

import datasets.bag.batch
from datasets.bag.tests import factories as bag_factories
from datasets.brk.tests import factories as brk_factories


import datasets.brk.batch
from batch import batch


class SubjectSearchTest(APITestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        bag_factories.OpenbareRuimteFactory.create(
            naam="Anjeliersstraat")

        bag_factories.OpenbareRuimteFactory.create(
            naam="Prinsengracht", type='01')

        bag_factories.OpenbareRuimteFactory.create(
            naam="Prinsengracht", type='02')

        batch.execute(datasets.bag.batch.IndexBagJob())

        batch.execute(datasets.brk.batch.IndexKadasterJob())

        time.sleep(1)   # this is stupid

    def test_matching_query(self):
        response = self.client.get(
            '/api/atlas/search/openbareruimte/', dict(q="anjel"))
        self.assertEqual(response.status_code, 200)
        self.assertIn('results', response.data)
        self.assertIn('count', response.data)
        self.assertEqual(response.data['count'], 1)

        first = response.data['results'][0]

        self.assertEqual(first['naam'], "Anjeliersstraat")
        self.assertEqual(first['type'], "Openbare ruimte")

    def test_query_openbare_ruimte_gracht(self):
        response = self.client.get(
            "/api/atlas/search/openbareruimte/", dict(q="prinsengracht"))
        self.assertEqual(response.status_code, 200)
        self.assertIn('results', response.data)
        self.assertIn('count', response.data)
        self.assertEqual(response.data['count'], 2)

        self.assertEqual(
            response.data['results'][0]['naam'], "Prinsengracht")

        results = [
            response.data['results'][0]['subtype'],
            response.data['results'][1]['subtype']
        ]

        self.assertIn("Weg", results)
        self.assertIn("Water", results)
