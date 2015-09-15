from rest_framework.test import APITestCase
import datasets.bag.batch
from batch import batch


class TypeaheadTest(APITestCase):

    fixtures = ['dataset.json']

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        batch.execute(datasets.bag.batch.IndexJob())

    def test_match_openbare_ruimte(self):
        response = self.client.get('/api/atlas/typeahead/', dict(q="an"))
        self.assertEqual(response.status_code, 200)

        lst = response.data
        self.assertEqual(lst[0], "Anjeliersstraat")

    def test_match_openbare_ruimte_lowercase(self):
        response = self.client.get('/api/atlas/typeahead/', dict(q="AN"))
        self.assertEqual(response.status_code, 200)

        lst = response.data
        self.assertEqual(lst[0], "Anjeliersstraat")

    def test_match_maximum_length(self):
        response = self.client.get('/api/atlas/typeahead/', dict(q="a"))
        self.assertEqual(response.status_code, 200)

        lst = response.data
        self.assertEqual(len(lst), 5)



