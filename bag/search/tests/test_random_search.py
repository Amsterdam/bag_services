# Python
import string
import random
# Packages
from rest_framework.test import APITestCase
# Project
from search.tests.fill_elastic import load_docs

import logging
log = logging.getLogger(__name__)


class RandomShitTest(APITestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        load_docs()

    def test_random_shit_typeahead(self):
        """
        random stuff that crashes search / inspired by ein smoke tests
        """

        typeahead_endpoints = [
            '/atlas/typeahead/bag/',
            '/atlas/typeahead/brk/',
            '/atlas/typeahead/gebieden/',
        ]

        for url in typeahead_endpoints:
            self.bomb_endpoint(url)

    def test_random_shit_endpoints(self):
        """
        random stuff that crashes search / inspired by ein smoke tests
        """
        search_endpoints = [
            '/atlas/search/adres/',
            '/atlas/search/bouwblok/',
            '/atlas/search/kadastraalsubject/',
            '/atlas/search/kadastraalobject/',
            '/atlas/search/postcode/',
            '/atlas/search/openbareruimte/',
            '/atlas/search/gebied/',

            # '/search/postcode/',
        ]

        for url in search_endpoints:
            log.debug('random_testing: %s', url)
            self.bomb_endpoint(url)

    def bomb_endpoint(self, url):
        """
        Bomb enpoints with junk make sure nothing causes a
        crash
        """
        source = string.ascii_letters + string.digits + ' ' * 20
        for i in range(450):
            KEY_LEN = random.randint(1, 35)
            keylist = [random.choice(source) for i in range(KEY_LEN)]
            query = "".join(keylist)

            response = self.client.get(url, {
                'q': "".join(query)})

            self.assertEqual(response.status_code, 200, url)
