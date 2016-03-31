import datetime
import requests
import socket

from datasets.generic import uva2


class UpdateDatasetMixin(object):
    dataset_id = None
    import_hostname = None

    def set_hostname(self, hostname=None):
        if hostname:
            self.import_hostname = hostname
        else:
            self.import_hostname = socket.gethostname()

    @property
    def uri(self):
        if '-acc' in self.import_hostname:
            return 'https://api-acc.datapunt.amsterdam.nl/metadata/'

        return 'https://api.datapunt.amsterdam.nl/metadata/'

    def update_metadata_uva2(self, path, code):
        filedate = uva2.get_uva2_filedate(path, code)

        return self.update_metadata_date(filedate)

    def update_metadata_onedate(self, path, code):
        filedate = uva2.get_filedate(path, code)

        return self.update_metadata_date(filedate)

    def update_metadata_date(self, date):
        if not date:
            return

        data = {
            'id': self.dataset_id,
            'data_modified_date': date,
            'last_import_date': datetime.date.today(),
        }

        self.set_hostname()
        uri = '%s%s/' % (self.uri, self.dataset_id)

        res = requests.put(uri, data)

        return res
