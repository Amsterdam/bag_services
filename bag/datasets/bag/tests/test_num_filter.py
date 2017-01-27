# Python
import logging
# Packages
from rest_framework.test import APITestCase
# Project
from datasets.bag.tests import factories as bag_factories
from datasets.brk.tests import factories as brk_factories


LOG = logging.getLogger(__name__)


class Numfilter(APITestCase):

    def setUp(self):
        self.vbo = bag_factories.VerblijfsobjectFactory.create()
        self.na = bag_factories.NummeraanduidingFactory.create()
        self.pand = bag_factories.PandFactory.create()

        self.pand_vbo = bag_factories.VerblijfsobjectPandRelatie.create(
            pand=self.pand,
            verblijfsobject=self.vbo)

        self.kot = brk_factories.KadastraalObjectFactory()

        self.kot_vbo = (
            brk_factories
            .KadastraalObjectVerblijfsobjectRelatieFactory
            .create(
                kadastraal_object=self.kot,
                verblijfsobject=self.vbo
            ))

        # add adres to vbo
        self.vbo.adressen.add(self.na)

    def test_kot_filter(self):
        url = f'/bag/nummeraanduiding/?kadastraal_object={self.kot.id}'
        response = self.client.get(url)

        self.assertEquals(200, response.status_code)
        data = response.json()

        self.assertEquals(
            self.na.landelijk_id,
            data['results'][0]['landelijk_id'])

    def test_pand_filter(self):
        url = f'/bag/nummeraanduiding/?pand={self.pand.landelijk_id}'
        response = self.client.get(url)

        self.assertEquals(200, response.status_code)
        data = response.json()

        self.assertEquals(
            self.na.landelijk_id,
            data['results'][0]['landelijk_id'])

    def test_postcode_filter(self):
        url = f'/bag/nummeraanduiding/?postcode={self.na.postcode}'
        response = self.client.get(url)

        self.assertEquals(200, response.status_code)
        data = response.json()
        self.assertEquals(
            self.na.landelijk_id,
            data['results'][0]['landelijk_id'])

    def test_partial_postcode_filter(self):
        url = f'/bag/nummeraanduiding/?postcode={self.na.postcode[:4]}'
        response = self.client.get(url)

        self.assertEquals(200, response.status_code)
        data = response.json()
        self.assertEquals(
            self.na.landelijk_id,
            data['results'][0]['landelijk_id'])

    def test_openbare_ruimte_filter(self):
        url = f'/bag/nummeraanduiding/?openbare_ruimte={self.na.openbare_ruimte.naam[:5]}'
        response = self.client.get(url)

        self.assertEquals(200, response.status_code)
        data = response.json()
        self.assertEquals(
            self.na.landelijk_id,
            data['results'][0]['landelijk_id'])

    def test_location_filter(self):
        url = '/bag/nummeraanduiding/?locatie=1000,1000,10'
        response = self.client.get(url)

        self.assertEquals(200, response.status_code)
        data = response.json()
        self.assertEquals(
            self.na.landelijk_id,
            data['results'][0]['landelijk_id'])

    def test_detailed_view(self):
        url = '/bag/nummeraanduiding/?detailed=1'
        response = self.client.get(url)

        self.assertEquals(200, response.status_code)
        data = response.json()
        # Making sure the details in response contains the detailed fields
        detailed = len(data['results'][0].keys()) > 14
        self.assertEquals(detailed, True)
