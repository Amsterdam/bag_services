import time
from unittest import skip

from rest_framework.test import APITestCase

import datasets.bag.batch
from datasets.brk.tests import factories as brk_factories
import datasets.brk.batch
from batch import batch


class SubjectSearchTest(APITestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        adres = brk_factories.AdresFactory(
            huisnummer=340,
            huisletter='A',
            postcode='1234AB',
            woonplaats='FabeltjesLand',
            openbareruimte_naam='Sesamstraat')

        brk_factories.NatuurlijkPersoonFactory(
            naam='Preeker',
            voornamen='Stephan Jacob',
            woonadres=adres
        )

        brk_factories.NatuurlijkPersoonFactory(
            naam='Kikker',
            voorvoegsels='de',
            voornamen='Kermet',
            woonadres=adres
        )

        batch.execute(datasets.bag.batch.IndexJob())

        batch.execute(datasets.brk.batch.IndexKadasterJob())

        time.sleep(1)   # this is stupid

    def test_match_subject(self):
        response = self.client.get(
            '/api/atlas/search/subject/',
            dict(q="Kikker"))
        self.assertEqual(response.status_code, 200)
        self.assertIn("Kermet de Kikker", str(response.data))

        response = self.client.get(
            '/api/atlas/search/subject/',
            dict(q="Kermet"))
        self.assertEqual(response.status_code, 200)
        self.assertIn("Kermet de Kikker", str(response.data))

    def test_match_subject2(self):
        response = self.client.get(
            '/api/atlas/search/subject/',
            dict(q="Stephan Preeker"))
        self.assertEqual(response.status_code, 200)
        self.assertIn("Stephan Jacob Preeker", str(response.data))
