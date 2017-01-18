import unittest

from django.conf import settings

from rest_framework.test import APITestCase
from elasticsearch import Elasticsearch

from batch import batch
import datasets.bag.batch
from datasets.bag.tests import factories as bag_factories
import datasets.brk.batch
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

        anjeliersstraat = bag_factories.OpenbareRuimteFactory.create(
            naam="Anjeliersstraat", type='01')

        bag_factories.NummeraanduidingFactory.create(
            openbare_ruimte=anjeliersstraat, huisnummer=11, huisletter='A',
            type='01',
            postcode=1001)

        bag_factories.NummeraanduidingFactory.create(
            openbare_ruimte=anjeliersstraat, huisnummer=11,
            huisletter='B', type='01',
            postcode=1001)

        bag_factories.NummeraanduidingFactory.create(
            openbare_ruimte=anjeliersstraat, huisnummer=11, huisletter='C',
            type='01',
            postcode=1001)

        bag_factories.NummeraanduidingFactory.create(
            postcode=1001,
            type='01',
            openbare_ruimte=anjeliersstraat, huisnummer=12)

        # Maak een woonboot
        kade_ruimte = bag_factories.OpenbareRuimteFactory.create(
            type='01',
            naam="Ligplaatsenstraat")

        bag_factories.NummeraanduidingFactory.create(
            type='05',
            postcode='9999ZZ',
            openbare_ruimte=kade_ruimte, huisnummer=33, hoofdadres=True)

        # marnixkade
        marnix_kade = bag_factories.OpenbareRuimteFactory.create(
            naam="Marnixkade")

        bag_factories.NummeraanduidingFactory.create(
            openbare_ruimte=marnix_kade, huisnummer=36, huisletter='F',
            hoofdadres=True, postcode='1015XR')

        rozenstraat = bag_factories.OpenbareRuimteFactory.create(
            naam="Rozenstraat")

        bag_factories.NummeraanduidingFactory.create(
            openbare_ruimte=rozenstraat, huisnummer=228, huisletter='a',
            hoofdadres=True, postcode='1016SZ', huisnummer_toevoeging='1')

        bag_factories.NummeraanduidingFactory.create(
            openbare_ruimte=rozenstraat, huisnummer=228, huisletter='b',
            hoofdadres=True, postcode='1016SZ', huisnummer_toevoeging='1')

        bag_factories.NummeraanduidingFactory.create(
            openbare_ruimte=rozenstraat, huisnummer=229,
            hoofdadres=True, postcode='1016SZ', huisnummer_toevoeging='1')

        bag_factories.NummeraanduidingFactory.create(
            openbare_ruimte=rozenstraat, huisnummer=229,
            hoofdadres=True, postcode='1016SZ', huisnummer_toevoeging='2')

        bag_factories.NummeraanduidingFactory.create(
            openbare_ruimte=rozenstraat, huisnummer=229,
            hoofdadres=True, postcode='1016SZ', huisnummer_toevoeging='3')

        bag_factories.NummeraanduidingFactory.create(
            openbare_ruimte=rozenstraat, huisnummer=229,
            hoofdadres=True, postcode='1016SZ', huisnummer_toevoeging='4')

        bag_factories.BouwblokFactory.create(code='RN35')
        bag_factories.BouwblokFactory.create(code='AB01')

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
        batch.execute(datasets.bag.batch.IndexGebiedenJob())
        batch.execute(datasets.brk.batch.IndexKadasterJob())

        es = Elasticsearch(hosts=settings.ELASTIC_SEARCH_HOSTS)
        es.indices.refresh(index="_all")

    def test_search_openbare_ruimte_api(self):
        response = self.client.get(
            "/atlas/search/openbareruimte/", {'q': "Prinsengracht"})
        self.assertEqual(response.status_code, 200)
        self.assertIn('results', response.data)
        self.assertIn('count', response.data)
        # self.assertEqual(response.data['count'], 1)

        self.assertEqual(
            response.data['results'][0]['naam'], "Prinsengracht")

        self.assertEqual(
            response.data['results'][0]['subtype'], "water")

    def test_search_subject_api(self):
        response = self.client.get(
            "/atlas/search/kadastraalsubject/", {'q': "kikker"})
        self.assertEqual(response.status_code, 200)
        self.assertIn('results', response.data)
        self.assertIn('count', response.data)

        self.assertEqual(
            response.data['results'][0]['naam'], "Kermet de Kikker")

    def test_search_bouwblok_api(self):
        response = self.client.get(
            "/atlas/search/bouwblok/", {'q': "RN3"})
        self.assertEqual(response.status_code, 200)
        self.assertIn('results', response.data)
        self.assertIn('count', response.data)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(
            response.data['results'][0]['code'], "RN35")

    def test_search_adres_api(self):
        response = self.client.get(
            "/atlas/search/postcode/", {'q': "1016 SZ 228 a 1"})
        self.assertEqual(response.status_code, 200)
        self.assertIn('results', response.data)
        self.assertIn('count', response.data)

        # not due to elk scoring it could happen 228 B, scores better
        # then 228 A
        adres = response.data['results'][0]['adres']
        self.assertTrue(adres.startswith("Rozenstraat 228"))
        self.assertFalse(expr='order' in response.data['results'][0],
                         msg='Order data should be stripped from result')

    def test_postcode_exact(self):
        response = self.client.get(
            "/search/postcode/", {'q': "1016 SZ 228 a 1"})
        self.assertEqual(response.status_code, 200)

        # not due to elk scoring it could happen 228 B, scores better
        # then 228 A
        adres = response.data['adres']
        self.assertTrue(
            adres.startswith("Rozenstraat 228")
        )

    def test_postcode_exact_incorrect_house_num(self):
        response = self.client.get(
            "/search/postcode/", {'q': "1016 SZ 1"})
        self.assertEqual(response.status_code, 200)

        # not due to elk scoring it could happen 228 B, scores better
        # then 228 A
        self.assertNotIn('adres', response.data)

    def test_postcode_exact_no_house_num(self):
        response = self.client.get(
            "/search/postcode/", {'q': "1016 SZ"})
        self.assertEqual(response.status_code, 200)

        # not due to elk scoring it could happen 228 B, scores better
        # then 228 A
        self.assertNotIn('adres', response.data)

