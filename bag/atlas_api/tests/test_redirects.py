# Packages
from datasets.bag.tests import factories
from rest_framework.test import APITestCase


class RedirectsTest(APITestCase):
    def testBouwblokCode(self):
        bbk = factories.BouwblokFactory.create(code='AN34')
        res = self.client.get('/gebieden/bouwblok/AN34/')

        self.assertRedirects(res, '/gebieden/bouwblok/{}/'.format(bbk.pk))

    def testStadsdeelCode(self):
        sdl = factories.StadsdeelFactory.create(code='X')
        res = self.client.get('/gebieden/stadsdeel/X/')

        self.assertRedirects(res, '/gebieden/stadsdeel/{}/'.format(sdl.pk))
