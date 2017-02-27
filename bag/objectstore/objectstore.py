import logging
import os

import datetime
import zipfile


from dateutil import parser
from functools import lru_cache
from pathlib import Path

from swiftclient.client import Connection


logging.basicConfig(level=logging.DEBUG)

log = logging.getLogger(__name__)

logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("swiftclient").setLevel(logging.WARNING)

os_connect = {
    'auth_version': '2.0',
    'authurl': 'https://identity.stack.cloudvps.com/v2.0',
    'user': 'bag_brk',
    'key': os.getenv('BAG_OBJECTSTORE_PASSWORD', 'insecure'),
    'tenant_name': 'BGE000081_BAG',
    'os_options': {
        'tenant_id': '4f2f4b6342444c84b3580584587cfd18',
        'region_name': 'NL',
    }
}

# zet in data directory laat diva voor test data.
# in settings een verschil maken
DIVA_DIR = '/app/data'


@lru_cache(maxsize=None)
def get_conn():
    assert os.getenv('BAG_OBJECTSTORE_PASSWORD')
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


def delete_from_objectstore(container, object_name):
    """
    remove file `object_name` fronm `container`
    :param container: Container name
    :param object_name:
    :return:
    """
    return get_conn().delete_object(container, object_name)


def download_diva_file(container_name, file_path, target_path=None):
    """
    Download a diva file
    :param container_name:
    :param mapped_folder: the foldername where file is written to
    :param folder: foldername in O/S
    :param file_name:
    :return:
    """

    path = file_path.split('/')

    file_name = path[-1]
    log.info("Create file {} in {}".format(DIVA_DIR, file_name))
    file_name = path[-1]

    if target_path:
        newfilename = '{}/{}'.format(DIVA_DIR, target_path)
    else:
        newfilename = '{}/{}'.format(DIVA_DIR, file_name)

    if file_exists(newfilename):
        log.debug('Skipped file exists: %s', newfilename)
        return

    with open(newfilename, 'wb') as newfile:
        zipdata = get_conn().get_object(container_name, file_path)[1]
        newfile.write(zipdata)


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
    for zipkey, zipfiles in zips_mapper.items():
        log.debug('KEEP : %s', zipfiles[0][1]['name'])
        if len(zipfiles) > 1:
            # delete old files
            for _, zipobject in zipfiles[1:]:
                zippath = zipobject['name']
                log.debug('PURGE: %s', zippath)
                delete_from_objectstore(container_name, zippath)


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


def unzip_files(zipsource):
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


# list of exeptions which are not in the 'official zips'
exception_list = [
    ('bag_geometrie/BAG_OPENBARERUIMTE_GEOMETRIE.dat',
     'bag_wkt/BAG_OPENBARERUIMTE_GEOMETRIE.dat'),
    ('gebieden_shp/GBD_gebiedsgerichtwerken.shp', ''),
    ('gebieden_shp/GBD_grootstedelijke_projecten.shp', ''),
    ('gebieden_shp/GBD_unesco.shp', ''),
]


def get_specific_files(container_name):
    """
    There are some files not contained in the zips.
    Lets pick them up seperately..
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


def unzip_data(zips_mapper):
    """
    unzip the zips
    """

    for zipkey, zipfiles in zips_mapper.items():

        latestzip = zipfiles[0][1]

        filepath = latestzip['name'].split('/')
        file_name = filepath[-1]
        zip_path = '{}/{}'.format(DIVA_DIR, file_name)

        log.info("Unzip {}".format(zip_path))

        zipsource = zipfile.ZipFile(zip_path, 'r')
        unzip_files(zipsource)


zip_age_limits = {
  'GEBASCII.zip': 5,
  'GEBSHAPE.zip': 50,
  'BAGACTUEEL.zip': 5,
  'BAGGEOMETRIE.zip': 5,
  'BAGLSLEUTEL.zip': 5,
  'BRKASCII.zip': 5,
  'BRKSHAPE.zip': 5,
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
    log.debug('%s_%s' % (zip_created.strftime('%Y%m%d'), file_key))

    for key, agelimit in zip_age_limits.items():
        if file_key.endswith(key):
            if zip_age_limits[key] < delta.days:
                raise ValueError(f'Zip delivery is late! {source_name}')


def fetch_diva_zips(container_name, zipfolder):
    """
    fetch files from folder in an objectstore container
    :param container_name:
    :param folder:
    :return:
    """
    log.info("import files from {}".format(zipfolder))

    zips_mapper = {}

    for file_object in get_full_container_list(
            container_name, prefix=zipfolder):

        if file_object['content_type'] == 'application/directory':
            continue

        path = file_object['name'].split('/')
        file_name = path[-1]

        if not file_name.endswith('.zip'):
            continue

        exclude = ['BRT', 'NAP', 'MBT']

        if any(REGTYPE in file_name for REGTYPE in exclude):
            continue

        dt = parser.parse(file_object['last_modified'])
        file_key = "".join(file_name.split('_')[1:])

        check_age(dt, file_key, file_object)

        zips_mapper.setdefault(file_key, []).append((dt, file_object))

    download_zips(container_name, zips_mapper)
    delete_old_zips(container_name, zips_mapper)
    unzip_data(zips_mapper)


def fetch_diva_files():
    """
    Er zijn nog geen zip files, selecteer de individuele files.
    totdat de zips gerealiseerd zijn alleen de .csvs en .uva2s
    :return:
    """
    # creat folders where files are expected.
    create_target_directories()
    # download the exceptions not in zip files
    # these are special cases manual made by some people
    get_specific_files('Diva')
    # download and unpack the zip files
    # These come from a more official product
    fetch_diva_zips('Diva', 'Zip_bestanden')


if __name__ == "__main__":
    # Download files from objectstore
    log.info("Start downloading files from objectstore")
    fetch_diva_files()
