import datetime
import requests
import socket

from datasets.generic import uva2

QUALIFIED_HOSTS = 'amsterdam.nl'
ACC_IDENTIFIER = '-acc'
ACC_METADATA_URL = 'https://api-acc.datapunt.amsterdam.nl/metadata/'
PROD_METADATA_URL = 'https://api.datapunt.amsterdam.nl/metadata/'


class UpdateDatasetMixin(object):
    """
    Mixin to update metadata API from import scripts.

    It will call the api-acc or api domain based on hostname.

    usage:

    - set dataset_id to correct dataset
    - call self.update_metadata_uva2 for UVA2 files, or
    - call self.update_metadata_onedate for CSV files, or
    - call self.update_metadata_date for datasets without date in de filename

    These calls will return a Response object, or None when no date was passed.
    """
    dataset_id = None

    @property
    def uri(self):
        if ACC_IDENTIFIER in socket.gethostname():
            return ACC_METADATA_URL

        return PROD_METADATA_URL

    @property
    def on_qualified_domain(self):
        return QUALIFIED_HOSTS in socket.gethostname()

    def update_metadata_uva2(self, path, code):
        filedate = uva2.get_uva2_filedate(path, code)

        return self.update_metadata_date(filedate)

    def update_metadata_onedate(self, path, code):
        filedate = uva2.get_filedate(path, code)

        return self.update_metadata_date(filedate)

    def update_metadata_date(self, date):
        if not date or not self.on_qualified_domain:
            return

        data = {
            'id': self.dataset_id.lower(),
            'data_modified_date': '%d-%d-%d' % (
                date.year, date.month, date.day),
            'last_import_date': datetime.date.today(),
        }

        uri = '%s%s/' % (self.uri, self.dataset_id.lower())

        res = requests.put(uri, data)

        return res
