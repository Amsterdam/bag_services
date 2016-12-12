import os
import datetime

from django.test import TestCase
from datasets.generic import metadata


class MetadataTest(TestCase, metadata.UpdateDatasetMixin):
    diva = 'diva/'

    #def setUp(self):
    #    metadata.METADATA_URL = 'https://api.datapunt.amsterdam.nl/metadata/'
    #    self.dataset_id = 'test-acc'

    #def tear_down(self):
    #    metadata.METADATA_URL = ''

    #def test_no_metadata_url_dont_call_update_metadata(self):
    #    metadata.METADATA_URL = ''
    #    response = self.update_metadata_date(datetime.datetime.now())

    #    self.assertEqual(response, None)

    #def test_no_date(self):
    #    response = self.update_metadata_date(None)
    #    self.assertEqual(response, None)

    #def test_non_existing(self):
    #    self.dataset_id = 'test-aac'
    #    self.path = os.path.join(self.diva, 'brk')

    #    response = self.update_metadata_onedate(
    #        self.path, 'BRK_zakelijk_recht')

    #    self.assertEqual(response.status_code, 404)

    #def test_upper_case(self):
    #    self.dataset_id = 'TEST-ACC'
    #    self.path = os.path.join(self.diva, 'brk')

    #    response = self.update_metadata_onedate(
    #        self.path, 'BRK_zakelijk_recht')

    #    self.assertEqual(response.status_code, 200)

    #def test_one_date(self):
    #    self.path = os.path.join(self.diva, 'brk')

    #    response = self.update_metadata_onedate(
    #        self.path, 'BRK_zakelijk_recht')

    #    self.assertNotEqual(response, None)
    #    self.assertEqual(response.status_code, 200)

    #def test_uva_2(self):
    #    self.path = os.path.join(self.diva, 'gebieden')

    #    response = self.update_metadata_uva2(self.path, 'BBK')

    #    self.assertNotEqual(response, None)
    #    self.assertEqual(response.status_code, 200)
