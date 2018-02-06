# Python
import datetime
import requests
import socket
import os
import logging
# Project
from datasets.generic import uva2

METADATA_URL = os.getenv('METADATA_URL', '')

log = logging.getLogger(__name__)


class UpdateDatasetMixin(object):
    """
    Mixin to update metadata API from import scripts.

    It will call the acc.api or api domain based on hostname.

    usage:

    - set dataset_id to correct dataset
    - call self.update_metadata_uva2 for UVA2 files, or
    - call self.update_metadata_onedate for CSV files, or
    - call self.update_metadata_date for datasets without date in de filename

    These calls will return a Response object, or None when no date was passed.
    """
    dataset_id = None

    def update_metadata_uva2(self, path, code):
        filedate = uva2.get_uva2_filedate(path, code)

        return self.update_metadata_date(filedate)

    def update_metadata_onedate(self, path, code):
        filedate = uva2.get_filedate(path, code)

        return self.update_metadata_date(filedate)

    def update_metadata_date(self, date):

        if not date:
            return

        log.warning('Substracting one day of import date!')
        day1 = datetime.timedelta(days=1)
        date = date - day1

        if not METADATA_URL:
            return

        data = {
            'id': self.dataset_id.lower(),
            'data_modified_date': '%d-%d-%d' % (
                date.year, date.month, date.day),
            'last_import_date': datetime.date.today(),
        }

        uri = '%s%s/' % (METADATA_URL, self.dataset_id.lower())

        res = requests.put(uri, data)

        return res
