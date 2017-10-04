# Packages
from datasets.bag.tests import factories
from rest_framework.test import APITestCase


class CodeRedirectsTest(APITestCase):
    """
    Use code to find object
    """

    def testBouwblokCode(self):
        bbk = factories.BouwblokFactory.create(code='AN34')
        res = self.client.get('/gebieden/bouwblok/AN34/')
        bb_id = res.data['bouwblokidentificatie']
        self.assertEqual(bb_id, bbk.id)

    def testBouwblokCodeFilter(self):
        bbk = factories.BouwblokFactory.create(code='AN34')
        res = self.client.get('/gebieden/bouwblok/?code=AN34')
        bb_id = res.data['results'][0]['id']
        self.assertEqual(bb_id, bbk.id)

    def testStadsdeelCode(self):
        sdl = factories.StadsdeelFactory.create(code='X')
        res = self.client.get('/gebieden/stadsdeel/X/')
        sd_id = res.data['stadsdeelidentificatie']
        self.assertEqual(sd_id, sdl.id)

    def testStadsdeelCodeFilter(self):
        sdl = factories.StadsdeelFactory.create(code='X')
        res = self.client.get('/gebieden/stadsdeel/?code=X')
        sd = res.data['results'][0]
        self.assertEqual(sd['code'], sdl.code)
