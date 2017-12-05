# Python
import logging
# Packages
from django.contrib.gis.geos import Point, Polygon, MultiPolygon
from rest_framework.test import APITransactionTestCase

from datasets.bag.tests import factories as bag_factories
from datasets.brk.tests import factories as brk_factories

LOG = logging.getLogger(__name__)


class Numfilter(APITransactionTestCase):

    def setUp(self):

        vierkantje = Polygon([
                (121849.65, 487303.93),
                (121889.65, 487303.93),
                (121889.65, 487373.93),
                (121849.65, 487303.93)
        ], srid=28992)

        self.opr = bag_factories.OpenbareRuimteFactory(
            geometrie=MultiPolygon([vierkantje])
        )

        self.vbo = bag_factories.VerblijfsobjectFactory.create(
            geometrie=Point(121849.65, 487303.93, srid=28992))
            # (52.3726097, 4.9004161)

        self.num = bag_factories.NummeraanduidingFactory.create(
            postcode='1000AN',  # default postcode..
            openbare_ruimte=self.opr,
            verblijfsobject=self.vbo,
        )

        self.ligplaats = bag_factories.LigplaatsFactory.create()

        self.num_ligplaats = bag_factories.NummeraanduidingFactory.create(
            postcode='1233AN',
            ligplaats=self.ligplaats
        )

        self.standplaats = bag_factories.StandplaatsFactory.create()

        self.num_standplaats = bag_factories.NummeraanduidingFactory.create(
            postcode='1233XX',
            standplaats=self.standplaats
        )

        self.pand = bag_factories.PandFactory.create(
            geometrie=vierkantje
        )
        self.pand_vbo = bag_factories.VerblijfsobjectPandRelatie.create(
            pand=self.pand,
            verblijfsobject=self.vbo)

        self.kot = brk_factories.KadastraalObjectFactory()

        self.kot_vbo = (
            brk_factories.KadastraalObjectVerblijfsobjectRelatieFactory
            .create(
                kadastraal_object=self.kot,
                verblijfsobject=self.vbo
            )
         )

        # add adres to vbo
        self.vbo.adressen.add(self.num)

        # Creating an extra Nummeraanduiding.
        # this should be expanded to a full item
        self.bad_na = bag_factories.NummeraanduidingFactory.create(
            postcode='2000ZZ')

    def test_kot_filter(self):
        url = f'/bag/nummeraanduiding/?kadastraalobject={self.kot.id}'
        response = self.client.get(url)

        self.assertEquals(200, response.status_code)
        data = response.json()

        self.assertEquals(
            self.num.landelijk_id,
            data['results'][0]['landelijk_id'])

    def test_pand_filter(self):
        url = f'/bag/nummeraanduiding/?pand={self.pand.landelijk_id}'
        response = self.client.get(url)

        self.assertEquals(200, response.status_code)
        data = response.json()

        self.assertEquals(
            self.num.landelijk_id,
            data['results'][0]['landelijk_id'])

    def test_vbo_filter(self):
        url = f'/bag/nummeraanduiding/?verblijfsobject={self.vbo.landelijk_id}'
        response = self.client.get(url)

        self.assertEquals(200, response.status_code)
        data = response.json()

        self.assertEquals(
            self.num.landelijk_id,
            data['results'][0]['landelijk_id'])

    def test_standplaats_filter(self):
        test_param = f"standplaats={self.standplaats.landelijk_id}"
        url = f'/bag/nummeraanduiding/?{test_param}'
        response = self.client.get(url)

        self.assertEquals(200, response.status_code)
        data = response.json()

        self.assertEquals(
            self.num_standplaats.landelijk_id,
            data['results'][0]['landelijk_id'])

    def test_ligplaats_filter(self):
        test_param = f"ligplaats={self.ligplaats.landelijk_id}"
        url = f'/bag/nummeraanduiding/?{test_param}'
        response = self.client.get(url)

        self.assertEquals(200, response.status_code)
        data = response.json()

        self.assertEquals(
            self.num_ligplaats.landelijk_id,
            data['results'][0]['landelijk_id'])

    def test_postcode_filter(self):
        url = f'/bag/nummeraanduiding/?postcode={self.num.postcode}'
        response = self.client.get(url)

        self.assertEquals(200, response.status_code)
        data = response.json()
        self.assertEquals(
            self.num.landelijk_id,
            data['results'][0]['landelijk_id'])

    def test_partial_postcode_filter(self):
        url = f'/bag/nummeraanduiding/?postcode={self.num.postcode[:4]}'
        response = self.client.get(url)

        self.assertEquals(200, response.status_code)
        data = response.json()
        self.assertEquals(
            self.num.landelijk_id,
            data['results'][0]['landelijk_id'])
        self.assertEquals(
            len(data['results']), 1
        )

    def test_openbare_ruimte_filter(self):
        url = f'/bag/nummeraanduiding/?openbare_ruimte={self.num.openbare_ruimte.naam[:5]}'   # noqa
        response = self.client.get(url)

        self.assertEquals(200, response.status_code)
        data = response.json()
        self.assertEquals(
            self.num.landelijk_id,
            data['results'][0]['landelijk_id'])

    def test_location_filter(self):

        url = '/bag/nummeraanduiding/?locatie=121849,487303,20'
        response = self.client.get(url)

        self.assertEquals(200, response.status_code)
        data = response.json()
        self.assertEquals(
            self.num.landelijk_id,
            data['results'][0]['landelijk_id'])

    def test_location_filter_2(self):
        url = '/bag/nummeraanduiding/?locatie=52.3726097,4.9004161,10'
        response = self.client.get(url)

        self.assertEquals(200, response.status_code)
        data = response.json()
        self.assertEquals(
            self.num.landelijk_id,
            data['results'][0]['landelijk_id'])

    def test_opr_location_filter_in(self):
        url = '/bag/openbareruimte/?locatie=121850,487304,10'
        response = self.client.get(url)

        self.assertEquals(200, response.status_code)
        data = response.json()
        self.assertEquals(
            self.opr.landelijk_id,
            data['results'][0]['landelijk_id'])

    def test_opr_location_filter_out(self):
        url = '/bag/openbareruimte/?locatie=100000,400000,10'
        response = self.client.get(url)

        self.assertEquals(200, response.status_code)
        data = response.json()
        self.assertEquals(data['results'], [])

    def test_pand_location_filter_in(self):
        url = '/bag/pand/?locatie=121850,487304,10'
        response = self.client.get(url)

        self.assertEquals(200, response.status_code)
        data = response.json()
        self.assertEquals(
            self.pand.landelijk_id,
            data['results'][0]['landelijk_id'])

    def test_pand_location_filter_out(self):
        url = '/bag/pand/?locatie=100000,400000,10'
        response = self.client.get(url)

        self.assertEquals(200, response.status_code)
        data = response.json()
        self.assertEquals(data['results'], [])

    def test_pand_location_filter_error(self):
        url = '/bag/pand/?locatie=X00000,X00000,10'
        response = self.client.get(url)

        self.assertEquals(400, response.status_code)
        data = response.json()
        self.assertEquals(data,
            ['Locatie must be x: float, y: float, r: int'])

    def test_detailed_view(self):
        url = '/bag/nummeraanduiding/?detailed=1'
        response = self.client.get(url)

        self.assertEquals(200, response.status_code)
        data = response.json()
        # Making sure the details in response contains the detailed fields
        detailed = len(data['results'][0].keys()) > 14
        self.assertEquals(detailed, True)
