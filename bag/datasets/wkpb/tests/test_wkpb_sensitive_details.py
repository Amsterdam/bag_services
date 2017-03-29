from datasets.wkpb.tests import factories

from datasets.generic.tests.authorization import AuthorizationSetup

from rest_framework.test import APITestCase


class ImportBeperkingVerblijfsobjectTaskTest(APITestCase, AuthorizationSetup):

    def setUp(self):

        self.brondocument = factories.BrondocumentFactory.create(
            documentnaam='i.am.a.secrect.pdf')

        self.setUpAuthorization()

    def test_match_brondocument_public(self):
        doc_id = self.brondocument.id
        response = self.client.get(f'/wkpb/brondocument/{doc_id}/')

        self.assertEqual(response.status_code, 200)
        data = str(response.data)

        self.assertIn(str(doc_id), data)
        # check if authorized fields are *NOT* in response
        self.assertNotIn('url', data)

    def test_employee_brondocument(self):
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer {}'.format(self.token_employee))

        doc_id = self.brondocument.id
        response = self.client.get(f'/wkpb/brondocument/{doc_id}/')

        data = str(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertIn(str(doc_id), data)

        # check if authorized fields are *IN* in response
        self.assertIn('url', data)

    def test_match_brondocument_public_list(self):
        doc_id = self.brondocument.id
        response = self.client.get(f'/wkpb/brondocument/')

        self.assertEqual(response.status_code, 200)

        data = response.data

        results = str(data['results'][0])

        self.assertIn(str(doc_id), results)
        # check if authorized fields are *NOT* in response
        self.assertNotIn('url', data)

    def test_employee_brondocument_list(self):
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer {}'.format(self.token_employee))

        doc_id = self.brondocument.id
        response = self.client.get(f'/wkpb/brondocument/')

        data = response.data

        results = str(data['results'][0])

        self.assertEqual(response.status_code, 200)
        self.assertIn(str(doc_id), results)

        # check if authorized fields are *IN* in response
        self.assertIn('url', results)
