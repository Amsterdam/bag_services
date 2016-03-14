import time
import logging

from unittest import skip

from rest_framework.test import APITestCase

import datasets.bag.batch
from datasets.brk.tests import factories as brk_factories
import datasets.brk.batch
from batch import batch

from django.conf import settings

from elasticsearch import Elasticsearch


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

    def test_match_perceelnummer(self):
        response = self.client.get(
            '/atlas/search/kadastraalobject/',
            dict(q="10000"))
        self.assertEqual(response.status_code, 200)
        self.assertIn("10000", str(response.data))
