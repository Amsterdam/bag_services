import datetime
import requests
import socket

from datasets.generic import uva2


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
    import_hostname = None

    def set_hostname(self, hostname=None):
        if hostname:
            self.import_hostname = hostname
        else:
            self.import_hostname = socket.gethostname()

    @property
    def uri(self):
        if not self.on_domains:
            return 'http://%s/metadata/' % self.import_hostname

        if '-acc' in self.import_hostname:
            return 'https://api-acc.datapunt.amsterdam.nl/metadata/'

        return 'https://api.datapunt.amsterdam.nl/metadata/'

    @property
    def on_domains(self):
        return self.import_hostname and self.import_hostname != socket.gethostname()

    def update_metadata_uva2(self, path, code, hostname=None):
        filedate = uva2.get_uva2_filedate(path, code)

        return self.update_metadata_date(filedate, hostname)

    def update_metadata_onedate(self, path, code, hostname=None):
        filedate = uva2.get_filedate(path, code)

        return self.update_metadata_date(filedate, hostname)

    def update_metadata_date(self, date, hostname=None):
        self.set_hostname(hostname)
        if not date or not self.on_domains:
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
