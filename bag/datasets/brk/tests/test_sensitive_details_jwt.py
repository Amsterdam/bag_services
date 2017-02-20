import time
from unittest import mock

from django.contrib.auth.models import User, Permission
from django.contrib.contenttypes.models import ContentType

from authorization_django import levels as authorization_levels
from django.test import override_settings
import jwt
from rest_framework.test import APITestCase

from .. import models
from . import factories


class SensitiveDetailsJwtTestCase(APITestCase):

    def setUp(self):
        from django.conf import settings
        # OLD STYLE AUTH
        permission = Permission.objects.get(
            content_type=ContentType.objects.get_for_model(models.KadastraalSubject),
            codename='view_sensitive_details'
        )

        self.not_authorized = User.objects.create_user(username='not_authorized', password='pass')
        self.authorized = User.objects.create_user(username='authorized', password='pass')
        self.authorized.user_permissions.add(permission)
        self.token_authorized = self.get_token(self.authorized)
        self.token_not_authorized = self.get_token(self.not_authorized)

        # NEW STYLE AUTH
        key, algorithm = settings.JWT_SECRET_KEY, settings.JWT_ALGORITHM

        now = int(time.time())

        token_default = jwt.encode(
            {'authz': authorization_levels.LEVEL_DEFAULT, 'iat': now, 'exp': now+600, 'username': 'anonymous'}, key, algorithm=algorithm)
        token_employee = jwt.encode(
            {'authz': authorization_levels.LEVEL_EMPLOYEE, 'iat': now, 'exp': now+600, 'username': 'anonymous'}, key, algorithm=algorithm)
        token_employee_plus = jwt.encode(
            {'authz': authorization_levels.LEVEL_EMPLOYEE_PLUS, 'iat': now, 'exp': now+600, 'username': 'anonymous'}, key, algorithm=algorithm)

        self.token_default = str(token_default, 'utf-8')
        self.token_employee = str(token_employee, 'utf-8')
        self.token_employee_plus = str(token_employee_plus, 'utf-8')

        self.kot = factories.KadastraalObjectFactory.create()
        self.natuurlijk = factories.NatuurlijkPersoonFactory.create()
        self.niet_natuurlijk = factories.NietNatuurlijkPersoonFactory.create()

        self.recht_natuurlijk = factories.ZakelijkRechtFactory.create(
            kadastraal_object=self.kot,
            kadastraal_subject=self.natuurlijk
        )

        self.recht_niet_natuurlijk = factories.ZakelijkRechtFactory.create(
            kadastraal_object=self.kot,
            kadastraal_subject=self.niet_natuurlijk
        )

    def get_token(self, user):
        from rest_framework_jwt.settings import api_settings
        jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
        jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER

        payload = jwt_payload_handler(user)
        return jwt_encode_handler(payload)

    def test_niet_ingelogd_geen_details_in_natuurlijk_persoon_json(self):
        response = self.client.get('/brk/subject/{}/'.format(self.natuurlijk.pk)).data

        self.assertNotIn('rechten', response)
        self.assertNotIn('woonadres', response)
        self.assertNotIn('postadres', response)

    def test_niet_ingelogd_wel_details_in_niet_natuurlijk_persoon_json(self):
        response = self.client.get('/brk/subject/{}/'.format(self.niet_natuurlijk.pk)).data

        self.assertIn('rechten', response)
        self.assertIn('woonadres', response)
        self.assertIn('postadres', response)

    def test_ingelogd_niet_geautoriseerd_geen_details_in_natuurlijk_json(self):
        self.client.credentials(HTTP_AUTHORIZATION='JWT {}'.format(self.token_not_authorized))
        response = self.client.get('/brk/subject/{}/'.format(self.natuurlijk.pk)).data

        self.assertNotIn('rechten', response)
        self.assertNotIn('woonadres', response)
        self.assertNotIn('postadres', response)

    def test_ingelogd_niet_geautoriseerd_geen_details_in_natuurlijk_json_nieuw(self):
        self.client.credentials(HTTP_AUTHORIZATION='JWT {}'.format(self.token_default))
        response = self.client.get('/brk/subject/{}/'.format(self.natuurlijk.pk)).data

        self.assertNotIn('rechten', response)
        self.assertNotIn('woonadres', response)
        self.assertNotIn('postadres', response)

    def test_ingelogd_wel_geautoriseed_wel_details_in_natuurlijk_persoon_json(self):
        self.client.credentials(HTTP_AUTHORIZATION='JWT {}'.format(self.token_authorized))
        response = self.client.get('/brk/subject/{}/'.format(self.natuurlijk.pk)).data

        self.assertIsNotNone(response['rechten'])
        self.assertIsNotNone(response['woonadres'])
        self.assertIsNotNone(response['postadres'])

    def test_ingelogd_wel_geautoriseed_wel_details_in_natuurlijk_persoon_json_nieuw(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(self.token_employee_plus))
        response = self.client.get('/brk/subject/{}/'.format(self.natuurlijk.pk)).data

        self.assertIsNotNone(response['rechten'])
        self.assertIsNotNone(response['woonadres'])
        self.assertIsNotNone(response['postadres'])

    def test_ingelogd_zakelijk_recht_verwijst_naar_hoofd_view(self):
        self.client.credentials(HTTP_AUTHORIZATION='JWT {}'.format(self.token_authorized))
        response = self.client.get('/brk/zakelijk-recht/{}/'.format(self.recht_natuurlijk.pk)).data

        subj = response['kadastraal_subject']
        self.assertEqual(
            subj['_links']['self']['href'],
            'http://testserver/brk/subject/{}/'.format(self.natuurlijk.pk)
        )

    def test_ingelogd_zakelijk_recht_verwijst_naar_hoofd_view_nieuw(self):
        self.client.credentials(HTTP_AUTHORIZATION='JWT {}'.format(self.token_employee_plus))
        response = self.client.get('/brk/zakelijk-recht/{}/'.format(self.recht_natuurlijk.pk)).data

        subj = response['kadastraal_subject']
        self.assertEqual(
            subj['_links']['self']['href'],
            'http://testserver/brk/subject/{}/'.format(self.natuurlijk.pk)
        )

    def test_uitgelogd_zakelijk_recht_niet_natuurlijk_verwijst_naar_hoofd_view(self):
        response = self.client.get('/brk/zakelijk-recht/{}/'.format(self.recht_niet_natuurlijk.pk)).data

        subj = response['kadastraal_subject']
        self.assertEqual(
            subj['_links']['self']['href'],
            'http://testserver/brk/subject/{}/'.format(self.niet_natuurlijk.pk)
        )

    def test_uitgelogd_zakelijk_recht_natuurlijk_verwijst_naar_subresource(self):
        response = self.client.get('/brk/zakelijk-recht/{}/'.format(self.recht_natuurlijk.pk)).data

        subj = response['kadastraal_subject']
        self.assertEqual(
            subj['_links']['self']['href'],
            'http://testserver/brk/subject/{}/'.format(self.natuurlijk.pk)
        )

    def test_subresource_toon_persoonsgegevens_maar_geen_relaties(self):
        response = self.client.get('/brk/zakelijk-recht/{}/subject/'.format(self.recht_natuurlijk.pk)).data

        self.assertIsNotNone(response['woonadres'])
        self.assertIsNotNone(response['postadres'])
        self.assertNotIn('rechten', response)

    def test_directional_name_subject(self):
        self.client.credentials(HTTP_AUTHORIZATION='JWT {}'.format(self.token_authorized))
        response = self.client.get('/brk/zakelijk-recht/?kadastraal_object={}'.format(self.kot.pk)).data

        subj = response['results'][0]
        self.assertTrue(
            self.recht_natuurlijk._kadastraal_subject_naam in subj['_display'] or
            self.recht_niet_natuurlijk._kadastraal_subject_naam in subj['_display']
        )

    def test_directional_name_subject_nieuw(self):
        self.client.credentials(HTTP_AUTHORIZATION='JWT {}'.format(self.token_employee_plus))
        response = self.client.get('/brk/zakelijk-recht/?kadastraal_object={}'.format(self.kot.pk)).data

        subj = response['results'][0]
        self.assertTrue(
            self.recht_natuurlijk._kadastraal_subject_naam in subj['_display'] or
            self.recht_niet_natuurlijk._kadastraal_subject_naam in subj['_display']
        )

    def test_directional_name_object(self):
        self.client.credentials(HTTP_AUTHORIZATION='JWT {}'.format(self.token_authorized))
        response = self.client.get('/brk/zakelijk-recht/?kadastraal_subject={}'.format(self.niet_natuurlijk.pk)).data

        obj = response['results'][0]
        self.assertTrue(self.kot.aanduiding in obj['_display'])

    def test_directional_name_object_nieuw(self):
        self.client.credentials(HTTP_AUTHORIZATION='JWT {}'.format(self.token_employee_plus))
        response = self.client.get('/brk/zakelijk-recht/?kadastraal_subject={}'.format(self.niet_natuurlijk.pk)).data

        obj = response['results'][0]
        self.assertTrue(self.kot.aanduiding in obj['_display'])

