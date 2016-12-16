import logging
import os
from swiftclient.client import Connection

logging.basicConfig(level=logging.DEBUG)

log = logging.getLogger(__name__)

logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("swiftclient").setLevel(logging.WARNING)

assert os.getenv('OS_PASSWORD_BAG')

os_connect = {
    'auth_version': '2.0',
    'authurl': 'https://identity.stack.cloudvps.com/v2.0',
    'user': 'bag_brk',
    'key': os.getenv('OS_PASSWORD_BAG', 'insecure'),
    'tenant_name': 'BGE000081_BAG',
    'os_options': {
        'tenant_id': '4f2f4b6342444c84b3580584587cfd18',
        'region_name': 'NL',
    }
}

# zet in data directory laat diva voor test data.
# in settings een verschil maken
DIVA_DIR = '/app/data'


def get_full_container_list(conn, container, **kwargs):
    limit = 10000
    kwargs['limit'] = limit
    page = []

    seed = []

    _, page = conn.get_container(container, **kwargs)
    seed.extend(page)

    while len(page) == limit:
        # keep getting pages..
        kwargs['marker'] = seed[-1]['name']
        _, page = conn.get_container(container, **kwargs)
        seed.extend(page)

    return seed

def split_first(lst):
    return lst.split('_')[0]

def concat_first_two(lst):
    res = lst.split('_')
    return res[0]+res[1]

def select_last_created_files(seq, key_func=split_first):
    """
    Select the last file, based on the date in the filename
    :param seq:
    :param key:
    :return:
    """
    my_files = [(key_func(c), c) for c in seq]
    key = ''
    res = {}
    for f in my_files:
        if key != f[0]:
            key = f[0]
        res[key] = f[1]
    return sorted([k for c, k in res.items()])


def fetch_diva_files():
    """
    Er zijn nog geen zip files, selecteer de individuele files.
    totdat de zips gerealiseerd zijn alleen de .csvs en .uva2s
    :return:
    """
    folder_mapping = {
        'bag_actueel': 'bag',
        'gebieden_ascii': 'gebieden',
        'brk_ascii': 'brk',
        'bag_wkt': 'bag_wkt',
    }

    store = ObjectStore()
    for container in store.get_containers():
        container_name = container['name']
        if container_name == 'Diva':
            folders_to_download = ['bag_actueel', 'brk_ascii', 'gebieden_ascii', 'bag_wkt']
            for folder in folders_to_download:
                log.info("import files from {}".format(folder))
                folder_files = []
                for file_object in store._get_full_container_list(container_name, [], prefix=folder):
                    if file_object['content_type'] != 'application/directory':
                        path = file_object['name'].split('/')
                        file_name = path[-1]
                        if (file_name.split('.')[-1] in ['UVA2', 'csv']):
                            folder_files.append(file_name)

                keyfunc = concat_first_two if folder == 'brk_ascii' else split_first
                files_to_download = select_last_created_files(sorted(folder_files), key_func=keyfunc)
                mapped_folder = folder_mapping['folder']
                dir = os.path.join(DIVA_DIR, mapped_folder)
                os.makedirs(dir, exist_ok=True)

                for file_name in files_to_download:
                    log.info("Create file {} in {}".format(file_name, mapped_folder))
                    newfile = open('{}/{}/{}'.format(DIVA_DIR, mapped_folder, file_name), 'wb')
                    newfile.write(store.get_store_object(container, '{}/{}'.format(folder, file_name)))
                    newfile.close()



class ObjectStore():
    RESP_LIMIT = 10000  # serverside limit of the response

    def __init__(self):
        self.conn = Connection(**os_connect)

    def get_containers(self):
        _, containers = self.conn.get_account()
        return containers

    def get_store_object(self, container, file_name):
        """
        Returns the object store
        :param container:
        :param file_name
        :return:
        """
        return self.conn.get_object(container['name'], file_name)[1]

    def _get_full_container_list(self, container, seed, **kwargs):
        kwargs['limit'] = self.RESP_LIMIT
        if len(seed):
            kwargs['marker'] = seed[-1]['name']

        _, page = self.conn.get_container(container, **kwargs)
        seed.extend(page)
        # geen cercursie AUB.
        return seed if len(page) < self.RESP_LIMIT else \
            self._get_full_container_list(container, seed, **kwargs)

    def put_to_objectstore(
            self, container, object_name, object_content, content_type):
        return self.conn.put_object(
            container, object_name, contents=object_content, content_type=content_type)

    def delete_from_objectstore(self, container, object_name):
        return self.conn.delete_object(container, object_name)


if __name__ == "__main__":
    # Download files from objectstore
    log.info("Start downloading files from objectstore")
    fetch_diva_files()
    log.info("Finished downloading files from objectstore")
