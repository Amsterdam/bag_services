from rest_framework.test import APITestCase
import time
import datasets.bag.batch
from batch import batch


class QueryTest(APITestCase):

    fixtures = ['dataset.json']

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        batch.execute(datasets.bag.batch.IndexJob())
        time.sleep(1)   # this is stupid

    def test_non_matching_query(self):
        response = self.client.get('/api/atlas/search/', dict(q="qqq"))
        self.assertEqual(response.status_code, 200)
        self.assertIn('hits', response.data)
        self.assertIn('total', response.data)
        self.assertEqual(response.data['total'], 0)

    def test_matching_query(self):
        response = self.client.get('/api/atlas/search/', dict(q="anjel"))
        self.assertEqual(response.status_code, 200)
        self.assertIn('hits', response.data)
        self.assertIn('total', response.data)
        self.assertEqual(response.data['total'], 5)

        first = response.data['hits'][0]
        self.assertEqual(first['naam'], "Anjeliersstraat")
        self.assertEqual(first['type'], "openbare_ruimte")

    def test_query_case_insensitive(self):
        response = self.client.get('/api/atlas/search/', dict(q="ANJEl"))
        self.assertEqual(response.status_code, 200)
        self.assertIn('hits', response.data)
        self.assertIn('total', response.data)
        self.assertEqual(response.data['total'], 5)

        first = response.data['hits'][0]
        self.assertEqual(first['naam'], "Anjeliersstraat")


