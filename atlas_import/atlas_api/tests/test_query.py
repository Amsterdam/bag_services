from django.conf import settings
from elasticsearch import Elasticsearch
from rest_framework.test import APITestCase

import datasets.bag.batch
import datasets.brk.batch

from batch import batch

from unittest import skip

from datasets.bag.tests import factories as bag_factories
from datasets.brk.tests import factories as brk_factories


class QueryTest(APITestCase):
    """
    Testing commonly used datasets
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        bag_factories.OpenbareRuimteFactory.create(
            naam="Prinsengracht", type='02')

        # Create brug objects
        bag_factories.OpenbareRuimteFactory.create(
            naam="Korte Brug", type='05')

        bag_factories.OpenbareRuimteFactory.create(
            naam="Brugover", type='05')

        bag_factories.OpenbareRuimteFactory.create(
            naam="Brughuis", type='05')

        openbare_ruimte = bag_factories.OpenbareRuimteFactory.create(
            naam="Anjeliersstraat")

        bag_factories.NummeraanduidingFactory.create(
            openbare_ruimte=openbare_ruimte, huisnummer=11, huisletter='A',
            postcode=1001)

        bag_factories.NummeraanduidingFactory.create(
            openbare_ruimte=openbare_ruimte, huisnummer=11, huisletter='B',
            postcode=1001)

        bag_factories.NummeraanduidingFactory.create(
            openbare_ruimte=openbare_ruimte, huisnummer=11, huisletter='C',
            postcode=1001)

        bag_factories.NummeraanduidingFactory.create(
            postcode=1001,
            openbare_ruimte=openbare_ruimte, huisnummer=12)

        # Maak een woonboot
        kade_ruimte = bag_factories.OpenbareRuimteFactory.create(
            type='01',
            naam="Ligplaatsenstraat")

        bag_factories.NummeraanduidingFactory.create(
            type='05',
            postcode='9999ZZ',
            openbare_ruimte=kade_ruimte, huisnummer=33, hoofdadres=True)

        # marnixkade
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

        bag_factories.NummeraanduidingFactory.create(
            openbare_ruimte=openbare_ruimte, huisnummer=229,
            hoofdadres=True, postcode='1016SZ', huisnummer_toevoeging='1')

        adres = brk_factories.AdresFactory(
            huisnummer=340,
            huisletter='A',
            postcode='1234AB',
            woonplaats='FabeltjesLand',
            openbareruimte_naam='Sesamstraat')

        brk_factories.NatuurlijkPersoonFactory(
            naam='Kikker',
            voorvoegsels='de',
            voornamen='Kermet',
            woonadres=adres
        )

        batch.execute(datasets.bag.batch.IndexBagJob())
        batch.execute(datasets.brk.batch.IndexKadasterJob())

        es = Elasticsearch(hosts=settings.ELASTIC_SEARCH_HOSTS)
        es.indices.refresh(index="_all")

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
        self.assertEqual(first['type'], "Openbare ruimte")

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

        self.assertTrue(
                response.data['results'][0]['adres'].startswith(
                        "Anjeliersstraat 11"))

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

        self.assertEqual(
                response.data['results'][0]['adres'], "Rozenstraat 228a-1")

    def test_query_straat_huisnummer_huisnummer(self):
        response = self.client.get(
                "/api/atlas/search/", dict(q="Rozenstraat 229-1"))
        self.assertEqual(response.status_code, 200)
        self.assertIn('results', response.data)
        self.assertIn('count', response.data)
        self.assertEqual(response.data['count'], 1)

        self.assertEqual(
                response.data['results'][0]['adres'], "Rozenstraat 229-1")

    def test_query_straat_huisnummer_huisletter_toevoeging(self):
        response = self.client.get(
                "/api/atlas/search/", dict(q="Rozenstraat 228 a-1"))
        self.assertEqual(response.status_code, 200)
        self.assertIn('results', response.data)
        self.assertIn('count', response.data)
        self.assertEqual(response.data['count'], 1)

        self.assertEqual(
                response.data['results'][0]['adres'], "Rozenstraat 228a-1")

    def test_query_straat_huisnummer_huisletter_toevoeging_enkel(self):
        response = self.client.get(
                "/api/atlas/search/", dict(q="Rozenstraat 228 a-1"))
        self.assertEqual(response.status_code, 200)
        self.assertIn('results', response.data)
        self.assertIn('count', response.data)
        self.assertEqual(response.data['count'], 1)

        self.assertEqual(
                response.data['results'][0]['adres'], "Rozenstraat 228a-1")

    def test_query_postcode_space(self):
        response = self.client.get("/api/atlas/search/", dict(q="1016 SZ"))
        self.assertEqual(response.status_code, 200)
        self.assertIn('results', response.data)
        self.assertIn('count', response.data)
        self.assertEqual(response.data['count'], 3)

        self.assertEqual(response.data['results'][0]['naam'], "Rozenstraat")

        self.assertEqual(
            response.data['results'][1]['adres'], "Rozenstraat 228a-1")

    def test_query_postcode_space_huisnummer(self):
        response = self.client.get("/api/atlas/search/", dict(q="1016 SZ 228"))
        self.assertEqual(response.status_code, 200)
        self.assertIn('results', response.data)
        self.assertIn('count', response.data)
        self.assertEqual(response.data['count'], 1)

        self.assertEqual(
                response.data['results'][0]['adres'], "Rozenstraat 228a-1")

    def test_query_postcode_space_huisnummer_huisletter(self):
        response = self.client.get(
                "/api/atlas/search/", dict(q="1016 SZ 228 a"))
        self.assertEqual(response.status_code, 200)
        self.assertIn('results', response.data)
        self.assertIn('count', response.data)
        self.assertEqual(response.data['count'], 1)

        self.assertEqual(
                response.data['results'][0]['adres'], "Rozenstraat 228a-1")

    def test_query_postcode_space_huisnummer_huisletter_toevoeging(self):
        response = self.client.get(
                "/api/atlas/search/", dict(q="1016 SZ 228 a-1"))
        self.assertEqual(response.status_code, 200)
        self.assertIn('results', response.data)
        self.assertIn('count', response.data)
        self.assertEqual(response.data['count'], 1)

        self.assertEqual(
                response.data['results'][0]['adres'], "Rozenstraat 228a-1")

    def test_query_openbare_ruimte_brug(self):
        response = self.client.get(
                "/api/atlas/search/", dict(q="brug"))
        self.assertEqual(response.status_code, 200)
        self.assertIn('results', response.data)
        self.assertIn('count', response.data)
        self.assertEqual(response.data['count'], 3)

        self.assertIn('Brug', response.data['results'][0]['naam'])

        self.assertEqual(
                response.data['results'][0]['subtype'], "Kunstwerk")

    def test_search_openbare_ruimte_api(self):
        response = self.client.get(
                "/api/atlas/search/openbareruimte/", dict(q="Prinsengracht"))
        self.assertEqual(response.status_code, 200)
        self.assertIn('results', response.data)
        self.assertIn('count', response.data)
        self.assertEqual(response.data['count'], 1)

        self.assertEqual(
                response.data['results'][0]['naam'], "Prinsengracht")

        self.assertEqual(
                response.data['results'][0]['subtype'], "Water")

    def test_search_subject_api(self):
        response = self.client.get(
                "/api/atlas/search/subject/", dict(q="kikker"))
        self.assertEqual(response.status_code, 200)
        self.assertIn('results', response.data)
        self.assertIn('count', response.data)
        self.assertEqual(response.data['count'], 1)

        self.assertEqual(
                response.data['results'][0]['naam'], "Kermet de Kikker")

    @skip
    def test_search_object_api(self):
        response = self.client.get(
                "/api/atlas/search/object/", dict(q="Ligplaatsenstraat 33"))
        self.assertEqual(response.status_code, 200)
        self.assertIn('results', response.data)
        self.assertIn('count', response.data)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(
                response.data['results'][0]['adres'], "Ligplaatsenstraat 33")

    def test_search_adres_api(self):
        response = self.client.get(
                "/api/atlas/search/adres/", dict(q="1016 SZ 228 a-1"))
        self.assertEqual(response.status_code, 200)
        self.assertIn('results', response.data)
        self.assertIn('count', response.data)
        self.assertEqual(response.data['count'], 1)

        self.assertEqual(
                response.data['results'][0]['adres'], "Rozenstraat 228a-1")
