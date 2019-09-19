from rest_framework.test import APITransactionTestCase

from datasets.bag.tests import factories as bag_factories


class LandelijkIDTest(APITransactionTestCase):

    bag_root_url = "/bag/v1.1"

    def setUp(self):
        self.vbo = bag_factories.VerblijfsobjectFactory.create()
        self.na = bag_factories.NummeraanduidingFactory.create()
        self.pand = bag_factories.PandFactory.create()

        self.pand_vbo = bag_factories.VerblijfsobjectPandRelatie()

    def test_vbo_amsterdams_id(self):
        res = self.client.get(self.bag_root_url+'/verblijfsobject/{}/'.format(self.vbo.id))
        self.assertEquals(200, res.status_code)
        self.assertEquals(self.vbo.id, res.data['sleutelverzendend'])

    def test_vbo_landelijk_id(self):
        res = self.client.get(self.bag_root_url+'/verblijfsobject/{}/'.format(
            self.vbo.landelijk_id))
        self.assertEquals(200, res.status_code)
        self.assertEquals(self.vbo.id, res.data['sleutelverzendend'])

    def test_vbo_pand_landelijk_id(self):

        res = self.client.get(
            self.bag_root_url+'/verblijfsobject/?panden__landelijk_id={}'.format(
                self.pand_vbo.pand.landelijk_id))

        self.assertEquals(200, res.status_code)

        self.assertEquals(
            self.pand_vbo.verblijfsobject.id,
            res.json()['results'][0]['id'])

    def test_nummeraanduiding_amsterdams_id(self):
        res = self.client.get(self.bag_root_url+'/nummeraanduiding/{}/'.format(
            self.na.id))
        self.assertEquals(200, res.status_code)
        self.assertEquals(self.na.id, res.data['sleutelverzendend'])

    def test_nummeraanduiding_landelijk_id(self):
        res = self.client.get(self.bag_root_url+'/nummeraanduiding/{}/'.format(
            self.na.landelijk_id))
        self.assertEquals(200, res.status_code)
        self.assertEquals(self.na.id, res.data['sleutelverzendend'])

    def test_pand_amsterdams_id(self):
        res = self.client.get(self.bag_root_url+'/pand/{}/'.format(
            self.pand.id))
        self.assertEquals(200, res.status_code)
        self.assertEquals(self.pand.id, res.data['sleutelverzendend'])

    def test_pand_landelijk_id(self):
        res = self.client.get(self.bag_root_url+'/pand/{}/'.format(
            self.pand.landelijk_id))
        self.assertEquals(200, res.status_code)
        self.assertEquals(self.pand.id, res.data['sleutelverzendend'])
