# Python
from unittest import skip
import string
import random
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

        linnaeusdwarsstraat = bag_factories.OpenbareRuimteFactory.create(
            naam="linnaeusdwarsstraat")

        weesperstraat = bag_factories.OpenbareRuimteFactory.create(
            naam="Weesperstraat")

        metro_weesperstraat = bag_factories.OpenbareRuimteFactory.create(
            naam="Metrostation Weesperstraat")

        bron_schimmel = bag_factories.OpenbareRuimteFactory.create(
            naam="Baron Schimmelpenninck van der Oyeweg")

        pieter_corn = bag_factories.OpenbareRuimteFactory.create(
            naam="Pieter Cornelisz. Hooftstraat"
        )

        rob_straatjes = [
            linnaeusdwarsstraat, weesperstraat, metro_weesperstraat,
            bron_schimmel, pieter_corn
        ]

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

        # create some random nummeraanduidingen
        for openbare_ruimte in rob_straatjes:
            hi = random.randint(5, 50)
            tv = random.choice(['2', 'A', 'AA', 'Z', '3'])
            r_postcode = random.randint(1001, 1040)
            l1 = random.choice(string.ascii_letters)
            l2 = random.choice(string.ascii_letters)
            postcode = '%s%s%s' % (r_postcode, l1, l2)

            bag_factories.NummeraanduidingFactory.create(
                openbare_ruimte=openbare_ruimte, huisnummer=hi,
                toevoeging=tv,
                hoofdadres=True, postcode=postcode)

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

        toevoeg_hof = bag_factories.OpenbareRuimteFactory.create(
            naam="Toevoeg Hof")

        bag_factories.NummeraanduidingFactory.create(
            openbare_ruimte=toevoeg_hof, huisnummer=1,
            huisletter='P',
            hoofdadres=True, postcode='1188TV')

        batch.execute(datasets.bag.batch.IndexBagJob())
        batch.execute(datasets.brk.batch.IndexKadasterJob())

    def test_match_openbare_ruimte(self):
        response = self.client.get('/atlas/typeahead/', {'q': '100'})
        self.assertEqual(response.status_code, 200)
        self.assertIn("Anjeliersstraat", str(response.data))

    def test_match_openbare_ruimte_lowercase(self):
        response = self.client.get('/atlas/typeahead/', {'q': '1000an'})
        self.assertEqual(response.status_code, 200)
        self.assertIn("Anjeliersstraat", str(response.data))

    def test_match_openbare_ruimte_uppercase(self):
        response = self.client.get('/atlas/typeahead/', {'q': '1000AN'})
        self.assertEqual(response.status_code, 200)
        self.assertIn("Anjeliersstraat", str(response.data))

    def test_match_adresseerbaar_object(self):
        response = self.client.get('/atlas/typeahead/', {'q': 'anjelier'})
        self.assertEqual(response.status_code, 200)
        self.assertIn("Anjeliersstraat", str(response.data))

    def test_match_rozenstraat(self):
        response = self.client.get('/atlas/typeahead/', {'q': 'rozengracht'})
        self.assertEqual(response.status_code, 200)
        self.assertIn("Rozengracht", str(response.data))

    @skip('This could return results but is not essential')
    def test_match_adresseerbaar_object_met_huisnummer(self):
        response = self.client.get(
            '/atlas/typeahead/',
            {'q': "anjeliersstraat 11"})
        self.assertIn("Anjeliersstraat", str(response.data))

    @skip('This could return results but is not essential')
    def test_match_adresseerbaar_object_toevoeg_hog(self):
        response = self.client.get(
            '/atlas/typeahead/',
            {'q': "toevoeg hof 1"})

        self.assertIn("Toevoeg Hof", str(response.data))

    def test_match_postcode(self):
        response = self.client.get("/atlas/typeahead/", {'q': '105'})
        self.assertIn("1e Ganshof", str(response.data))

    # Rob tests

    def test_partial_street_name(self):
        response = self.client.get("/atlas/typeahead/", {'q': 'linnae'})
        self.assertIn("linnaeusdwarsstraat", str(response.data))

    def test_partial_with_metro(self):
        response = self.client.get("/atlas/typeahead/", {'q': 'Weesperstraat'})
        # todo order?
        self.assertIn("Metrostation", str(response.data))
        self.assertIn("Weesperstraat", str(response.data))

    def test_partial_prefix_later_words(self):
        response = self.client.get("/atlas/typeahead/", {'q': 'oyeweg'})
        self.assertIn(
            "Baron Schimmelpenninck van der Oyeweg",
            str(response.data))

    @skip('This should return results but is not essential')
    def test_punctuations_in_street_name(self):
        response = self.client.get("/atlas/typeahead/", {'q': 'p c hooft'})
        self.assertIn(
            "pieter cornelisz. hooftstraat",
            str(response.data))

    def test_random_shit_tests(self):
        """
        random stuff that crashes search / inspired by ein smoke tests
        """
        source = string.ascii_letters + string.digits + ' ' * 20
        for i in range(150):
            KEY_LEN = random.randint(1, 15)
            keylist = [random.choice(source) for i in range(KEY_LEN)]
            query = "".join(keylist)

            response = self.client.get("/atlas/typeahead/", {
                'q': "".join(query)})

            self.assertEqual(response.status_code, 200)
