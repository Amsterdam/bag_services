# Python
import unittest
# Packages
from django.conf import settings
from elasticsearch import Elasticsearch
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

    def test_match_adresseerbaar_object_met_huisnummer(self):
        response = self.client.get(
            '/atlas/typeahead/',
            {'q': "anjeliersstraat 11"})

        self.assertIn("Anjeliersstraat 11", str(response.data))

    def test_match_postcode(self):
        response = self.client.get("/atlas/typeahead/", {'q': '105'})
        self.assertIn("105", str(response.data))
