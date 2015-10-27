import csv
import os.path
from django.contrib.gis.gdal import DataSource

from django.contrib.gis.geos import GEOSGeometry, Polygon, MultiPolygon


def process_wkt(path, filename, callback):
    """
    Processes a WKT file

    :param path: directory containing the file
    :param filename: name of the file
    :param callback: function taking an id and a geometry; called for every row
    """
    source = os.path.join(path, filename)
    with open(source) as f:
        rows = csv.reader(f, delimiter='|')
        return [callback(row[0], GEOSGeometry(row[1])) for row in rows]


def process_shp(path, filename, callback):
    """
    Processes a shape file

    :param path: directory containing the file
    :param filename: name of the file
    :param callback: function taking a shapefile record; called for every row
    :return:
    """
    source = os.path.join(path, filename)
    ds = DataSource(source, encoding='ISO-8859-1')
    lyr = ds[0]
    return [callback(feature) for feature in lyr]


def get_multipoly(wkt):
    geom = GEOSGeometry(wkt)

    if geom and isinstance(geom, Polygon):
        geom = MultiPolygon(geom)

    return geom
