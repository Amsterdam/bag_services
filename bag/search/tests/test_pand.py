from rest_framework.test import APITestCase
# Project
from batch import batch
import datasets.bag.batch
from datasets.bag.tests import factories as bag_factories
import datasets.brk.batch


class SubjectSearchTest(APITestCase):

    formats = [
        ('api', 'text/html; charset=utf-8'),
        ('json', 'application/json'),
        ('xml', 'application/xml; charset=utf-8'),
        ('csv', 'text/csv; charset=utf-8'),
    ]

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.pand = bag_factories.PandFactory.create()
        batch.execute(datasets.bag.batch.DeleteIndexPandJob())
        batch.execute(datasets.bag.batch.IndexPandJob())

    def test_search_pand_landelijk_id(self):
        q = self.pand.landelijk_id.strip('0')[0:6]
        response = self.client.get('/atlas/search/pand/', {'q': q})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['landelijk_id'], self.pand.landelijk_id)

    def test_search_pand_pandnaam(self):
        q = self.pand.pandnaam.strip('0')[0:6]
        response = self.client.get('/atlas/search/pand/', {'q': q})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['pandnaam'], self.pand.pandnaam)
