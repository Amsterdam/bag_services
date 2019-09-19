# Python
import logging
# Packages
from unittest import skip

from django.conf import settings
from elasticsearch import Elasticsearch
from rest_framework.test import APITransactionTestCase
# Project
from batch import batch

import datasets.brk.batch

from datasets.brk.tests import factories as brk_factories

log = logging.getLogger('search')


@skip
class ObjectSearchTest(APITransactionTestCase):
    """
    Kadastraal objecten search tests
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        amsterdam = brk_factories.GemeenteFactory(
            gemeente='Amsterdam',
        )

        kada_amsterdam = brk_factories.KadastraleGemeenteFactory(
            pk='ACD00',
            gemeente=amsterdam,
            naam='Amsterdam',
        )

        kada_amsterdam2 = brk_factories.KadastraleGemeenteFactory(
            pk='ASD15',
            gemeente=amsterdam,
            naam='Amsterdam',
        )

        sectie = brk_factories.KadastraleSectieFactory(
            sectie='S'
        )

        brk_factories.KadastraalObjectFactory(
            kadastrale_gemeente=kada_amsterdam,
            perceelnummer=10000,  # must be 5 long!
            indexletter='A',
            sectie=sectie,
        )

        brk_factories.KadastraalObjectFactory(
            kadastrale_gemeente=kada_amsterdam2,
            perceelnummer='00045',  # must be 5 long!
            indexletter='G',
            indexnummer=0,
            sectie=sectie,
        )

        brk_factories.KadastraalObjectFactory(
            kadastrale_gemeente=kada_amsterdam,
            perceelnummer=999,
        )

        batch.execute(datasets.brk.batch.IndexKadasterJob())

        esclient = Elasticsearch(hosts=settings.ELASTIC_SEARCH_HOSTS)
        esclient.indices.refresh(index='_all')

    def test_match_object(self):
        """
        Minimale match
        """
        response = self.client.get(
            '/atlas/search/kadastraalobject/',
            dict(q="ACD00"))
        self.assertEqual(response.status_code, 200)
        self.assertIn("ACD00", str(response.data['results']))

    # @skip('This test needs to be looked into')
    def test_match_perceelnummer(self):
        """
        perceel number matching
        """
        response = self.client.get(
            '/atlas/search/kadastraalobject/', {'q': 'amsterdam s 10000'})
        self.assertEqual(response.status_code, 200)
        self.assertIn("10000", str(response.data['results']))

    def test_match_object_typeahead(self):
        response = self.client.get(
            '/atlas/typeahead/brk/',
            dict(q="ACD00"))

        self.assertEqual(response.status_code, 200)

        self.assertIn(
            "ACD00", str(response.data))

    def test_kad_stuff(self):
        """
        Test some kot shortcuts
        """

        examples = [
            [['ASD15', 'S', '00045', 'G', '0000'], 'ASD15 S 00045 G 0000'],
            [['ASD15', 'S', '00045', 'G'], 'ASD15 S 00045 G 0000'],
            [['ASD15', 'S', '00045'], 'ASD15 S 00045 G 0000'],
            [['ASD15', 'S'], 'ASD15 S 00045 G 0000'],
        ]

        for example, kot in examples:
            query = " ".join(example)
            response = self.client.get(
                '/atlas/search/kadastraalobject/', {'q': query})

            self.assertEqual(response.status_code, 200)
            self.assertIn(
                kot, str(response.data.get('results', 'empty')), query)

            response = self.client.get(
                '/atlas/typeahead/brk/', {'q': query})

            self.assertEqual(response.status_code, 200)
            self.assertIn(
                kot, str(response.data), query)
