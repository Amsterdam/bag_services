# Python
# Package

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

        ptt_straat = bag_factories.OpenbareRuimteFactory.create(
            naam="Marius Cornelis straat",
            type='01')

        nen_straat = bag_factories.OpenbareRuimteFactory.create(
            naam="Stoom Maker Weg",
            naam_nen="S Maker wg",
            type='01')

        kon_straat = bag_factories.OpenbareRuimteFactory.create(
            naam="Koningin Wilhelminaplein",
            naam_nen="K Wilhem pl",
            type='01',
            landelijk_id="0363300000004031")

        straat = bag_factories.OpenbareRuimteFactory.create(
            naam="Anjeliersstraat", type='01', landelijk_id="0363300000002718")

        gracht = bag_factories.OpenbareRuimteFactory.create(
            naam="Prinsengracht", type='01', landelijk_id="0363300000004580")

        straat_1e = bag_factories.OpenbareRuimteFactory.create(
            naam="1e Boomdwarsstraat", type='01', landelijk_id="0363300000002533")

        bag_factories.NummeraanduidingFactory.create(
            huisnummer=192,
            huisletter='A',
            type='01',  # Verblijfsobject
            openbare_ruimte=gracht,
            landelijk_id="0363300000002534"
        )

        cls.anje42F = bag_factories.NummeraanduidingFactory.create(
            huisnummer=42,
            huisletter='F',
            huisnummer_toevoeging='1',
            type='01',  # Verblijfsobject
            openbare_ruimte=straat,
            landelijk_id="0363200000451203"
        )

        bag_factories.NummeraanduidingFactory.create(
            huisnummer=43,
            huisletter='F',
            huisnummer_toevoeging='1',
            type='01',  # Verblijfsobject
            openbare_ruimte=straat,
            landelijk_id="0363200000451204"
        )

        bag_factories.NummeraanduidingFactory.create(
            huisnummer=99,
            huisletter='',
            type='01',  # Verblijfsobject
            openbare_ruimte=ptt_straat,
            landelijk_id="0363200000451205"
        )

        bag_factories.NummeraanduidingFactory.create(
            huisnummer=100,
            huisletter='',
            postcode='1234AB',
            type='01',  # Verblijfsobject
            openbare_ruimte=nen_straat,
            landelijk_id="0363200000451206"
        )

        cls.na1 = bag_factories.NummeraanduidingFactory.create(
            huisnummer=29,
            huisletter='H',
            huisnummer_toevoeging=17,
            postcode='1234AB',
            type='01',  # Verblijfsobject
            openbare_ruimte=kon_straat,
            landelijk_id="0363200000451207"
        )

        bag_factories.NummeraanduidingFactory.create(
            huisnummer=122,
            huisletter='B',
            huisnummer_toevoeging='1A',
            postcode='1234AB',
            type='01',  # Verblijfsobject
            openbare_ruimte=kon_straat,
            landelijk_id="0363200000451208"
        )

        bag_factories.NummeraanduidingFactory.create(
            huisnummer=8,
            huisnummer_toevoeging='3',
            postcode='1234AB',
            type='01',  # Verblijfsobject
            openbare_ruimte=straat_1e,
            landelijk_id="0363200000451209"
        )

        batch.execute(datasets.bag.batch.IndexBagJob())
        batch.execute(datasets.brk.batch.IndexKadasterJob())

    def test_no_match_query(self):
        response = self.client.get(
            '/atlas/search/adres/', {'q': 'x'})
        self.assertEqual(response.status_code, 200)
        self.assertIn('results', response.data)
        self.assertIn('count', response.data)

        self.assertEqual(response.data['count'], 0)

    def test_straat_query(self):
        for fmt, content_type in self.formats:

            url = '/atlas/search/adres/'

            response = self.client.get(
                '/atlas/search/adres/', {'q': 'anjel', 'format': fmt}
            )

            self.assertEqual(
                f"{content_type}",
                response["Content-Type"],
                "Wrong Content-Type for {}".format(url),
            )

            self.assertEqual(response.status_code, 200)
            self.assertIn('results', response.data)
            self.assertIn('count', response.data)

            self.assertEqual(response.data['count'], 2)

            first = response.data['results'][0]
            self.assertEqual(first['straatnaam'], "Anjeliersstraat")

    def test_straat_1e_query(self):
        for fmt, content_type in self.formats:

            url = '/atlas/search/adres/'

            response = self.client.get(
                '/atlas/search/adres/', {'q': '1e boomdw', 'format': fmt}
            )

            self.assertEqual(
                f"{content_type}",
                response["Content-Type"],
                "Wrong Content-Type for {}".format(url),
            )

            self.assertEqual(response.status_code, 200)
            self.assertIn('results', response.data)
            self.assertIn('count', response.data)

            self.assertEqual(response.data['count'], 1)

            first = response.data['results'][0]
            self.assertEqual(first['straatnaam'], "1e Boomdwarsstraat")

    def test_straat_vbo_status(self):
        response = self.client.get(
            '/atlas/search/adres/', {'q': 'Anjeliersstraat 42 F'})

        self.assertEqual(response.status_code, 200)
        self.assertIn('results', response.data)
        self.assertIn('count', response.data)

        # exact 1 result
        self.assertEqual(response.data['count'], 1)

        first = response.data['results'][0]

        vbo_status = self.anje42F.adresseerbaar_object.status

        self.assertEqual(
            first['vbo_status'], vbo_status)

    def test_gracht_query(self):
        response = self.client.get(
            "/atlas/search/adres/", {'q': "prinsengracht 192"})
        self.assertEqual(response.status_code, 200)
        self.assertIn('results', response.data)
        self.assertIn('count', response.data)
        self.assertEqual(response.data['count'], 1)

        self.assertEqual(
            response.data['results'][0]['adres'], "Prinsengracht 192A")

    def test_adres_1e_query(self):
        response = self.client.get(
            "/atlas/search/adres/", {'q': "1e boomdwarsstraat 8 3"})
        self.assertEqual(response.status_code, 200)
        self.assertIn('results', response.data)
        self.assertIn('count', response.data)
        self.assertEqual(response.data['count'], 1)

        self.assertEqual(
            response.data['results'][0]['adres'], "1e Boomdwarsstraat 8-3")

    def test_postcode_huisnummer_query(self):
        response = self.client.get(
            '/atlas/search/adres/', {'q': '1234AB 100'})

        self.assertEqual(response.status_code, 200)
        self.assertIn('results', response.data)
        self.assertIn('count', response.data)

        self.assertEqual(response.data['count'], 1)

        first = response.data['results'][0]
        self.assertEqual(first['straatnaam'], "Stoom Maker Weg")

    def test_nen_query(self):
        response = self.client.get(
            "/atlas/search/adres/", {'q': "s maker wg"})
        self.assertEqual(response.status_code, 200)
        self.assertIn('results', response.data)
        self.assertIn('count', response.data)
        self.assertEqual(response.data['count'], 1)

        self.assertEqual(
            response.data['results'][0]['adres'], "Stoom Maker Weg 100")

    def test_meercijferige_toevoeging(self):
        response = self.client.get(
            "/atlas/search/adres/", {'q': "Koningin Wilhelminaplein 29H 17"})
        self.assertEqual(response.status_code, 200)
        self.assertIn('results', response.data)
        self.assertIn('count', response.data)
        self.assertEqual(response.data['count'], 1)

        self.assertEqual(
            response.data['results'][0]['adres'], "Koningin Wilhelminaplein 29H-17")

    def test_complexe_toevoeging(self):
        response = self.client.get(
            "/atlas/search/adres/", {'q': "Koningin Wilhelminaplein 122B 1A"})
        self.assertEqual(response.status_code, 200)
        self.assertIn('results', response.data)
        self.assertIn('count', response.data)
        self.assertEqual(response.data['count'], 1)

        self.assertEqual(
            response.data['results'][0]['adres'], "Koningin Wilhelminaplein 122B-1A")

    def test_query_landelijk_id(self):
        landelijk_id =  self.na1.landelijk_id.lstrip('0')
        response = self.client.get(
            "/atlas/search/adres/", {'q': landelijk_id})
        self.assertEqual(response.status_code, 200)
        self.assertIn('results', response.data)
        self.assertIn('count', response.data)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['landelijk_id'], self.na1.landelijk_id)

    def test_query_addresseerbaar_object_id_id(self):
        adresseerbaar_object_id = self.na1.verblijfsobject.landelijk_id
        response = self.client.get(
            "/atlas/search/adres/", {'q': adresseerbaar_object_id})
        self.assertEqual(response.status_code, 200)
        self.assertIn('results', response.data)
        self.assertIn('count', response.data)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['adresseerbaar_object_id'], adresseerbaar_object_id )
