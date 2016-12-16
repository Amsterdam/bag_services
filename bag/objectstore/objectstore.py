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
conn = Connection(**os_connect)

# zet in data directory laat diva voor test data.
# in settings een verschil maken
DIVA_DIR = '/app/data'


def get_full_container_list(container_name, **kwargs):
    limit = 10000
    kwargs['limit'] = limit
    page = []
    seed = []
    _, page = conn.get_container(container_name, **kwargs)
    seed.extend(page)

    while len(page) == limit:
        # keep getting pages..
        kwargs['marker'] = seed[-1]['name']
        _, page = conn.get_container(container_name, **kwargs)
        seed.extend(page)
    return seed


def split_first(lst):
    "returns the first element after splitting string on '_'"
    return lst.split('_')[0]


def concat_first_two(lst):
    "returns the concatenated first and second element after splitting string on '_'"
    res = lst.split('_')
    return res[0] + res[1]

def get_all(lst):
    return lst

folder_mapping = {
    'bag_actueel': ('bag', split_first, ['UVA2', 'csv']),
    'gebieden_ascii': ('gebieden', split_first, ['UVA2', 'csv']),
    'brk_ascii': ('brk', concat_first_two, ['UVA2', 'csv']),
    'bag_wkt': ('bag_wkt', split_first, ['UVA2', 'csv']),
    'gebieden_shp': ('gebieden_shp', get_all, ['dbf','prj','shp','shx']),
}


def select_last_created_files(seq, key_func=split_first):
    """
    select the last file
    :param seq:
    :param key_func:
    :return:
    """
    my_files = [(key_func(c), c) for c in sorted(seq)]
    latest_in_group = {f[0]: f[1] for f in my_files}
    return sorted([k for c, k in latest_in_group.items()])


def download_diva_file(container_name, mapped_folder, folder, file_name):
    log.info("Create file {} in {}".format(file_name, mapped_folder))
    newfile = open('{}/{}/{}'.format(DIVA_DIR, mapped_folder, file_name), 'wb')
    # import ipdb;ipdb.set_trace()
    newfile.write(conn.get_object(container_name, '{}/{}'.format(folder, file_name))[1])
    newfile.close()


def fetch_diva_folder(container_name, folder):
    """
    fetch files from folder in an objectstore container
    :param container_name:
    :param folder:
    :return:
    """
    log.info("import files from {}".format(folder))
    folder_files = []
    mapped_folder, keyfunc, file_types = folder_mapping[folder]
    for file_object in get_full_container_list(container_name, prefix=folder):
        if file_object['content_type'] != 'application/directory':
            path = file_object['name'].split('/')
            file_name = path[-1]
            if file_types:
                if (file_name.split('.')[-1] in file_types):
                    folder_files.append(file_name)
            else:
                folder_files.append(file_name)

    files_to_download = select_last_created_files(sorted(folder_files), key_func=keyfunc)
    dir = os.path.join(DIVA_DIR, mapped_folder)
    os.makedirs(dir, exist_ok=True)

    for file_name in files_to_download:
        download_diva_file(container_name, mapped_folder, folder, file_name)


def fetch_diva_files():
    """
    Er zijn nog geen zip files, selecteer de individuele files.
    totdat de zips gerealiseerd zijn alleen de .csvs en .uva2s
    :return:
    """
    container_name = 'Diva'
    folders_to_download = ['bag_actueel', 'brk_ascii',
                           'bag_wkt', 'gebieden_ascii', 'gebieden_shp']
    for folder in folders_to_download:
        fetch_diva_folder(container_name, folder)


if __name__ == "__main__":
    # Download files from objectstore
    log.info("Start downloading files from objectstore")
    fetch_diva_files()
    log.info("Finished downloading files from objectstore")
