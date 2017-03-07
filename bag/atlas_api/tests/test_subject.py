import time
import jwt

from django.contrib.auth.models import User, Permission
from django.contrib.contenttypes.models import ContentType

from django.conf import settings

from rest_framework.test import APITestCase

from rest_framework_jwt.settings import api_settings

from authorization_django import levels as authorization_levels

from batch import batch
import datasets.bag.batch
import datasets.brk.batch
from datasets.brk.tests import factories as brk_factories


from datasets.brk import models


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

    def setUp(self):

        permission = Permission.objects.get(
            content_type=ContentType.objects.get_for_model(
                models.KadastraalSubject),
            codename='view_sensitive_details'
        )

        self.not_authorized = User.objects.create_user(
            username='not_authorized', password='pass')
        self.authorized = User.objects.create_user(
            username='authorized', password='pass')

        self.authorized.user_permissions.add(permission)
        self.token_authorized = self.get_token(self.authorized)
        self.token_not_authorized = self.get_token(self.not_authorized)

        # NEW STYLE AUTH
        key, algorithm = settings.JWT_SECRET_KEY, settings.JWT_ALGORITHM

        now = int(time.time())

        token_default = jwt.encode({
            'authz': authorization_levels.LEVEL_DEFAULT,
            'iat': now, 'exp': now+600}, key, algorithm=algorithm)
        token_employee = jwt.encode({
            'authz': authorization_levels.LEVEL_EMPLOYEE,
            'iat': now, 'exp': now+600}, key, algorithm=algorithm)
        token_employee_plus = jwt.encode({
            'authz': authorization_levels.LEVEL_EMPLOYEE_PLUS,
            'iat': now, 'exp': now+600}, key, algorithm=algorithm)

        self.token_default = str(token_default, 'utf-8')
        self.token_employee = str(token_employee, 'utf-8')
        self.token_employee_plus = str(token_employee_plus, 'utf-8')

    def get_token(self, user):
        jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
        jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER

        payload = jwt_payload_handler(user)
        return jwt_encode_handler(payload)

    def test_match_subject(self):
        self.client.credentials(
            HTTP_AUTHORIZATION=f'JWT {self.token_authorized}')

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
        self.client.credentials(
            HTTP_AUTHORIZATION='JWT {}'.format(self.token_authorized))

        response = self.client.get(
            '/atlas/search/kadastraalsubject/',
            {'q': 'Stephan Preeker'})
        self.assertEqual(response.status_code, 200)
        self.assertIn("Stephan Jacob Preeker", str(response.data))

    def test_match_subject2_not_authorizer(self):
        self.client.credentials(
            HTTP_AUTHORIZATION='JWT {}'.format(self.token_not_authorized))

        response = self.client.get(
            '/atlas/search/kadastraalsubject/',
            {'q': 'Stephan Preeker'})
        self.assertEqual(response.status_code, 200)
        self.assertNotIn("Stephan Jacob Preeker", str(response.data))

    def test_match_subject_not_authorized(self):
        self.client.credentials(
            HTTP_AUTHORIZATION='JWT {}'.format(self.token_not_authorized))

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
