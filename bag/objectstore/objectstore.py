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
import argparse
import datetime
import logging
import os
import time
import zipfile

from functools import lru_cache
from pathlib import Path
from dateutil import parser

from swiftclient.client import Connection

log = logging.getLogger(__name__)

logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("swiftclient").setLevel(logging.WARNING)

connections = {
    'bag_brk': {
        'auth_version': '2.0',
        'authurl': 'https://identity.stack.cloudvps.com/v2.0',
        'user': 'bag_brk',
        'key': os.getenv('BAG_OBJECTSTORE_PASSWORD', 'insecure'),
        'tenant_name': 'BGE000081_BAG',
        'os_options': {
            'tenant_id': '4f2f4b6342444c84b3580584587cfd18',
            'region_name': 'NL',
        }
    },
    'GOB_user': {
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
}

# zet in data directory laat diva voor test data.
# in settings een verschil maken
DIVA_DIR = '/app/data'
GOB_DIR = '/app/data/gob'


@lru_cache(maxsize=None)
def get_conn(connect):
    assert (connect == 'bag_brk' and os.getenv('BAG_OBJECTSTORE_PASSWORD')) or (
            connect == 'GOB_user' and os.getenv('GOB_OBJECTSTORE_PASSWORD'))
    return Connection(**connections[connect])


def get_full_container_list(connect, container_name, **kwargs):
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
    _, page = get_conn(connect).get_container(container_name, **kwargs)
    seed.extend(page)

    while len(page) == limit:
        # keep getting pages..
        kwargs['marker'] = seed[-1]['name']
        _, page = get_conn(connect).get_container(container_name, **kwargs)
        seed.extend(page)

    return seed


def delete_from_objectstore(connect, container, object_name):
    """
    remove file `object_name` fronm `container`
    :param container: Container name
    :param object_name:
    :return:
    """
    return get_conn(connect).delete_object(container, object_name)


def download_file(connect, container_name, file_path, target_path=None, target_root=DIVA_DIR, file_last_modified=None):
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
        data = get_conn(connect).get_object(container_name, file_path)[1]
        newfile.write(data)
    if file_last_modified:
        epoch_modified = file_last_modified.timestamp()
        os.utime(newfilename, (epoch_modified, epoch_modified))


def download_file_data(connect, container_name, file_path):
    return get_conn(connect).get_object(container_name, file_path)[1]


def download_diva_file(container_name, file_path, target_path=None):
    """
    Download a diva file
    """
    download_file('bag_brk', container_name, file_path, target_path=target_path)


def file_exists(target):
    target = Path(target)
    return target.is_file()


def download_zips(container_name, zips_mapper):
    """
    Download latest zips
    """

    for _, zipfiles in zips_mapper.items():
        zipfiles.sort(reverse=True)
        zip_name = zipfiles[0][1]['name']
        download_diva_file(container_name, zip_name)


def delete_old_zips(container_name, zips_mapper):
    """
    Cleanup old zips
    """
    for _zipkey, zipfiles in zips_mapper.items():
        log.debug('KEEP : %s', zipfiles[0][1]['name'])
        if len(zipfiles) > 1:
            # delete old files
            for _, zipobject in zipfiles[1:]:
                zippath = zipobject['name']
                log.debug('PURGE: %s', zippath)
                delete_from_objectstore('bag_brk', container_name, zippath)


"""
Originele mappen gebruikt door import
bag, bag_wkt, beperkingen, brk, brk_shp
gebieden, gebieden_shp, kbk10, kbk50
"""

path_mapping = {
    'Gebieden/UVA2/GEB_Actueel/ASCII': 'gebieden',
    'Gebieden/Objecten/Esri_Shape': 'gebieden_shp',
    'BRK/BRK_Totaal/ASCII': 'brk',
    'BRK/BRK_Totaal/Esri_Shape': 'brk_shp',
    'BAG/BAG_Geometrie/WKT': 'bag_wkt',
    'BAG/UVA2/BAG_Actueel/ASCII': 'bag',
    'BAG/BAG_LandelijkeSleutel/ASCII': 'bag',
    'WKPB/beperkingen/ASCII': 'beperkingen',
    'BAG/BAG_Authentiek/ASCII': 'bag',
    'bestaatnietinzip': 'bag_openbareruimte_beschrijving',
}


def create_target_directories():
    """
    the directories where the import proces expects the import source files
    should be created before unzipping files.
    """

    # Make sure target directories exist
    for target in path_mapping.values():
        directory = os.path.join(DIVA_DIR, target)
        if not os.path.exists(directory):
            os.makedirs(directory)


def unzip_files(zipsource, mtime):
    """
    Unzip single files to the right target directory
    """

    # Extract files to the expected location
    directory = os.path.join(DIVA_DIR)

    for fullname in zipsource.namelist():
        zipsource.extract(fullname, directory)
        file_name = fullname.split('/')[-1]
        for path, target in path_mapping.items():
            if path in fullname:
                source = f"{directory}/{fullname}"
                target = f'{directory}/{target}/{file_name}'
                # relocate fiel to expected location
                print(source)
                print(target)
                os.rename(source, target)
                os.utime(target, (mtime, mtime))


# list of exceptions which are not in the 'official zips'
exception_list = [
    ('bag_geometrie/BAG_OPENBARERUIMTE_GEOMETRIE.dat',
     'bag_wkt/BAG_OPENBARERUIMTE_GEOMETRIE.dat'),
    ('gebieden_shp/GBD_gebiedsgerichtwerken.shp', ''),
    ('gebieden_shp/GBD_gebiedsgerichtwerken_praktijk.shp', ''),
    ('gebieden_shp/GBD_grootstedelijke_projecten.shp', ''),
    ('gebieden_shp/GBD_unesco.shp', ''),
    ('bag_openbareruimte_beschrijving/OPR_beschrijving.csv', ''),
]


def get_specific_files(container_name):
    """
    There are some files not contained in the zips.
    Lets pick them up separately.
    """
    for specific_file, target in exception_list:

        if not target:
            target = specific_file

        if specific_file.endswith('shp'):
            for ext in ['.dbf', '.prj', '.shx']:
                also_get = specific_file.replace('.shp', ext)
                new_target = target.replace('.shp', ext)
                download_diva_file(
                    container_name, also_get, target_path=new_target)

        download_diva_file(container_name, specific_file, target_path=target)


gob_file_age_list = {
    # gebieden
    'gebieden/SHP/GBD_bouwblok.shp': 10,
    'gebieden/SHP/GBD_buurt.shp': 10,
    'gebieden/SHP/GBD_ggw_gebied.shp': 10,
    'gebieden/SHP/GBD_ggw_praktijkgebied.shp': 10,
    'gebieden/SHP/GBD_stadsdeel.shp': 10,
    'gebieden/SHP/GBD_wijk.shp': 10,
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
    #  The geometrie is also in the CSV files
    #   'bag/SHP/BAG_ligplaats.shp': 100,
    #   'bag/SHP/BAG_openbare_ruimte.shp': 100,
    #   'bag/SHP/BAG_pand.shp': 100,
    #   'bag/SHP/BAG_standplaats.shp': 100,
    #   'bag/SHP/BAG_verblijfsobject.shp': 100,
    #   'bag/SHP/BAG_woonplaats.shp': 100,
    # brk
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

    for file_object in get_full_container_list(
            'GOB_user', container_name, prefix=prefix):

        if file_object['content_type'] == 'application/directory':
            continue

        file_path = file_object['name']
        path = file_path.split('/')

        file_max_age = gob_file_age_list.get(file_path)
        file_name = path[-1]

        if not file_max_age:
            continue

        file_last_modified = parser.parse(file_object['last_modified'])

        delta = now - file_last_modified
        log.debug('AGE %s: %2d days', file_name, delta.days)

        if delta.days > file_max_age:
            raise ValueError(f"""

            Delivery of file {file_name}is late!

            {file_path} age {delta.days} max_age: {file_max_age}
            """)

        directory = os.path.join(GOB_DIR, *path[:-1])
        if not os.path.exists(directory):
            os.makedirs(directory)

        download_file('GOB_user', container_name, file_path, target_root=GOB_DIR, target_path=file_path,
                      file_last_modified=file_last_modified)


def unzip_data(zips_mapper):
    """
    unzip the zips
    """

    for _zipkey, zipfiles in zips_mapper.items():
        latestzip = zipfiles[0][1]

        filepath = latestzip['name'].split('/')
        file_name = filepath[-1]
        zip_path = '{}/{}'.format(DIVA_DIR, file_name)

        log.info(f"Unzip {zip_path}")

        zip_date = file_name.split('_')[0]
        log.debug('ZIP_DATE: %s', zip_date)
        zip_date = parser.parse(zip_date)
        zip_seconds = time.mktime(zip_date.timetuple())

        zipsource = zipfile.ZipFile(zip_path, 'r')
        unzip_files(zipsource, zip_seconds)


zip_age_limits = {
    'GEBASCII.zip': 5,
    'GEBSHAPE.zip': 365,
    'BAGACTUEEL.zip': 5,
    'BAGGEOMETRIE.zip': 5,
    'BAGLSLEUTEL.zip': 5,
    'BRKASCII.zip': 10,
    'BRKSHAPE.zip': 10,
    'WKPB.zip': 5,
}


def check_age(zip_created, file_key, file_object):
    """
    Do basic sanity check on zip delivery..
    """

    now = datetime.datetime.today()
    delta = now - zip_created
    log.debug('AGE: %2d days', delta.days)
    source_name = file_object['name']

    log.debug('%s_%s', zip_created.strftime('%Y%m%d'), file_key)

    for key, _agelimit in zip_age_limits.items():
        if file_key.endswith(key):
            if zip_age_limits[key] < delta.days:
                raise ValueError(
                    f"""

        Zip delivery is late!

        {key} age: {delta.days}  max_age: {zip_age_limits[key]}

        from {source_name}

                    """)


def validate_age(zips_mapper):
    """
    Check if the files we want to import are not to old!
    """
    log.debug('validating age..')

    for zipkey, zipfiles in zips_mapper.items():
        # this is the file we want to import
        age, importsource = zipfiles[0]

        check_age(age, zipkey, importsource)

        log.debug('OK: %s %s', age, zipkey)


def fetch_diva_zips(container_name, zipfolder):
    """
    fetch files from folder in an objectstore container
    :param container_name:
    :param zipfolder:
    :return:
    """
    log.info(f"import files from {zipfolder}")

    zips_mapper = {}

    for file_object in get_full_container_list(
            'bag_brk', container_name, prefix=zipfolder):

        if file_object['content_type'] == 'application/directory':
            continue

        path = file_object['name'].split('/')
        file_name = path[-1]

        if not file_name.endswith('.zip'):
            continue

        # not of interest for bag / brk
        exclude = ['BRT', 'NAP', 'MBT']

        if any(REGTYPE in file_name for REGTYPE in exclude):
            continue

        dt = parser.parse(file_object['last_modified'])

        file_key = "".join(file_name.split('_')[1:])

        zips_mapper.setdefault(file_key, []).append((dt, file_object))

    download_zips(container_name, zips_mapper)
    delete_old_zips(container_name, zips_mapper)

    validate_age(zips_mapper)

    unzip_data(zips_mapper)


def fetch_diva_files():
    """
    Er zijn nog geen zip files, selecteer de individuele files.
    totdat de zips gerealiseerd zijn alleen de .csvs en .uva2s
    :return:
    """
    logging.basicConfig(level=logging.DEBUG)
    # creat folders where files are expected.
    create_target_directories()
    # download the exceptions not in zip files
    # these are special cases manual made by some people
    get_specific_files('Diva')
    # download and unpack the zip files
    # These come from a more official product
    fetch_diva_zips('Diva', 'Zip_bestanden')


if __name__ == "__main__":
    argparser = argparse.ArgumentParser()
    argparser.add_argument('-g', '--gob', action='store_true', help='Do GOB import')
    args = argparser.parse_args()
    # Download files from objectstore
    log.info("Start downloading files from objectstore")
    if args.gob:
        fetch_gob_files('productie', 'gebieden')
        fetch_gob_files('productie', 'bag')

    # As long as GOB import not complete we also import DIVA files
    fetch_diva_files()
