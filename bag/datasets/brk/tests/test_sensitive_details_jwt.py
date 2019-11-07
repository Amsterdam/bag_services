"""
Test sensitive detauls Kadaster.  personen en eigendommen
worden niet meer gevonden zonder in te loggen.
"""

from rest_framework.test import APITestCase

from datasets.generic.tests.authorization import AuthorizationSetup
from . import factories


class SensitiveDetailsJwtTestCase(APITestCase, AuthorizationSetup):
    
    brk_root_url = '/brk'

    def setUp(self):

        # NEW STYLe AUTH
        self.setUpAuthorization()

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

    def test_ingelogd_wel_geautoriseed_wel_details_in_np_json_nieuw(self):
        for token in (self.token_employee_plus, self.token_scope_brk_rsn):
            self.client.credentials(
                HTTP_AUTHORIZATION='Bearer {}'.format(token))
            response = self.client.get(self.brk_root_url+'/subject/{}/'.format(
                self.natuurlijk.pk)).data

            self.assertIn('rechten', response)
            self.assertIn('woonadres', response)
            self.assertIn('postadres', response)

    def test_ingelogd_zakelijk_recht_verwijst_naar_hoofd_view_nieuw(self):
        for token in (self.token_employee_plus, self.token_scope_brk_rsn):
            self.client.credentials(
                HTTP_AUTHORIZATION='Bearer {}'.format(token))
            response = self.client.get(
                self.brk_root_url+'/zakelijk-recht/{}/'.format(self.recht_natuurlijk.pk)).data

            subj = response['kadastraal_subject']
            self.assertEqual(
                subj['_links']['self']['href'],
                'http://testserver/brk/subject/{}/'.format(self.natuurlijk.pk)
            )

    def test_uitgelogd_zakelijk_recht_niet_natuurlijk_hoofd_view(self):

        response = self.client.get(
            self.brk_root_url+'/zakelijk-recht/{}/'.format(
                self.recht_niet_natuurlijk.pk))

        self.assertEqual(response.status_code, 401)

    def test_uitgelogd_zakelijk_recht_natuurlijk_subresource(self):

        response = self.client.get(
            self.brk_root_url+'/zakelijk-recht/{}/'.format(
                self.recht_natuurlijk.pk))

        self.assertEqual(response.status_code, 401)

    def test_subresource_toon_persoonsgegevens_maar_geen_relaties(self):

        for token in (self.token_employee_plus, self.token_scope_brk_rsn):
            self.client.credentials(
                HTTP_AUTHORIZATION='Bearer {}'.format(token))

            response = self.client.get(
                self.brk_root_url+'/zakelijk-recht/{}/subject/'.format(
                    self.recht_natuurlijk.pk))

            data = response.data

            self.assertIn('woonadres', data)
            self.assertIn('postadres', data)

            self.assertNotIn('rechten', data)

    def test_directional_name_subject_nieuw(self):
        for token in (self.token_employee_plus, self.token_scope_brk_ro):
            self.client.credentials(
                HTTP_AUTHORIZATION='Bearer {}'.format(token))
            response = self.client.get(
                self.brk_root_url+'/zakelijk-recht/?kadastraal_object={}'.format(
                    self.kot.pk)).data

            kad_nat_naam = self.recht_natuurlijk._kadastraal_subject_naam
            kad_nnat_naam = self.recht_niet_natuurlijk._kadastraal_subject_naam

            subj = response['results'][0]
            self.assertTrue(
                kad_nat_naam in subj['_display'] or
                kad_nnat_naam in subj['_display']
            )

    def test_directional_name_object_nieuw(self):
        for token in (self.token_employee_plus, self.token_scope_brk_rsn):
            self.client.credentials(
                HTTP_AUTHORIZATION='Bearer {}'.format(token))
            response = self.client.get(
                self.brk_root_url+'/zakelijk-recht/?kadastraal_subject={}'.format(
                    self.niet_natuurlijk.pk)).data

            obj = response['results'][0]
            self.assertTrue(self.kot.aanduiding in obj['_display'])

    def test_match_kot_object_authorized(self):
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer {}'.format(self.token_scope_brk_ro))

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
            HTTP_AUTHORIZATION='Bearer {}'.format(self.token_scope_brk_ro))

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

    def test_match_kot_object_wkpb_authorized(self):
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer {}'.format(self.token_scope_wkpd_rdbu))

        response = self.client.get(f'/brk/object-wkpb/{self.kot.pk}/')

        self.assertEqual(response.status_code, 200)
        self.assertIn("ACD00", str(response.data))

        data = str(response.data)

        # check if authorized fields are in response
        for field in self.not_public_fields:
            self.assertIn(field, data)

    def test_match_kot_object__wkpb_public(self):
        response = self.client.get(f'/brk/object-wkpb/{self.kot.pk}/')

        self.assertEqual(response.status_code, 200)
        self.assertIn("ACD00", str(response.data))

        data = str(response.data)

        # check if authorized fields are *NOT* in response
        for field in self.not_public_fields:
            self.assertNotIn(field, data)

    def test_niet_ingelogd_ziet_geen_niet_natuurlijk_persoon_json(self):
        response = self.client.get(self.brk_root_url+'/subject/{}/'.format(
            self.niet_natuurlijk.pk))

        self.assertEqual(response.status_code, 401)

        self.client.credentials(
            HTTP_AUTHORIZATION=f'Bearer {self.token_default}')

        response = self.client.get(self.brk_root_url+'/subject/{}/'.format(
            self.niet_natuurlijk.pk))

        self.assertEqual(response.status_code, 401)

    def test_niet_geautoriseerd_krijgt_geen_natuurlijk_persoon(self):
        response = self.client.get(self.brk_root_url+'/subject/{}/'.format(
            self.natuurlijk.pk))
        self.assertEqual(response.status_code, 401)

        self.client.credentials(
            HTTP_AUTHORIZATION=f'Bearer {self.token_default}')

        response = self.client.get(self.brk_root_url+'/subject/{}/'.format(
            self.natuurlijk.pk))
        self.assertEqual(response.status_code, 401)

    def test_niet_geautoriseerd_natuurlijk_persoon_zonder_rechten(self):
        response = self.client.get(self.brk_root_url+'/subject/{}/'.format(
            self.natuurlijk.pk))

        self.assertEqual(response.status_code, 401)

        self.client.credentials(
            HTTP_AUTHORIZATION=f'Bearer {self.token_scope_brk_rs}')

        response = self.client.get(self.brk_root_url+'/subject/{}/'.format(
            self.natuurlijk.pk))
        self.assertEqual(response.status_code, 200)

        self.assertNotIn('rechten', str(response.data))
