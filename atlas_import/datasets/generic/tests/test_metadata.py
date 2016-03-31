import os

from django.conf import settings
from django.test import TestCase

from datasets.generic import metadata


class MetadataTest(TestCase, metadata.UpdateDatasetMixin):
    diva = None

    def setUp(self):
        self.diva = settings.DIVA_DIR
        if not os.path.exists(self.diva):
            raise ValueError("DIVA_DIR not found: {}".format(self.diva))

        self.set_hostname()

        if '-acc' in self.import_hostname:
            self.dataset_id = 'test-acc'
        else:
            self.dataset_id = 'test-prod'

    def testUriAcc(self):
        self.set_hostname('ap01-acc.datapunt.amsterdam.nl')

        self.assertEqual(self.uri, 'https://api-acc.datapunt.amsterdam.nl/metadata/')

    def testUriProd(self):
        self.set_hostname('ap01.datapunt.amsterdam.nl')

        self.assertEqual(self.uri, 'https://api.datapunt.amsterdam.nl/metadata/')

    def testNoDate(self):
        response = self.update_metadata_date(None)
        self.assertEqual(response, None)

    def testOneDateAcc(self):
        self.dataset_id = 'test-acc'
        self.path = os.path.join(self.diva, 'brk')

        response = self.update_metadata_onedate(self.path, 'BRK_zakelijk_recht', 'ap01-acc.datapunt.amsterdam.nl')

        self.assertNotEqual(response, None)
        self.assertEqual(response.status_code, 200)

    def testOneDateProd(self):
        self.dataset_id = 'test-prod'
        self.path = os.path.join(self.diva, 'brk')

        response = self.update_metadata_onedate(self.path, 'BRK_zakelijk_recht', 'ap01.datapunt.amsterdam.nl')

        self.assertNotEqual(response, None)
        self.assertEqual(response.status_code, 200)

    def testUv2Acc(self):
        self.dataset_id = 'test-acc'
        self.path = os.path.join(self.diva, 'gebieden')

        response = self.update_metadata_uva2(self.path, 'BBK', 'ap01-acc.datapunt.amsterdam.nl')

        self.assertNotEqual(response, None)
        self.assertEqual(response.status_code, 200)

    def testUva2Prod(self):
        self.dataset_id = 'test-prod'
        self.path = os.path.join(self.diva, 'gebieden')

        response = self.update_metadata_uva2(self.path, 'BBK', 'ap01.datapunt.amsterdam.nl')

        self.assertNotEqual(response, None)
        self.assertEqual(response.status_code, 200)
