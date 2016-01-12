from rest_framework.test import APITestCase
import time
import datasets.bag.batch
import datasets.brk.batch
from batch import batch

from datasets.bag.tests import factories as bag_factories


class QueryTest(APITestCase):
    """
    Testing commonly used datasets

    # brug
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        openbare_ruimte = bag_factories.OpenbareRuimteFactory.create(
            naam="Anjeliersstraat")

        bag_factories.NummeraanduidingFactory.create(
            openbare_ruimte=openbare_ruimte, huisnummer=11, huisletter='A',
            hoofdadres=True)

        bag_factories.NummeraanduidingFactory.create(
            openbare_ruimte=openbare_ruimte, huisnummer=11, huisletter='B',
            hoofdadres=True)

        bag_factories.NummeraanduidingFactory.create(
            openbare_ruimte=openbare_ruimte, huisnummer=11, huisletter='C',
            hoofdadres=True)

        bag_factories.NummeraanduidingFactory.create(
            openbare_ruimte=openbare_ruimte, huisnummer=12, hoofdadres=True)

        openbare_ruimte = bag_factories.OpenbareRuimteFactory.create(
            naam="Marnixkade")

        bag_factories.NummeraanduidingFactory.create(
            openbare_ruimte=openbare_ruimte, huisnummer=36, huisletter='F',
            hoofdadres=True, postcode='1015XR')

        openbare_ruimte = bag_factories.OpenbareRuimteFactory.create(
            naam="Rozenstraat")

        bag_factories.NummeraanduidingFactory.create(
            openbare_ruimte=openbare_ruimte, huisnummer=228, huisletter='a',
            hoofdadres=True, postcode='1016SZ', huisnummer_toevoeging='1')


        batch.execute(datasets.bag.batch.IndexJob())

        batch.execute(datasets.brk.batch.IndexKadasterJob())

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
        response = self.client.get(
            '/api/atlas/search/', dict(q="anjeliersstraat 11"))
        self.assertEqual(response.status_code, 200)
        self.assertIn('results', response.data)
        self.assertIn('count', response.data)
        self.assertEqual(response.data['count'], 3)

        self.assertEqual(
            response.data['results'][0]['adres'], "Anjeliersstraat 11A")

    def test_query_postcode(self):
        response = self.client.get("/api/atlas/search/", dict(q="1015x"))
        self.assertEqual(response.status_code, 200)
        self.assertIn('results', response.data)
        self.assertIn('count', response.data)
        self.assertEqual(response.data['count'], 2)

        self.assertEqual(response.data['results'][0]['naam'], "Marnixkade")
        self.assertEqual(
            response.data['results'][1]['adres'], "Marnixkade 36F")

    def test_query_straat_huisnummer_huisletter(self):
        response = self.client.get(
            "/api/atlas/search/", dict(q="Rozenstraat 228 a"))
        self.assertEqual(response.status_code, 200)
        self.assertIn('results', response.data)
        self.assertIn('count', response.data)
        self.assertEqual(response.data['count'], 1)

        self.assertEqual(response.data['results'][0]['adres'], "Rozenstraat 228a-1")

    def test_query_straat_huisnummer_huisletter_toevoeging(self):
        response = self.client.get("/api/atlas/search/", dict(q="Rozenstraat 228 a-1"))
        self.assertEqual(response.status_code, 200)
        self.assertIn('results', response.data)
        self.assertIn('count', response.data)
        self.assertEqual(response.data['count'], 1)

        self.assertEqual(response.data['results'][0]['adres'], "Rozenstraat 228a-1")

    def test_query_postcode_space(self):
        response = self.client.get("/api/atlas/search/", dict(q="1016 SZ"))
        self.assertEqual(response.status_code, 200)
        self.assertIn('results', response.data)
        self.assertIn('count', response.data)
        self.assertEqual(response.data['count'], 2)

        self.assertEqual(response.data['results'][0]['naam'], "Rozenstraat")
        self.assertEqual(response.data['results'][1]['adres'], "Rozenstraat 228a-1")

    def test_query_postcode_space_huisnummer(self):
        response = self.client.get("/api/atlas/search/", dict(q="1016 SZ 228"))
        self.assertEqual(response.status_code, 200)
        self.assertIn('results', response.data)
        self.assertIn('count', response.data)
        self.assertEqual(response.data['count'], 1)

        self.assertEqual(response.data['results'][0]['adres'], "Rozenstraat 228a-1")

    def test_query_postcode_space_huisnummer_huisletter(self):
        response = self.client.get("/api/atlas/search/", dict(q="1016 SZ 228 a"))
        self.assertEqual(response.status_code, 200)
        self.assertIn('results', response.data)
        self.assertIn('count', response.data)
        self.assertEqual(response.data['count'], 1)

        self.assertEqual(response.data['results'][0]['adres'], "Rozenstraat 228a-1")

    def test_query_postcode_space_huisnummer_huisletter_toevoeging(self):
        response = self.client.get("/api/atlas/search/", dict(q="1016 SZ 228 a-1"))
        self.assertEqual(response.status_code, 200)
        self.assertIn('results', response.data)
        self.assertIn('count', response.data)
        self.assertEqual(response.data['count'], 1)

        self.assertEqual(response.data['results'][0]['adres'], "Rozenstraat 228a-1")
