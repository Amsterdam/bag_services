# Python
import logging
import time
from unittest import skip
# Packages
from django.conf import settings
from elasticsearch import Elasticsearch
from rest_framework.test import APITestCase
# Project
from batch import batch
import datasets.bag.batch
import datasets.brk.batch
from datasets.brk.tests import factories as brk_factories


log = logging.getLogger('search')

class ObjectSearchTest(APITestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        amsterdam = brk_factories.GemeenteFactory(
            gemeente='Amsterdam'
        )
        kada_amsterdam = brk_factories.KadastraleGemeenteFactory(
            pk='ACD00',
            gemeente=amsterdam
        )

        brk_factories.KadastraalObjectFactory(
            kadastrale_gemeente=kada_amsterdam,
            perceelnummer=10000,  # must be 5 long!
            index_letter='A',
        )

        brk_factories.KadastraalObjectFactory(
            kadastrale_gemeente=kada_amsterdam,
            perceelnummer=999,
        )

        batch.execute(datasets.brk.batch.IndexKadasterJob())

        es = Elasticsearch(hosts=settings.ELASTIC_SEARCH_HOSTS)
        es.indices.refresh(index='_all')

    def test_match_object(self):
        response = self.client.get(
            '/atlas/search/kadastraalobject/',
            dict(q="ACD00"))

        self.assertEqual(response.status_code, 200)
        self.assertIn("ACD00", str(response.data))

    @skip('This test needs to be looked into')
    def test_match_perceelnummer(self):
        response = self.client.get(
            '/atlas/search/kadastraalobject/', {'q': '10000'})
        self.assertEqual(response.status_code, 200)
        print("\n", response.data, "\n")
        self.assertIn("10000", str(response.data))
