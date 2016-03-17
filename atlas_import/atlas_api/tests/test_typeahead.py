# Python
# Packages
from rest_framework.test import APITestCase
# Project
from batch import batch
import datasets.bag.batch
from datasets.bag.tests import factories as bag_factories
import datasets.brk.batch


class TypeaheadTest(APITestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        anjeliersstraat = bag_factories.OpenbareRuimteFactory.create(
            naam="Anjeliersstraat")

        bag_factories.NummeraanduidingFactory.create(
            openbare_ruimte=anjeliersstraat,
            postcode='1000AN',
            huisnummer=11, huisletter='A', hoofdadres=True)

        bag_factories.NummeraanduidingFactory.create(
            openbare_ruimte=anjeliersstraat,
            postcode='1000AN',
            huisnummer=11, huisletter='B', hoofdadres=True)

        bag_factories.NummeraanduidingFactory.create(
            openbare_ruimte=anjeliersstraat,
            postcode='1000AN',
            huisnummer=11, huisletter='C', hoofdadres=True)

        bag_factories.NummeraanduidingFactory.create(
            postcode='1000AN',
            openbare_ruimte=anjeliersstraat,
            huisnummer=12, hoofdadres=True)

        marnix_kade = bag_factories.OpenbareRuimteFactory.create(
            naam="Marnixkade")

        bag_factories.NummeraanduidingFactory.create(
            openbare_ruimte=marnix_kade,
            huisnummer=36, huisletter='F',
            hoofdadres=True, postcode='1051XR')

        bag_factories.NummeraanduidingFactory.create(
            openbare_ruimte=marnix_kade,
            huisnummer=36, huisletter='F',
            hoofdadres=True, postcode='1052WR')

        rozengracht = bag_factories.OpenbareRuimteFactory.create(
            naam="Rozengracht")

        for t in ['A', 'B', 'C', 'D']:
            bag_factories.NummeraanduidingFactory.create(
                openbare_ruimte=rozengracht,
                huisnummer=2, huisletter=t,
                hoofdadres=True, postcode='1088RG')

        for i in range(100, 120):
            bag_factories.NummeraanduidingFactory.create(
                openbare_ruimte=rozengracht, huisnummer=i,
                toevoeging=2,
                hoofdadres=True, postcode='1088RG')

        eerste_ganshof = bag_factories.OpenbareRuimteFactory.create(
            naam="1e Ganshof")

        bag_factories.NummeraanduidingFactory.create(
            openbare_ruimte=eerste_ganshof,
            huisnummer=20, huisletter='A',
            hoofdadres=True, postcode='1055GH')

        bag_factories.NummeraanduidingFactory.create(
            openbare_ruimte=eerste_ganshof,
            huisnummer=2, huisletter='A',
            hoofdadres=True, postcode='1055GH')

        for i in range(100, 120):

            test_hof = bag_factories.OpenbareRuimteFactory.create(
                naam="testE%shof" % i)

            bag_factories.NummeraanduidingFactory.create(
                openbare_ruimte=test_hof, huisnummer=1,
                huisletter='E',
                hoofdadres=True, postcode='1088TH')

        batch.execute(datasets.bag.batch.IndexBagJob())
        batch.execute(datasets.brk.batch.IndexKadasterJob())

    def test_match_openbare_ruimte(self):
        response = self.client.get('/atlas/typeahead/', {'q': '100'})
        self.assertEqual(response.status_code, 200)
        self.assertIn("1000an", str(response.data))

    def test_match_openbare_ruimte_lowercase(self):
        response = self.client.get('/atlas/typeahead/', {'q': '1000an'})
        self.assertEqual(response.status_code, 200)
        self.assertIn("1000an", str(response.data))

    def test_match_openbare_ruimte_uppercase(self):
        response = self.client.get('/atlas/typeahead/', {'q': '1000AN'})
        self.assertEqual(response.status_code, 200)
        self.assertIn("1000an", str(response.data))

    def test_match_adresseerbaar_object(self):
        response = self.client.get('/atlas/typeahead/', {'q': 'anjelier'})
        self.assertEqual(response.status_code, 200)
        self.assertIn("Anjeliersstraat", str(response.data))
        self.assertIn("Anjeliersstraat 11", str(response.data))

    def test_match_rozenstraat(self):
        response = self.client.get('/atlas/typeahead/', {'q': 'rozengracht 2'})
        self.assertEqual(response.status_code, 200)
        self.assertIn("Rozengracht", str(response.data))
        self.assertIn("Rozengracht 2", str(response.data))

    #def test_match_eerste(self):
    #    response = self.client.get(
    #        '/atlas/typeahead/', {'q': '1e ganshof'})
    #    self.assertEqual(response.status_code, 200)
    #    self.assertIn("1e Ganshof", str(response.data))

    #def test_match_eerste2(self):
    #    response = self.client.get(
    #        '/atlas/typeahead/', {'q': 'eerste ganshof'})
    #    self.assertEqual(response.status_code, 200)
    #    self.assertIn("1e Ganshof", str(response.data))

    #def test_match_eerste_teveel(self):
    #    response = self.client.get(
    #        '/atlas/typeahead/', {'q': 'eerste'})
    #    self.assertEqual(response.status_code, 200)
    #    self.assertIn("1e Ganshof", str(response.data))

    def test_match_adresseerbaar_object_met_huisnummer(self):
        response = self.client.get(
            '/atlas/typeahead/',
            {'q': "anjeliersstraat 11"})

        self.assertIn("Anjeliersstraat 11", str(response.data))

    def test_match_postcode(self):
        response = self.client.get("/atlas/typeahead/", {'q': '105'})
        self.assertIn("105", str(response.data))
