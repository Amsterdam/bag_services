import datetime
import requests

from datasets.generic import uva2


class UpdateDatasetMixin(object):
    dataset_id = None

    def update_metadata_uva2(self, path, code):
        filedate = uva2.get_uva2_filedate(path, code)

        self.update_metadata_date(filedate)

    def update_metadata_onedate(self, path, code):
        filedate = uva2.get_filedate(path, code)

        self.update_metadata_date(filedate)

    def update_metadata_date(self, date):
        if not date:
            return

        data = {
            'id': self.dataset_id,
            'data_modified_date': date,
            'last_import_date': datetime.date.today(),
        }

        requests.put('/metadata/api/{}/'.format(self.dataset_id), data, format='json')
