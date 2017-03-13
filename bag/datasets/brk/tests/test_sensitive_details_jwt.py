import time

from django.contrib.auth.models import User, Permission
from django.contrib.contenttypes.models import ContentType

from authorization_django import levels as authorization_levels
from django.conf import settings
import jwt
from rest_framework_jwt.settings import api_settings
from rest_framework.test import APITestCase

from .. import models
from . import factories


class SensitiveDetailsJwtTestCase(APITestCase):

    def setUp(self):
        # OLD STYLE AUTH
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
        key = settings.DATAPUNT_AUTHZ['JWT_SECRET_KEY']
        algorithm = settings.DATAPUNT_AUTHZ['JWT_ALGORITHM']

        now = int(time.time())

        token_default = jwt.encode({
            'authz': authorization_levels.LEVEL_DEFAULT,
            'iat': now, 'exp': now + 600}, key, algorithm=algorithm)
        token_employee = jwt.encode({
            'authz': authorization_levels.LEVEL_EMPLOYEE,
            'iat': now, 'exp': now + 600}, key, algorithm=algorithm)
        token_employee_plus = jwt.encode({
            'authz': authorization_levels.LEVEL_EMPLOYEE_PLUS,
            'iat': now, 'exp': now + 600}, key, algorithm=algorithm)

        self.token_default = str(token_default, 'utf-8')
        self.token_employee = str(token_employee, 'utf-8')
        self.token_employee_plus = str(token_employee_plus, 'utf-8')

        sectie = factories.KadastraleSectieFactory(
            sectie='s'
        )

        amsterdam = factories.GemeenteFactory(
            gemeente='amsterdam',
        )

        kada_amsterdam = factories.KadastraleGemeenteFactory(
            pk='ACD00',
            gemeente=amsterdam
        )

        self.kot = factories.KadastraalObjectFactory.create(
            kadastrale_gemeente=kada_amsterdam,
            perceelnummer=10000,  # must be 5 long!
            indexletter='A',
            sectie=sectie,
        )

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

        self.not_public_fields = [
            'koopsom', 'koopjaar',
            'cultuurcode_onbebouwd',
            'cultuurcode_bebouwd',
            'rechten',
            'aantekeningen',

        ]

    def get_token(self, user):
        jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
        jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER

        payload = jwt_payload_handler(user)
        return jwt_encode_handler(payload)

    def test_niet_ingelogd_geen_details_in_natuurlijk_persoon_json(self):
        response = self.client.get('/brk/subject/{}/'.format(
            self.natuurlijk.pk)).data

        self.assertNotIn('rechten', response)
        self.assertNotIn('woonadres', response)
        self.assertNotIn('postadres', response)

    def test_niet_ingelogd_wel_details_in_niet_natuurlijk_persoon_json(self):
        response = self.client.get('/brk/subject/{}/'.format(
            self.niet_natuurlijk.pk)).data

        self.assertIn('rechten', response)
        self.assertIn('woonadres', response)
        self.assertIn('postadres', response)

    def test_ingelogd_niet_geautoriseerd_geen_details_in_natuurlijk_json(self):
        self.client.credentials(HTTP_AUTHORIZATION='JWT {}'.format(
            self.token_not_authorized))
        response = self.client.get('/brk/subject/{}/'.format(
            self.natuurlijk.pk)).data

        self.assertNotIn('rechten', response)
        self.assertNotIn('woonadres', response)
        self.assertNotIn('postadres', response)

    def test_ingelogd_niet_geautoriseerd_geen_details_in_natuurlijk(self):
        self.client.credentials(HTTP_AUTHORIZATION='JWT {}'.format(
            self.token_default))
        response = self.client.get('/brk/subject/{}/'.format(
            self.natuurlijk.pk)).data

        self.assertNotIn('rechten', response)
        self.assertNotIn('woonadres', response)
        self.assertNotIn('postadres', response)

    def test_ingelogd_geautoriseed_details_np_json(self):
        self.client.credentials(HTTP_AUTHORIZATION='JWT {}'.format(
            self.token_authorized))
        response = self.client.get('/brk/subject/{}/'.format(
            self.natuurlijk.pk)).data

        self.assertIn('rechten', response)
        self.assertIn('woonadres', response)
        self.assertIn('postadres', response)

    def test_ingelogd_wel_geautoriseed_wel_details_in_np_json_nieuw(self):
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer {}'.format(self.token_employee_plus))
        response = self.client.get('/brk/subject/{}/'.format(
            self.natuurlijk.pk)).data

        self.assertIn('rechten', response)
        self.assertIn('woonadres', response)
        self.assertIn('postadres', response)

    def test_ingelogd_zakelijk_recht_verwijst_naar_hoofd_view(self):
        self.client.credentials(
            HTTP_AUTHORIZATION='JWT {}'.format(self.token_authorized))
        response = self.client.get(
            '/brk/zakelijk-recht/{}/'.format(self.recht_natuurlijk.pk)).data

        subj = response['kadastraal_subject']
        self.assertEqual(
            subj['_links']['self']['href'],
            'http://testserver/brk/subject/{}/'.format(self.natuurlijk.pk)
        )

    def test_ingelogd_zakelijk_recht_verwijst_naar_hoofd_view_nieuw(self):
        self.client.credentials(
            HTTP_AUTHORIZATION='JWT {}'.format(self.token_employee_plus))
        response = self.client.get(
            '/brk/zakelijk-recht/{}/'.format(self.recht_natuurlijk.pk)).data

        subj = response['kadastraal_subject']
        self.assertEqual(
            subj['_links']['self']['href'],
            'http://testserver/brk/subject/{}/'.format(self.natuurlijk.pk)
        )

    def test_uitgelogd_zakelijk_recht_niet_natuurlijk_hoofd_view(self):

        response = self.client.get(
            '/brk/zakelijk-recht/{}/'.format(
                self.recht_niet_natuurlijk.pk)).data

        subj = response['kadastraal_subject']
        self.assertEqual(
            subj['_links']['self']['href'],
            'http://testserver/brk/subject/{}/'.format(self.niet_natuurlijk.pk)
        )

    def test_uitgelogd_zakelijk_recht_natuurlijk_subresource(self):
        response = self.client.get(
            '/brk/zakelijk-recht/{}/'.format(
                self.recht_natuurlijk.pk)).data

        subj = response['kadastraal_subject']
        self.assertEqual(
            subj['_links']['self']['href'],
            'http://testserver/brk/subject/{}/'.format(self.natuurlijk.pk)
        )

    def test_subresource_toon_persoonsgegevens_maar_geen_relaties(self):
        response = self.client.get(
            '/brk/zakelijk-recht/{}/subject/'.format(
                self.recht_natuurlijk.pk)).data

        self.assertIn('woonadres', response)
        self.assertIn('postadres', response)
        self.assertNotIn('rechten', response)

    def test_directional_name_subject(self):
        self.client.credentials(
            HTTP_AUTHORIZATION='JWT {}'.format(self.token_authorized))
        response = self.client.get(
            '/brk/zakelijk-recht/?kadastraal_object={}'.format(
                self.kot.pk)).data

        subj = response['results'][0]

        kad_nat_naam = self.recht_natuurlijk._kadastraal_subject_naam
        kad_nnat_naam = self.recht_niet_natuurlijk._kadastraal_subject_naam

        self.assertTrue(
            kad_nat_naam in subj['_display'] or
            kad_nnat_naam in subj['_display']
        )

    def test_directional_name_subject_nieuw(self):
        self.client.credentials(
            HTTP_AUTHORIZATION='JWT {}'.format(self.token_employee_plus))
        response = self.client.get(
            '/brk/zakelijk-recht/?kadastraal_object={}'.format(
                self.kot.pk)).data

        kad_nat_naam = self.recht_natuurlijk._kadastraal_subject_naam
        kad_nnat_naam = self.recht_niet_natuurlijk._kadastraal_subject_naam

        subj = response['results'][0]
        self.assertTrue(
            kad_nat_naam in subj['_display'] or
            kad_nnat_naam in subj['_display']
        )

    def test_directional_name_object(self):
        self.client.credentials(
            HTTP_AUTHORIZATION='JWT {}'.format(self.token_authorized))

        response = self.client.get(
            '/brk/zakelijk-recht/?kadastraal_subject={}'.format(
                self.niet_natuurlijk.pk)).data

        obj = response['results'][0]
        self.assertTrue(self.kot.aanduiding in obj['_display'])

    def test_directional_name_object_nieuw(self):
        self.client.credentials(
            HTTP_AUTHORIZATION='JWT {}'.format(self.token_employee_plus))
        response = self.client.get(
            '/brk/zakelijk-recht/?kadastraal_subject={}'.format(
                self.niet_natuurlijk.pk)).data

        obj = response['results'][0]
        self.assertTrue(self.kot.aanduiding in obj['_display'])

    def test_match_kot_object_authorized(self):
        self.client.credentials(
            HTTP_AUTHORIZATION='JWT {}'.format(self.token_employee))

        response = self.client.get(f'/brk/object/{self.kot.pk}/')

        self.assertEqual(response.status_code, 200)
        self.assertIn("ACD00", str(response.data))

        data = str(response.data)

        # check if authorized fields are in response
        for field in self.not_public_fields:
            self.assertIn(field, data)

    def test_match_kot_object_public(self):
        response = self.client.get(f'/brk/object/{self.kot.pk}/')

        self.assertEqual(response.status_code, 200)
        self.assertIn("ACD00", str(response.data))

        data = str(response.data)

        # check if authorized fields are *NOT* in response
        for field in self.not_public_fields:
            self.assertNotIn(field, data)

    def test_match_kot_object_expand_authorized(self):
        self.client.credentials(
            HTTP_AUTHORIZATION='JWT {}'.format(self.token_employee))

        response = self.client.get(f'/brk/object-expand/{self.kot.pk}/')

        self.assertEqual(response.status_code, 200)
        self.assertIn("ACD00", str(response.data))

        data = str(response.data)

        # check if authorized fields are in response
        for field in self.not_public_fields:
            self.assertIn(field, data)

    def test_match_kot_object__expandpublic(self):
        response = self.client.get(f'/brk/object-expand/{self.kot.pk}/')

        self.assertEqual(response.status_code, 200)
        self.assertIn("ACD00", str(response.data))

        data = str(response.data)

        # check if authorized fields are *NOT* in response
        for field in self.not_public_fields:
            self.assertNotIn(field, data)
