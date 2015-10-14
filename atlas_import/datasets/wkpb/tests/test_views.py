from django.core.urlresolvers import reverse
from rest_framework.test import APITestCase


class WkpbTestCase(APITestCase):
    """
    Test the API for wkpb
    """

    fixtures = ['akr.json', 'lki.json', 'dataset-wkpb.json']

    def test_get_beperking(self):
        response = self.client.get(
            reverse('wkpd-beperking', kwargs={'kadastraal_object_akr': 'ASD24AC01331A0071'})
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')
        self.assertEqual(response.data['inschrijfnummer'], 6672)
