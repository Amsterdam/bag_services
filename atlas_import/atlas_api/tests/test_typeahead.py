import unittest

from django.conf import settings
from elasticsearch import Elasticsearch
from rest_framework.test import APITestCase

import datasets.bag.batch
from datasets.bag.tests import factories as bag_factories
import datasets.brk.batch
from batch import batch


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

        batch.execute(datasets.bag.batch.IndexBagJob())
        batch.execute(datasets.brk.batch.IndexKadasterJob())


    def test_match_openbare_ruimte(self):
        response = self.client.get('/atlas/typeahead/', {'q': 'an'})
        self.assertEqual(response.status_code, 200)

        self.assertIn("Anjeliersstraat", str(response.data))

    def test_match_openbare_ruimte_lowercase(self):
        response = self.client.get('/atlas/typeahead/', {'q': 'AN'})
        self.assertEqual(response.status_code, 200)

        self.assertIn("Anjeliersstraat", str(response.data))

    def test_match_maximum_length(self):
        response = self.client.get('/atlas/typeahead/', {'q':'a'})
        self.assertEqual(response.status_code, 200)

        lst = response.data['verblijfsobject ~ 6']
        self.assertEqual(len(lst), 5)

    @unittest.skip("Werkt even niet wegens uitzetten fuzzy-stuff")
    def test_match_adresseerbaar_object(self):
        response = self.client.get('/atlas/typeahead/', {'q': 'anjelier'})
        self.assertEqual(response.status_code, 200)

        obs = [ob['item'] for ob in response.data['weg ~ 1']]
        self.assertIn("Anjeliersstraat", str(response.data))
        #self.assertIn("Anjeliersstraat 11", str(response.data))

    def test_match_adresseerbaar_object_met_huisnummer(self):
        response = self.client.get(
            '/atlas/typeahead/',
            {'q': "anjeliersstraat 11"})

        self.assertIn("Anjeliersstraat 11", str(response.data))

    @unittest.skip(reason="not really stable")
    def test_match_postcode(self):
        response = self.client.get("/atlas/typeahead/", {'q': '105'})
        self.assertIn("105", str(response.data))
