from rest_framework.test import APITestCase

from datasets.bag.tests import factories as bag_factories


class LandelijkIDTest(APITestCase):

    def setUp(self):
        self.vbo = bag_factories.VerblijfsobjectFactory.create()
        self.na = bag_factories.NummeraanduidingFactory.create()

    def test_vbo_amsterdams_id(self):
        res = self.client.get('/bag/verblijfsobject/{}/'.format(self.vbo.id))
        self.assertEquals(200, res.status_code)
        self.assertEquals(self.vbo.id, res.data['sleutelverzendend'])

    def test_vbo_landelijk_id(self):
        res = self.client.get('/bag/verblijfsobject/{}/'.format(
            self.vbo.landelijk_id))
        self.assertEquals(200, res.status_code)
        self.assertEquals(self.vbo.id, res.data['sleutelverzendend'])

    def test_nummeraanduiding_amsterdams_id(self):
        res = self.client.get('/bag/nummeraanduiding/{}/'.format(
            self.na.id))
        self.assertEquals(200, res.status_code)
        self.assertEquals(self.na.id, res.data['sleutelverzendend'])

    def test_nummeraanduiding_landelijk_id(self):
        res = self.client.get('/bag/nummeraanduiding/{}/'.format(
            self.na.landelijk_id))
        self.assertEquals(200, res.status_code)
        self.assertEquals(self.na.id, res.data['sleutelverzendend'])
