from rest_framework.test import APITestCase

from datasets.wkpb.tests.factories import BeperkingKadastraalObjectFactory


class KadastraalobjectTestCase(APITestCase):
    def setUp(self):
        self.kob = BeperkingKadastraalObjectFactory.create()

        pass

    def test_beperkingen(self):
        response = self.client.get('/api/kadaster/object/%s.html' % self.kob.kadastraal_object_akr.pk)

        self.assertContains(response, '', status_code=200)
        # self.assertEqual(len(response.context[-1]['object.beperkingen.all']), 1)
