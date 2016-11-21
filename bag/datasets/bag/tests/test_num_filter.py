import logging

# django
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
        url = '/bag/nummeraanduiding/?kadastraal_object={}'
        response = self.client.get(url.format(self.kot.id))

        self.assertEquals(200, response.status_code)
        data = response.json()

        self.assertEquals(
            self.na.landelijk_id,
            data['results'][0]['landelijk_id'])

    def test_pand_filter(self):
        url = '/bag/nummeraanduiding/?pand={}'
        response = self.client.get(url.format(self.pand.landelijk_id))

        self.assertEquals(200, response.status_code)
        data = response.json()

        self.assertEquals(
            self.na.landelijk_id,
            data['results'][0]['landelijk_id'])

    def test_postcode_filter(self):
        url = '/bag/nummeraanduiding/?postcode={}'
        response = self.client.get(url.format(self.na.postcode))

        self.assertEquals(200, response.status_code)
        data = response.json()
        self.assertEquals(
            self.na.landelijk_id,
            data['results'][0]['landelijk_id'])
