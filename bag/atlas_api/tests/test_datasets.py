# Packages
from rest_framework.test import APITestCase
from rest_framework.reverse import reverse
# Project
from datasets.bag.tests import factories as bag_factories
from datasets.brk.tests import factories as brk_factories
from datasets.wkpb.tests import factories as wkpb_factories

from datasets.generic.tests.authorization import AuthorizationSetup


class BrowseDatasetsTestCase(APITestCase, AuthorizationSetup):
    """
    Verifies that browsing the API works correctly.

    We use employee plus authorization which should be able
    to see every endpoint
    """
    datasets = [
        'bag/ligplaats',
        'bag/standplaats',
        'bag/verblijfsobject',


        'bag/pand',
        'bag/nummeraanduiding',
        'bag/openbareruimte',
        'bag/woonplaats',

        'gebieden/stadsdeel',
        'gebieden/buurt',
        'gebieden/bouwblok',

        'wkpb/beperking',
        'wkpb/brondocument',
        'wkpb/broncode',

        'brk/gemeente',
        'brk/kadastrale-gemeente',
        'brk/kadastrale-sectie',

        'brk/object',
        'brk/object-expand',

        'brk/subject',
        'brk/zakelijk-recht',
        'brk/aantekening',
    ]

    def setUp(self):
        bag_factories.LigplaatsFactory.create()
        bag_factories.StandplaatsFactory.create()
        bag_factories.VerblijfsobjectFactory.create()
        bag_factories.PandFactory.create()
        bag_factories.NummeraanduidingFactory.create()
        bag_factories.GemeenteFactory.create()
        bag_factories.WoonplaatsFactory.create()
        bag_factories.StadsdeelFactory.create()
        bag_factories.BuurtFactory.create()
        bag_factories.BouwblokFactory.create()

        wkpb_factories.BeperkingKadastraalObjectFactory.create()
        wkpb_factories.BrondocumentFactory.create()

        brk_factories.GemeenteFactory.create()
        brk_factories.KadastraleGemeenteFactory.create()
        brk_factories.KadastraleSectieFactory.create()
        brk_factories.KadastraalObjectFactory.create()
        brk_factories.KadastraalSubjectFactory.create()
        brk_factories.ZakelijkRechtFactory.create()
        brk_factories.AantekeningFactory.create()

        self.setUpAuthorization()

        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer {}'.format(self.token_employee_plus))

    def valid_response(self, url, response):
        """
        Helper method to check common status/json
        """

        self.assertEqual(
            200, response.status_code,
            'Wrong response code for {}'.format(url))

        self.assertEqual(
            'application/json', response['Content-Type'],
            'Wrong Content-Type for {}'.format(url))

    def valid_html_response(self, url, response):
        """
        Helper method to check common status/json
        """

        self.assertEqual(
            200, response.status_code,
            'Wrong response code for {}'.format(url))

        self.assertEqual(
            'text/html; charset=utf-8', response['Content-Type'],
            'Wrong Content-Type for {}'.format(url))

    def test_lists(self):
        for url in self.datasets:
            response = self.client.get('/{}/'.format(url))

            self.valid_response(url, response)

            self.assertIn(
                'count', response.data, 'No count attribute in {}'.format(url))
            self.assertNotEqual(
                response.data['count'],
                0, 'Wrong result count for {}'.format(url))

    def test_details(self):
        for url in self.datasets:
            response = self.client.get('/{}/'.format(url))

            url = response.data['results'][0]['_links']['self']['href']
            detail = self.client.get(url)

            self.valid_response(url, detail)

            self.assertIn('_display', detail.data)

    def test_lists_html(self):
        for url in self.datasets:
            response = self.client.get('/{}/?format=api'.format(url))

            self.valid_html_response(url, response)

            self.assertIn(
                'count', response.data, 'No count attribute in {}'.format(url))
            self.assertNotEqual(
                response.data['count'],
                0, 'Wrong result count for {}'.format(url))

    def test_details_html(self):
        for url in self.datasets:
            response = self.client.get('/{}/?format=api'.format(url))

            url = response.data['results'][0]['_links']['self']['href']
            detail = self.client.get(url)

            self.valid_html_response(url, detail)

            self.assertIn('_display', detail.data)

    def test_brk_object_wkpb(self):

        url = 'brk/object'

        response = self.client.get('/{}/'.format(url))

        test_id = response.data['results'][0]['id']

        test_url = reverse('brk-object-wkpb', args=[test_id])

        detail = self.client.get(test_url)

        self.valid_response(test_url, detail)

    def test_brk_object_wkpb_html(self):

        url = 'brk/object'

        response = self.client.get('/{}/?format=api'.format(url))

        test_id = response.data['results'][0]['id']

        test_url = reverse('brk-object-wkpb', args=[test_id])

        detail = self.client.get(test_url)

        self.valid_response(test_url, detail)
