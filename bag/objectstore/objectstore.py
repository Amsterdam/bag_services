"""
Module Contains logic to get the latest most up to date
files to import in the BAG / BRK / WKPB database

Goal is to assure we load Datapunt with accurate and current data

checks:

   check AGE of filenames
     - we do not work with old data
   check filename changes
     - we do not work of old files because new files are renamed

We download specific zip files:

Unzip target data in to empty new location and start
import proces.


"""
import datetime
import logging
import os
import re

from functools import lru_cache
from pathlib import Path
from dateutil import parser

from swiftclient.client import Connection

log = logging.getLogger(__name__)

logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("swiftclient").setLevel(logging.WARNING)

environment = os.getenv('GOB_OBJECTSTORE_ENV', 'productie')
os_connect = {
    'auth_version': '2.0',
    'authurl': 'https://identity.stack.cloudvps.com/v2.0',
    'user': 'GOB_user',
    'key': os.getenv('GOB_OBJECTSTORE_PASSWORD', 'insecure'),
    'tenant_name': 'BGE000081_GOB',
    'os_options': {
        'tenant_id': '2ede4a78773e453db73f52500ef748e5',
        'region_name': 'NL',
    }
}

GOB_DIR = os.getenv('GOB_DIR', '/app/data/gob')


@lru_cache(maxsize=None)
def get_conn():
    assert os.getenv('GOB_OBJECTSTORE_PASSWORD')
    return Connection(**os_connect)


def get_full_container_list(container_name, **kwargs):
    """
    Return a listing of filenames in container `container_name`
    :param container_name:
    :param kwargs:
    :return:
    """
    limit = 10000
    kwargs['limit'] = limit
    page = []
    seed = []
    _, page = get_conn().get_container(container_name, **kwargs)
    seed.extend(page)

    while len(page) == limit:
        # keep getting pages..
        kwargs['marker'] = seed[-1]['name']
        _, page = get_conn().get_container(container_name, **kwargs)
        seed.extend(page)

    return seed


def download_file(container_name, file_path, target_path=None, target_root=GOB_DIR, file_last_modified=None):
    path = file_path.split('/')

    file_name = path[-1]
    log.info(f"Create file {file_name} in {target_root}")
    file_name = path[-1]

    if target_path:
        newfilename = '{}/{}'.format(target_root, target_path)
    else:
        newfilename = '{}/{}'.format(target_root, file_name)

    if file_exists(newfilename):
        log.debug('Skipped file exists: %s', newfilename)
        return

    with open(newfilename, 'wb') as newfile:
        data = get_conn().get_object(container_name, file_path)[1]
        newfile.write(data)
    if file_last_modified:
        epoch_modified = file_last_modified.timestamp()
        os.utime(newfilename, (epoch_modified, epoch_modified))


def download_file_data(container_name, file_path):
    return get_conn().get_object(container_name, file_path)[1]


def download_wkpb_file_data(file_path):
    return download_file_data(environment, file_path)


def file_exists(target):
    target = Path(target)
    return target.is_file()


gob_file_age_list = {
    # gebieden
    'gebieden/SHP/GBD_ggw_gebied.shp': 10,
    'gebieden/SHP/GBD_ggw_praktijkgebied.shp': 10,
    'gebieden/SHP/GBD_wijk.shp': 10,
    'gebieden/SHP/GBD_grootstedelijke_projecten.shp': 365,  # this is manually uploaded, not generated by GOB
    'gebieden/SHP/GBD_unesco.shp': 365,                     # this is manually uploaded, not generated by GOB
    'gebieden/CSV_Actueel/GBD_gemeente_Actueel.csv': 365,   # this is manually uploaded, not generated by GOB
    'gebieden/CSV_Actueel/GBD_bouwblok_Actueel.csv': 10,
    'gebieden/CSV_Actueel/GBD_buurt_Actueel.csv': 10,
    'gebieden/CSV_Actueel/GBD_ggw_gebied_Actueel.csv': 10,
    'gebieden/CSV_Actueel/GBD_ggw_praktijkgebied_Actueel.csv': 10,
    'gebieden/CSV_Actueel/GBD_stadsdeel_Actueel.csv': 10,
    'gebieden/CSV_Actueel/GBD_wijk_Actueel.csv': 10,
    # bag
    'bag/CSV_Actueel/BAG_brondocument.csv': 5,
    'bag/CSV_Actueel/BAG_ligplaats_Actueel.csv': 5,
    'bag/CSV_Actueel/BAG_nummeraanduiding_Actueel.csv': 5,
    'bag/CSV_Actueel/BAG_openbare_ruimte_Actueel.csv': 5,
    'bag/CSV_Actueel/BAG_openbare_ruimte_beschrijving_Actueel.csv': 5,
    'bag/CSV_Actueel/BAG_pand_Actueel.csv': 5,
    'bag/CSV_Actueel/BAG_standplaats_Actueel.csv': 5,
    'bag/CSV_Actueel/BAG_verblijfsobject_Actueel.csv': 5,
    'bag/CSV_Actueel/BAG_woonplaats_Actueel.csv': 5,
    # brk
    'brk/AmsterdamRegio/CSV_Actueel/BRK_Gemeente_': 365,
    'brk/AmsterdamRegio/CSV_Actueel/BRK_kadastraal_object_': 35,
    'brk/AmsterdamRegio/CSV_Actueel/BRK_kadastraal_subject_': 35,
    'brk/AmsterdamRegio/CSV_Actueel/BRK_aantekening_': 35,
    'brk/AmsterdamRegio/CSV_Actueel/BRK_zakelijke_recht_': 35,
    'brk/AmsterdamRegio/CSV_Actueel/BRK_c_aard_zakelijkrecht_': 35,
    # wkpb
    'wkpb/CSV_Actueel/WKPB_beperking.csv': 5,
    'wkpb/CSV_Actueel/WKPB_brondocument.csv': 5,
    'wkpb/CSV_Actueel/WKPB_orgaan.csv': 5,
    'wkpb/CSV_Actueel/WKPB_type.csv': 5,
    'wkpb/CSV_Actueel/WKPB_beperking_kadastraalobject.csv': 5,
}


def fetch_gob_files(container_name, prefix):
    logging.basicConfig(level=logging.DEBUG)
    now = datetime.datetime.today()

    new_gob_file_age_list = {}
    for key, val in gob_file_age_list.items():
        if key.endswith('.shp'):
            for ext in ['.dbf', '.prj', '.shx']:
                new_key = key.replace('.shp', ext)
                new_gob_file_age_list[new_key] = val
    gob_file_age_list.update(new_gob_file_age_list)

    for file_object in get_full_container_list(container_name, prefix=prefix):

        if file_object['content_type'] == 'application/directory':
            continue

        file_path = file_object['name']
        path = file_path.split('/')

        m = re.search(r'BRK[a-zA-Z_]+(\d{8})\.csv$', file_path)
        if m:
            file_key = file_path[:-12]
            target_filename = path[-1][:-12]+path[-1][-4:]
        else:
            file_key = file_path
            target_filename = path[-1]
        file_max_age = gob_file_age_list.get(file_key)

        if not file_max_age:
            continue

        file_last_modified = parser.parse(file_object['last_modified'])

        delta = now - file_last_modified
        log.debug('AGE %s: %2d days', target_filename, delta.days)

        if delta.days > file_max_age:
            raise ValueError(f"""

            Delivery of file {file_name}is late!

            {file_path} age {delta.days} max_age: {file_max_age}
            """)

        directory = os.path.join(GOB_DIR, *path[:-1])
        if not os.path.exists(directory):
            os.makedirs(directory)

        target_path = os.path.join(*path[:-1], target_filename)
        download_file(container_name, file_path, target_root=GOB_DIR, target_path=target_path,
                      file_last_modified=file_last_modified)


if __name__ == "__main__":
    # Download files from objectstore
    log.info("Start downloading files from objectstore")

    fetch_gob_files(environment, 'gebieden')
    fetch_gob_files(environment, 'bag')
    fetch_gob_files(environment, 'wkpb')
    fetch_gob_files(environment, 'brk')
