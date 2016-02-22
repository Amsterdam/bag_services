from rest_framework.test import APITestCase

from datasets.bag.tests import factories as bag_factories
from datasets.brk.tests import factories as brk_factories
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

    def test_lists(self):
        for url in self.datasets:
            response = self.client.get('/{}/'.format(url))

            self.assertEqual(response.status_code, 200, 'Wrong response code for {}'.format(url))
            self.assertEqual(response['Content-Type'], 'application/json', 'Wrong Content-Type for {}'.format(url))

            self.assertIn('count', response.data, 'No count attribute in {}'.format(url))
            self.assertNotEqual(response.data['count'], 0, 'Wrong result count for {}'.format(url))

    def test_details(self):
        for url in self.datasets:
            response = self.client.get('/{}/'.format(url))

            url = response.data['results'][0]['_links']['self']['href']
            detail = self.client.get(url)

            self.assertEqual(detail.status_code, 200, 'Wrong response code for {}'.format(url))
            self.assertEqual(detail['Content-Type'], 'application/json', 'Wrong Content-Type for {}'.format(url))
            self.assertIn('_display', detail.data)
