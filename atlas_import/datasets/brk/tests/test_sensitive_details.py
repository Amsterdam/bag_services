from unittest import skip
from django.contrib.auth.models import User, Permission

from rest_framework.test import APITestCase

from datasets.brk.tests import factories


class SensitiveDetailsTestCase(APITestCase):
    def setUp(self):
        self.not_authorized = User.objects.create_user(username='not_authorized', password='pass')
        self.authorized = User.objects.create_user(username='authorized', password='pass')
        self.authorized.user_permissions.add(Permission.objects.get(codename='view_sensitive_details'))

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
        response = self.client.get('/api/brk/subject/{}/'.format(self.natuurlijk.pk)).data

        self.assertNotIn('rechten', response)
        self.assertNotIn('woonadres', response)
        self.assertNotIn('postadres', response)

    def test_niet_ingelogd_wel_details_in_niet_natuurlijk_persoon_json(self):
        response = self.client.get('/api/brk/subject/{}/'.format(self.niet_natuurlijk.pk)).data

        self.assertIsNotNone(response['rechten'])
        self.assertIsNotNone(response['woonadres'])
        self.assertIsNotNone(response['postadres'])

    def test_ingelogd_niet_geautoriseerd_geen_details_in_natuurlijk_json(self):
        self.client.login(username='not_authorized', password='pass')
        response = self.client.get('/api/brk/subject/{}/'.format(self.natuurlijk.pk)).data

        self.assertNotIn('rechten', response)
        self.assertNotIn('woonadres', response)
        self.assertNotIn('postadres', response)

    def test_ingelogd_wel_geautoriseed_wel_details_in_natuurlijk_persoon_json(self):
        self.client.login(username='authorized', password='pass')
        response = self.client.get('/api/brk/subject/{}/'.format(self.natuurlijk.pk)).data

        self.assertIsNotNone(response['rechten'])
        self.assertIsNotNone(response['woonadres'])
        self.assertIsNotNone(response['postadres'])

    def test_ingelogd_zakelijk_recht_verwijst_naar_hoofd_view(self):
        self.client.login(username='authorized', password='pass')
        response = self.client.get('/api/brk/zakelijk-recht/{}/'.format(self.recht_natuurlijk.pk)).data

        subj = response['kadastraal_subject']
        self.assertEqual(
            subj['_links']['self']['href'],
            'http://testserver/api/brk/subject/{}/'.format(self.natuurlijk.pk)
        )

    def test_uitgelogd_zakelijk_recht_niet_natuurlijk_verwijst_naar_hoofd_view(self):
        response = self.client.get('/api/brk/zakelijk-recht/{}/'.format(self.recht_niet_natuurlijk.pk)).data

        subj = response['kadastraal_subject']
        self.assertEqual(
            subj['_links']['self']['href'],
            'http://testserver/api/brk/subject/{}/'.format(self.niet_natuurlijk.pk)
        )

    def test_uitgelogd_zakelijk_recht_natuurlijk_verwijst_naar_subresource(self):
        response = self.client.get('/api/brk/zakelijk-recht/{}/'.format(self.recht_natuurlijk.pk)).data

        subj = response['kadastraal_subject']
        self.assertEqual(
            subj,
            'http://testserver/api/brk/zakelijk-recht/{}/subject/'.format(self.recht_natuurlijk.pk)
        )

    def test_subresource_toon_persoonsgegevens_maar_geen_relaties(self):
        response = self.client.get('/api/brk/zakelijk-recht/{}/subject/'.format(self.recht_natuurlijk.pk)).data

        self.assertIsNotNone(response['woonadres'])
        self.assertIsNotNone(response['postadres'])
        self.assertNotIn('rechten', response)
