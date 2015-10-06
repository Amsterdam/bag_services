from rest_framework.test import APITestCase
import time
import datasets.bag.batch
import datasets.akr.batch
from batch import batch


class QueryTest(APITestCase):

    fixtures = ['dataset.json']

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        batch.execute(datasets.bag.batch.IndexJob())
        batch.execute(datasets.akr.batch.IndexKadasterJob())
        time.sleep(1)   # this is stupid

    def test_non_matching_query(self):
        response = self.client.get('/api/atlas/search/', dict(q="qqq"))
        self.assertEqual(response.status_code, 200)
        self.assertIn('results', response.data)
        self.assertIn('count', response.data)
        self.assertEqual(response.data['count'], 0)

    def test_matching_query(self):
        response = self.client.get('/api/atlas/search/', dict(q="anjel"))
        self.assertEqual(response.status_code, 200)
        self.assertIn('results', response.data)
        self.assertIn('count', response.data)
        self.assertEqual(response.data['count'], 5)

        first = response.data['results'][0]
        self.assertEqual(first['naam'], "Anjeliersstraat")
        self.assertEqual(first['type'], "openbare_ruimte")

    def test_query_case_insensitive(self):
        response = self.client.get('/api/atlas/search/', dict(q="ANJEl"))
        self.assertEqual(response.status_code, 200)
        self.assertIn('results', response.data)
        self.assertIn('count', response.data)
        self.assertEqual(response.data['count'], 5)

        first = response.data['results'][0]
        self.assertEqual(first['naam'], "Anjeliersstraat")

    def test_query_adresseerbaar_object(self):
        response = self.client.get('/api/atlas/search/', dict(q="anjeliersstraat 11"))
        self.assertEqual(response.status_code, 200)
        self.assertIn('results', response.data)
        self.assertIn('count', response.data)
        self.assertEqual(response.data['count'], 3)

        self.assertEqual(response.data['results'][0]['adres'], "Anjeliersstraat 11A")

    def test_query_postcode(self):
        response = self.client.get("/api/atlas/search/", dict(q="1015x"))
        self.assertEqual(response.status_code, 200)
        self.assertIn('results', response.data)
        self.assertIn('count', response.data)
        self.assertEqual(response.data['count'], 2)

        self.assertEqual(response.data['results'][0]['naam'], "Marnixkade")
        self.assertEqual(response.data['results'][1]['adres'], "Marnixkade 36F")


