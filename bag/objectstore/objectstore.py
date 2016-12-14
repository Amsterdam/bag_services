import logging
import os

from swiftclient.client import Connection

log = logging.getLogger(__name__)

logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("swiftclient").setLevel(logging.WARNING)

assert os.getenv('OS_PASSWORD_BAG')

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
        'endpoint_type': 'internalURL'
    }
}

DIVA_DIR = 'diva/'


def fetch_importfiles():
    """
    Fetches all files mentioned in prefixes and writes them to `data_dir`/prefixes[1]
    :return:
    """
    store = ObjectStore()

    for container in store.get_containers():
        container_name = container['name']
        for file_object in store._get_full_container_list(container_name, []):
            path = file_object['name'].split('/')

            dir = os.path.join(DIVA_DIR, container_name, '/'.join(path[:-1]))
            fname = os.path.join(DIVA_DIR, container_name, '/'.join(path))

            # create the directory inclusive nonexisting path
            os.makedirs(dir, exist_ok=True)

            # Create the file with content if it is not a directory in object store
            if file_object['content_type'] != 'application/directory':
                newfile = open(fname, 'wb')
                newfile.write(store.get_store_object(container, file_object))
                newfile.close()


class ObjectStore():
    RESP_LIMIT = 10000  # serverside limit of the response

    def __init__(self):
        self.conn = Connection(**os_connect)

    def get_containers(self):
        _, containers = self.conn.get_account()
        return containers

    def get_store_object(self, container, file_object):
        """
        Returns the object store
        :param container:
        :param file_object
        :return:
        """
        return self.conn.get_object(container['name'], file_object['name'])[1]

    def _get_full_container_list(self, container, seed, **kwargs):
        kwargs['limit'] = self.RESP_LIMIT
        if len(seed):
            kwargs['marker'] = seed[-1]['name']

        _, page = self.conn.get_container(container, **kwargs)
        seed.extend(page)
        return seed if len(page) < self.RESP_LIMIT else \
            self._get_full_container_list(container, seed, **kwargs)

    def put_to_objectstore(self, container, object_name, object_content, content_type):
        return self.conn.put_object(container, object_name, contents=object_content, content_type=content_type)

    def delete_from_objectstore(self, container, object_name):
        return self.conn.delete_object(container, object_name)


if __name__ == "__main__":
    # Download files from objectstore
    log.info("Start downloading files from objectstore")
    fetch_importfiles()
    log.info("Finished downloading files from objectstore")

