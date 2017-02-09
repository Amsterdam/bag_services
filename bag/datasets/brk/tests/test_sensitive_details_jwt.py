import time
import authorization_levels
from django.conf import settings

import jwt
from rest_framework.test import APITestCase

from . import factories


class SensitiveDetailsJwtTestCase(APITestCase):
    def setUp(self):

        key, algorithm = settings.JWT_SECRET_KEY, settings.JWT_ALGORITHM

        now = int(time.time())

        token_default = jwt.encode(
            {'authz': authorization_levels.LEVEL_DEFAULT, 'iat': now, 'exp': now+600}, key, algorithm=algorithm)
        token_employee = jwt.encode(
            {'authz': authorization_levels.LEVEL_EMPLOYEE, 'iat': now, 'exp': now+600}, key, algorithm=algorithm)
        token_employee_plus = jwt.encode(
            {'authz': authorization_levels.LEVEL_EMPLOYEE_PLUS, 'iat': now, 'exp': now+600}, key, algorithm=algorithm)

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
        self.client.credentials(HTTP_AUTHORIZATION='JWT {}'.format(self.token_default))
        response = self.client.get('/brk/subject/{}/'.format(self.natuurlijk.pk)).data

        self.assertNotIn('rechten', response)
        self.assertNotIn('woonadres', response)
        self.assertNotIn('postadres', response)

    def test_ingelogd_wel_geautoriseed_wel_details_in_natuurlijk_persoon_json(self):
        self.client.credentials(HTTP_AUTHORIZATION='JWT {}'.format(self.token_employee_plus))
        response = self.client.get('/brk/subject/{}/'.format(self.natuurlijk.pk)).data

        self.assertIsNotNone(response['rechten'])
        self.assertIsNotNone(response['woonadres'])
        self.assertIsNotNone(response['postadres'])

    def test_ingelogd_zakelijk_recht_verwijst_naar_hoofd_view(self):
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
        self.client.credentials(HTTP_AUTHORIZATION='JWT {}'.format(self.token_employee_plus))
        response = self.client.get('/brk/zakelijk-recht/?kadastraal_object={}'.format(self.kot.pk)).data

        subj = response['results'][0]
        self.assertTrue(
            self.recht_natuurlijk._kadastraal_subject_naam in subj['_display'] or
            self.recht_niet_natuurlijk._kadastraal_subject_naam in subj['_display']
        )

    def test_directional_name_object(self):
        self.client.credentials(HTTP_AUTHORIZATION='JWT {}'.format(self.token_employee_plus))
        response = self.client.get('/brk/zakelijk-recht/?kadastraal_subject={}'.format(self.niet_natuurlijk.pk)).data

        obj = response['results'][0]
        self.assertTrue(self.kot.aanduiding in obj['_display'])

