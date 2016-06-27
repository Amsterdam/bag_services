from rest_framework.test import APITestCase

from batch import batch
import datasets.bag.batch
import datasets.brk.batch
from datasets.brk.tests import factories as brk_factories


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

        batch.execute(datasets.brk.batch.IndexKadasterJob())

    def test_match_subject(self):
        response = self.client.get(
            '/atlas/search/kadastraalsubject/',
            {'q': 'Kikker'})
        self.assertEqual(response.status_code, 200)
        self.assertIn("Kermet de Kikker", str(response.data))

        response = self.client.get(
            '/atlas/search/kadastraalsubject/',
            {'q': 'Kermet'})
        self.assertEqual(response.status_code, 200)
        self.assertIn("Kermet de Kikker", str(response.data))

    def test_match_subject2(self):
        response = self.client.get(
            '/atlas/search/kadastraalsubject/',
            {'q': 'Stephan Preeker'})
        self.assertEqual(response.status_code, 200)
        self.assertIn("Stephan Jacob Preeker", str(response.data))
