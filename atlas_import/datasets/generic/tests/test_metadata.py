import os
import datetime
import socket

from django.test import TestCase
from datasets.generic import metadata


class MetadataTest(TestCase, metadata.UpdateDatasetMixin):
    diva = None
    host_name = 'localhost'
    backup_method = socket.gethostname

    def setUp(self):
        self.diva = 'diva/'

        if '-acc' in socket.gethostname():
            self.dataset_id = 'test-acc'
        else:
            self.dataset_id = 'test-prod'

        socket.gethostname = self.mockhostname

    def tearDown(self):
        socket.gethostname = self.backup_method

    def mockhostname(self):
        return self.host_name

    def testUriAcc(self):
        self.host_name = 'ap01-acc.datapunt.amsterdam.nl'
        self.assertEqual(self.uri, 'https://api-acc.datapunt.amsterdam.nl/metadata/')

    def testAmsterdamDomainDefaulting(self):
        self.host_name = 'xxx.amsterdam.nl'
        self.assertEqual(self.uri, 'https://api.datapunt.amsterdam.nl/metadata/')

    def testOtherDomainsDontCallUpdateMetadata(self):
        self.host_name = 'my_machine.nl'
        response = self.update_metadata_date(datetime.datetime.now())
        self.assertEqual(response, None)

    def testUriProd(self):
        self.host_name = 'ap01.datapunt.amsterdam.nl'
        self.assertEqual(self.uri, 'https://api.datapunt.amsterdam.nl/metadata/')

    def testNoDate(self):
        response = self.update_metadata_date(None)
        self.assertEqual(response, None)

    def testNonExisting(self):
        self.dataset_id = 'test-aac'
        self.path = os.path.join(self.diva, 'brk')
        self.host_name = 'ap01-acc.datapunt.amsterdam.nl'

        response = self.update_metadata_onedate(self.path, 'BRK_zakelijk_recht')

        self.assertEqual(response.status_code, 404)

    def testUpperCase(self):
        self.dataset_id = 'TEST-ACC'
        self.path = os.path.join(self.diva, 'brk')
        self.host_name = 'ap01-acc.datapunt.amsterdam.nl'

        response = self.update_metadata_onedate(self.path, 'BRK_zakelijk_recht')

        self.assertEqual(response.status_code, 200)

    def testOneDateAcc(self):
        self.dataset_id = 'test-acc'
        self.path = os.path.join(self.diva, 'brk')
        self.host_name = 'ap01-acc.datapunt.amsterdam.nl'

        response = self.update_metadata_onedate(self.path, 'BRK_zakelijk_recht')

        self.assertNotEqual(response, None)
        self.assertEqual(response.status_code, 200)

    def testOneDateProd(self):
        self.dataset_id = 'test-prod'
        self.path = os.path.join(self.diva, 'brk')
        self.host_name = 'ap01.datapunt.amsterdam.nl'

        response = self.update_metadata_onedate(self.path, 'BRK_zakelijk_recht')

        self.assertNotEqual(response, None)
        self.assertEqual(response.status_code, 200)

    def testUva2Acc(self):
        self.dataset_id = 'test-acc'
        self.path = os.path.join(self.diva, 'gebieden')
        self.host_name = 'ap01-acc.datapunt.amsterdam.nl'

        response = self.update_metadata_uva2(self.path, 'BBK')

        self.assertNotEqual(response, None)
        self.assertEqual(response.status_code, 200)

    def testUva2Prod(self):
        self.dataset_id = 'test-prod'
        self.path = os.path.join(self.diva, 'gebieden')
        self.host_name = 'ap01.datapunt.amsterdam.nl'

        response = self.update_metadata_uva2(self.path, 'BBK')

        self.assertNotEqual(response, None)
        self.assertEqual(response.status_code, 200)
