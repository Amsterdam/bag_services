from rest_framework.test import APITestCase
from datasets.bag.tests import factories as bag_factories
from datasets.akr.tests import factories as akr_factories
from datasets.wkpb.tests import factories as wkpb_factories

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
        'kadaster/object',
        'kadaster/subject',
        'kadaster/transactie',
        'kadaster/zakelijk-recht',
        'wkpb/beperking',
    ]

    def setUp(self):
        bag_factories.LigplaatsFactory.create()
        bag_factories.StandplaatsFactory.create()
        bag_factories.VerblijfsobjectFactory.create()
        bag_factories.PandFactory.create()
        bag_factories.NummeraanduidingFactory.create()
        akr_factories.KadastraalObjectFactory.create()
        akr_factories.NatuurlijkPersoonFactory.create()
        akr_factories.TransactieFactory.create()
        akr_factories.ZakelijkRechtFactory.create()
        wkpb_factories.BeperkingKadastraalObjectFactory.create()

    def test_root(self):
        response = self.client.get('/api/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')

        for url in self.datasets:
            self.assertIn(url, response.data)

    def test_lists(self):
        for url in self.datasets:
            response = self.client.get('/api/{}/'.format(url))
            self.assertEqual(response.status_code, 200, 'Wrong response code for {}'.format(url))
            self.assertEqual(response['Content-Type'], 'application/json', 'Wrong Content-Type for {}'.format(url))

            self.assertIn('count', response.data, 'No count attribute in {}'.format(url))
            self.assertNotEqual(response.data['count'], 0, 'Wrong result count for {}'.format(url))

    def test_details(self):
        for url in self.datasets:
            response = self.client.get('/api/{}/'.format(url))
            url = response.data['results'][0]['_links']['self']['href']
            detail = self.client.get(url)

            self.assertEqual(detail.status_code, 200, 'Wrong response code for {}'.format(url))
            self.assertEqual(detail['Content-Type'], 'application/json', 'Wrong Content-Type for {}'.format(url))
