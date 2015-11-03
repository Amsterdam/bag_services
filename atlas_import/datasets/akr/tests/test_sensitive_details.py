import json
from django.contrib.auth.models import User, Permission

from django.test import TestCase
from rest_framework.test import APITestCase

from datasets.akr.tests import factories


class SensitiveDetailsTestCase(APITestCase):
    def setUp(self):
        self.not_authorized = User.objects.create_user(username='not_authorized', password='pass')
        self.authorized = User.objects.create_user(username='authorized', password='pass')
        self.authorized.user_permissions.add(Permission.objects.get(codename='view_sensitive_details'))

        self.kot = factories.KadastraalObjectFactory.create()
        self.natuurlijk = factories.NatuurlijkPersoonFactory.create()
        self.niet_natuurlijk = factories.NietNatuurlijkPersoonFactory.create()
        self.transactie = factories.TransactieFactory.create()

        self.natuurlijk_recht = factories.ZakelijkRechtFactory.create(
            kadastraal_subject=self.natuurlijk,
            kadastraal_object=self.kot,
            transactie=self.transactie,
        )

        self.niet_natuurlijk_recht = factories.ZakelijkRechtFactory.create(
            kadastraal_subject=self.niet_natuurlijk,
            kadastraal_object=self.kot,
            transactie=self.transactie,
        )

    def test_niet_ingelogd_geen_details_in_natuurlijk_persoon_json(self):
        response = self.client.get('/api/kadaster/subject/{}.json'.format(self.natuurlijk.pk)).data
        self.assertIsNone(response['rechten'])
        self.assertIsNone(response['woonadres'])
        self.assertIsNone(response['postadres'])

    def test_niet_ingelogd_wel_details_in_niet_natuurlijk_persoon_json(self):
        response = self.client.get('/api/kadaster/subject/{}.json'.format(self.niet_natuurlijk.pk)).data

        self.assertIsNotNone(response['rechten'])
        self.assertIsNotNone(response['woonadres'])
        self.assertIsNotNone(response['postadres'])

    def test_ingelogd_niet_geautoriseerd_geen_details_in_natuurlijk_json(self):
        self.client.login(username='not_authorized', password='pass')
        response = self.client.get('/api/kadaster/subject/{}.json'.format(self.natuurlijk.pk)).data

        self.assertIsNone(response['rechten'])
        self.assertIsNone(response['woonadres'])
        self.assertIsNone(response['postadres'])

    def test_ingelogd_wel_geautoriseed_wel_details_in_natuurlijk_persoon_json(self):
        self.client.login(username='authorized', password='pass')
        response = self.client.get('/api/kadaster/subject/{}.json'.format(self.natuurlijk.pk)).data

        self.assertIsNotNone(response['rechten'])
        self.assertIsNotNone(response['woonadres'])
        self.assertIsNotNone(response['postadres'])

