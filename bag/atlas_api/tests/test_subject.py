from django.contrib.auth.models import User, Permission
from django.contrib.contenttypes.models import ContentType

from rest_framework.test import APITestCase

from rest_framework_jwt.settings import api_settings

from batch import batch
import datasets.brk.batch

from datasets.brk.tests import factories as brk_factories
from datasets.generic.tests.authorization import AuthorizationSetup


class SubjectSearchTest(APITestCase, AuthorizationSetup):

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

        brk_factories.NietNatuurlijkPersoonFactory(
            naam='stoeptegel bakker',
            statutaire_naam='stoeptegel bakker',
            woonadres=adres,
        )

        batch.execute(datasets.brk.batch.IndexKadasterJob())

    def setUp(self):
        self.setUpAuthorization()

    def test_match_subject2(self):
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer {}'.format(self.token_employee_plus))

        response = self.client.get(
            '/atlas/search/kadastraalsubject/',
            {'q': 'Stephan Preeker'})
        self.assertEqual(response.status_code, 200)
        self.assertIn("Stephan Jacob Preeker", str(response.data))

        response = self.client.get(
            '/atlas/search/kadastraalsubject/',
            {'q': 'stoeptegel'})
        self.assertEqual(response.status_code, 200)
        self.assertIn("stoeptegel", str(response.data))

    def test_match_subject2_not_authorizer(self):
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer {}'.format(self.token_default))

        response = self.client.get(
            '/atlas/search/kadastraalsubject/',
            {'q': 'Stephan Preeker'})
        self.assertEqual(response.status_code, 200)
        self.assertNotIn("Stephan Jacob Preeker", str(response.data))

        response = self.client.get(
            '/atlas/search/kadastraalsubject/',
            {'q': 'stoeptegel'})
        self.assertEqual(response.status_code, 200)
        self.assertNotIn("stoeptegel", str(response.data))

    def test_match_subject2_employee_authorized(self):
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer {}'.format(self.token_employee))

        # we should not find person
        response = self.client.get(
            '/atlas/search/kadastraalsubject/',
            {'q': 'Stephan Preeker'})
        self.assertEqual(response.status_code, 200)
        self.assertNotIn("Stephan Jacob Preeker", str(response.data))

        # we should find stoeptegel
        response = self.client.get(
            '/atlas/search/kadastraalsubject/',
            {'q': 'stoeptegel'})
        self.assertEqual(response.status_code, 200)
        self.assertIn("stoeptegel", str(response.data))

    def test_match_subject_not_authorized(self):
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer {}'.format(self.token_default))

        response = self.client.get(
            '/atlas/search/kadastraalsubject/',
            {'q': 'Kikker'})
        self.assertEqual(response.status_code, 200)

        self.assertNotIn("Kermet de Kikker", str(response.data))

        response = self.client.get(
            '/atlas/search/kadastraalsubject/',
            {'q': 'Kermet'})

        self.assertEqual(response.status_code, 200)

        self.assertNotIn("Kermet de Kikker", str(response.data))

        response = self.client.get(
            '/atlas/search/kadastraalsubject/',
            {'q': 'stoeptegel'})

        self.assertEqual(response.status_code, 200)

        self.assertNotIn("stoeptegel", str(response.data))

    def test_match_typeahead_subject_employeeplus(self):
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer {}'.format(self.token_employee_plus))

        response = self.client.get(
            '/atlas/typeahead/brk/',
            {'q': 'Stephan Preeker'})
        self.assertEqual(response.status_code, 200)
        self.assertIn("Stephan Jacob Preeker", str(response.data))

        response = self.client.get(
            '/atlas/typeahead/brk/',
            {'q': 'stoeptegel'})

        self.assertEqual(response.status_code, 200)

        self.assertIn("stoeptegel", str(response.data))

    def test_match_typeahead_subject_not_authorized(self):
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer {}'.format(self.token_default))

        response = self.client.get(
            '/atlas/typeahead/brk/',
            {'q': 'Stephan Preeker'})
        self.assertEqual(response.status_code, 200)
        self.assertNotIn("Stephan Jacob Preeker", str(response.data))

        response = self.client.get(
            '/atlas/typeahead/brk/', {'q': 'stoeptegel'})

        self.assertEqual(response.status_code, 200)
        self.assertNotIn("stoeptegel", str(response.data))

    def test_match_typeahead_subject_level_employee(self):
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer {}'.format(self.token_employee))

        response = self.client.get(
            '/atlas/typeahead/brk/', {'q': 'stoeptegel'})

        self.assertEqual(response.status_code, 200)
        self.assertIn("stoeptegel", str(response.data))
