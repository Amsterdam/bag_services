
import logging
import json

# Packages
from rest_framework.test import APITransactionTestCase
from rest_framework.reverse import reverse
# Project
from datasets.bag.tests import factories as bag_factories
from datasets.brk.tests import factories as brk_factories
from datasets.wkpb.tests import factories as wkpb_factories

from datasets.generic.tests.authorization import AuthorizationSetup

from django.core.management import call_command



LOG = logging.getLogger(__name__)


def pretty_data(data):
    return json.dumps(data, indent=4, sort_keys=True)


class BrowseDatasetsTestCase(APITransactionTestCase, AuthorizationSetup):
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
        'gebieden/wijk',
        'gebieden/buurtcombinatie',
        'gebieden/gebiedsgerichtwerken',
        'gebieden/grootstedelijkgebied',

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

    formats = [
        ('api', 'text/html; charset=utf-8'),
        ('json', 'application/json'),
        ('xml', 'application/xml; charset=utf-8'),
        ('csv', 'text/csv; charset=utf-8'),
    ]

    def setUp(self):
        """
        This create a graph of objects that point to
        each others with nice working links

        This is done to test the generated
        links and properly

        """

        bag_factories.GrootstedelijkGebiedFactory()

        # gebieden
        stadsdeel = bag_factories.StadsdeelFactory.create(
            id='testdatasets', code='ABC')

        bag_factories.GebiedsgerichtwerkenFactory.create(
            stadsdeel=stadsdeel
        )

        bc = bag_factories.BuurtcombinatieFactory.create(
            stadsdeel=stadsdeel,
        )

        buurt = bag_factories.BuurtFactory.create(
            stadsdeel=stadsdeel,
            buurtcombinatie=bc
        )
        self.buurt = buurt

        bag_factories.BouwblokFactory.create(
            buurt=buurt
        )

        ligplaats = bag_factories.LigplaatsFactory.create(
            buurt=buurt
        )
        standplaats = bag_factories.StandplaatsFactory.create(
            buurt=buurt
        )
        vbo = bag_factories.VerblijfsobjectFactory.create(
            buurt=buurt
        )
        pand = bag_factories.PandFactory.create()

        opr = bag_factories.OpenbareRuimteFactory()

        bag_factories.VerblijfsobjectPandRelatie(
            pand=pand,
            verblijfsobject=vbo
        )

        bag_factories.NummeraanduidingFactory.create(
            ligplaats=ligplaats,
            standplaats=standplaats,
            verblijfsobject=vbo,
            openbare_ruimte=opr,
        )

        bag_factories.GemeenteFactory.create()

        bag_factories.WoonplaatsFactory.create()

        kot_gem = brk_factories.KadastraleGemeenteFactory.create()

        kot_sectie = brk_factories.KadastraleSectieFactory.create(
            kadastrale_gemeente=kot_gem
        )

        kot = brk_factories.KadastraalObjectFactory.create(
            kadastrale_gemeente=kot_gem,
            sectie=kot_sectie
        )

        brk_factories.APerceelGPerceelRelatieFactory.create(
            a_perceel=kot,
            g_perceel=kot,
        )

        beperking = wkpb_factories.BeperkingFactory()

        wkpb_factories.BeperkingKadastraalObjectFactory.create(
            beperking=beperking,
            kadastraal_object=kot
        )

        wkpb_factories.BrondocumentFactory.create(
            beperking=beperking
        )

        brk_factories.GemeenteFactory.create(
            gemeente='Amsterdam'
        )
        brk_factories.KadastraalObjectVerblijfsobjectRelatieFactory(
            kadastraal_object=kot,
            verblijfsobject=vbo
        )

        sub = brk_factories.KadastraalSubjectFactory.create()

        brk_factories.ZakelijkRechtFactory.create(
            kadastraal_object=kot,
            kadastraal_subject=sub
        )
        self.aantekening = brk_factories.AantekeningFactory.create(
            aantekening_id='NL.KAD.Aantekening.AKR1.100000007082195',
            kadastraal_object=kot,
            opgelegd_door=sub
        )

        self.setUpAuthorization()
        self.makesuperuser()

    def test_root_urls(self):
        """
        Visit all root main api pages
        """
        urls = [
            'atlas/search',
            'atlas/typeahead',
            'wkpb',
            'bag',
            'brk',
            'gebieden',
        ]

        for url in urls:
            response = self.client.get('/{}/'.format(url))
            self.valid_response(url, response, 'application/json')

    def makesuperuser(self):
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer {}'.format(self.token_employee_plus))

    def valid_response(
            self, url, response,
            content_type='text/html; charset=utf-8'):
        """
        Helper method to check common status/json
        """

        self.assertEqual(
            200, response.status_code, "Wrong response code for {}".format(url)
        )

        self.assertEqual(
            f"{content_type}",
            response["Content-Type"],
            "Wrong Content-Type for {}".format(url),
        )

    def test_lists(self):
        for _format, encoding in self.formats:
            for url in self.datasets:
                response = self.client.get(f'/{url}/', {'format': _format})

                self.valid_response(url, response, encoding)

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

            self.valid_response(url, detail, 'application/json')

            self.assertIn('_display', detail.data)

    def test_links_in_details(self):
        for url in self.datasets:

            response = self.client.get('/{}/'.format(url))

            url = response.data['results'][0]['_links']['self']['href']

            detail = self.client.get(url)

            self.valid_response(url, detail, 'application/json')

            self.assertIn('_display', detail.data)

            if url:
                self.find_all_href(detail.data)

    def find_all_href(self, data):
        """
        Validate al links referenced in json documents
        """

        data = [data]

        tested_urls = set()

        jsondata = pretty_data(data)

        while data:
            item = data.pop()

            for key, value in item.items():
                # external link cannot be checked in standalone testrun
                if key == '_monumenten':
                    self.assertIn('https://api.data.amsterdam.nl/monumenten/monumenten/?betreft_pand=', value['href'])
                    continue

                if isinstance(value, dict):
                    # new object to check
                    data.append(value)

                if key != 'href':
                    continue

                url = value

                if not self.follow_href(item, url):
                    continue

                self.item_href_checks(url, tested_urls, jsondata)

    def follow_href(self, item, url):
        """
        check if we should follow link in item
        """

        # check if there is a count.
        # do not follow.
        if 'count' in item:
            if not item['count']:
                # skip this one
                return False

        return True

    def item_href_checks(self, url, tested_urls, jsondata):

        # keep track of already vistited urls
        if url in tested_urls:
            return

        tested_urls.add(url)

        # visited endpoint
        result = self.client.get(url)

        self.assertEqual(result.status_code, 200, url)
        LOG.debug('test url %s', url)

        self.valid_response(url, result, 'application/json')

        if 'count' in result.data:
            pdata = pretty_data(result.data)

            self.assertNotEqual(
                result.data['count'], 0,
                f'\n\n {jsondata} \n\n {pdata} \n\n')

    def test_lists_html(self):

        for url in self.datasets:
            response = self.client.get(
                f'/{url}/', {'format': 'api'})

            self.valid_response(url, response, 'text/html; charset=utf-8')

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

            self.valid_response(url, detail)

            self.assertIn('_display', detail.data)

    def test_brk_object_wkpb(self):

        url = 'brk/object'

        response = self.client.get('/{}/'.format(url))

        test_id = response.data['results'][0]['id']

        test_url = reverse('brk-object-wkpb', args=[test_id])

        detail = self.client.get(test_url)

        self.valid_response(test_url, detail, 'application/json')

    def test_brk_object_wkpb_html(self):

        url = 'brk/object'

        response = self.client.get(f'/{url}/', {'format': 'api'})

        test_id = response.data['results'][0]['id']

        test_url = reverse('brk-object-wkpb', args=[test_id])

        detail = self.client.get(test_url, {'format': 'api'})

        self.valid_response(test_url, detail, 'text/html; charset=utf-8')

    def test_kos_filter(self):

        url = 'brk/subject'

        response = self.client.get(f'/{url}/', {'buurt': self.buurt.vollcode})

        self.assertEqual(response.status_code, 200)

    def test_aantekening_id(self):

        url = 'brk/aantekening'

        aantekening_id = self.aantekening.aantekening_id
        _id = self.aantekening.id

        response = self.client.get(f'/{url}/{_id}/')
        self.assertEqual(response.status_code, 200)
        response = self.client.get(f'/{url}/{aantekening_id}/')
        self.assertEqual(response.status_code, 200)

    def test_validate_tables(self):
        """Make sure validation command runs.
        """
        try:
            output = call_command('run_import', '--validate')
        except ValueError:
            # should fail. the tables are not filled.
            pass
