from django.conf import settings
from rest_framework.test import APITestCase

from datasets.akr.tests import factories as akr_factories
from datasets.bag.tests import factories as bag_factories
from datasets.wkpb.tests import factories as wkpb_factories
from datasets.brk.tests import factories as brk_factories


class BrowseDatasetsTestCase(APITestCase):
    """
    Verifies that browsing the API works correctly.
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

        'kadaster/object',
        'kadaster/subject',
        'kadaster/transactie',
        'kadaster/zakelijk-recht',
        'kadaster/gemeente',

        'wkpb/beperking',
        'wkpb/brondocument',
        'wkpb/broncode',

        'brk/gemeente',
        'brk/kadastrale-gemeente',
        'brk/kadastrale-sectie',
        'brk/object',
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

        akr_factories.KadastraalObjectFactory.create()
        akr_factories.NatuurlijkPersoonFactory.create()
        akr_factories.TransactieFactory.create()
        akr_factories.ZakelijkRechtFactory.create()

        wkpb_factories.BeperkingKadastraalObjectFactory.create()
        wkpb_factories.BrondocumentFactory.create()

        brk_factories.GemeenteFactory.create()
        brk_factories.KadastraleGemeenteFactory.create()
        brk_factories.KadastraleSectieFactory.create()
        brk_factories.KadastraalObjectFactory.create()
        brk_factories.KadastraalSubjectFactory.create()
        brk_factories.ZakelijkRechtFactory.create()
        brk_factories.AantekeningFactory.create()

    def should_skip_url(self, url):
        return (settings.USE_BRK and url[0:len('kadaster')] == 'kadaster') or (
            not settings.USE_BRK and url[0:len('brk')] == 'brk')

    def test_root(self):
        response = self.client.get('/api/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/hal+json')

        for url in self.datasets:
            if self.should_skip_url(url):
                continue

            self.assertIn(url, response.data)

    def test_lists(self):
        for url in self.datasets:
            if self.should_skip_url(url):
                continue

            response = self.client.get('/api/{}/'.format(url))

            self.assertEqual(response.status_code, 200, 'Wrong response code for {}'.format(url))
            self.assertEqual(response['Content-Type'], 'application/json', 'Wrong Content-Type for {}'.format(url))

            self.assertIn('count', response.data, 'No count attribute in {}'.format(url))
            self.assertNotEqual(response.data['count'], 0, 'Wrong result count for {}'.format(url))

    def test_details(self):
        for url in self.datasets:
            if self.should_skip_url(url):
                continue

            response = self.client.get('/api/{}/'.format(url))

            url = response.data['results'][0]['_links']['self']['href']
            detail = self.client.get(url)

            self.assertEqual(detail.status_code, 200, 'Wrong response code for {}'.format(url))
            self.assertEqual(detail['Content-Type'], 'application/json', 'Wrong Content-Type for {}'.format(url))
            self.assertIn('_display', detail.data)
