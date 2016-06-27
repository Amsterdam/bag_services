import csv
import os.path

import sys
from django.contrib.gis.gdal import DataSource

from django.contrib.gis.geos import GEOSGeometry, Polygon, MultiPolygon, Point

# sommige WKT-velden zijn best wel groot
csv.field_size_limit(sys.maxsize)


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
        return [result for result in (callback(row[0], GEOSGeometry(row[1])) for row in rows) if result]


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
    return [result for result in (callback(feature) for feature in lyr) if result]


def get_multipoly(wkt):
    if not wkt:
        return None

    geom = GEOSGeometry(wkt)

    if not geom:
        return None

    if isinstance(geom, Polygon):
        return MultiPolygon(geom)

    if isinstance(geom, Point):
        return None

    return geom
