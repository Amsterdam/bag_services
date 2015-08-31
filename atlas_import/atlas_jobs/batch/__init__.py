import csv
import logging
import os
from django.contrib.gis.geos import GEOSGeometry
from atlas_jobs import uva2

log = logging.getLogger(__name__)


class AbstractOrmTask(object):
    """
    Basic batch task for working with Django ORM.
    """

    def __init__(self):
        self.cache = dict()

    def execute(self):
        raise NotImplementedError()

    def tear_down(self):
        self.cache.clear()

    def merge(self, model, pk, values):
        model.objects.update_or_create(pk=pk, defaults=values)

    def merge_existing(self, model, pk, values):
        model.objects.filter(pk=pk).update(**values)

    def foreign_key_id(self, model, model_id):
        """
        Returns `model_id` if `model_id` identifies a valid instance of `model`; returns None otherwise.
        """
        if not model_id:
            return None

        key = str(model)
        id_set = self.cache.get(key, None)

        if id_set is None:
            id_set = set(model.objects.values_list('pk', flat=True))
            self.cache[key] = id_set

        if model_id not in id_set:
            log.warning("Reference to non-existing object of type %s with key %s", model, model_id)
            return None

        return model_id


class AbstractUvaTask(AbstractOrmTask):
    """
    Basic task for processing UVA2 files
    """
    code = None

    def __init__(self, source):
        super().__init__()
        self.source = uva2.resolve_file(source, self.code)
        self.cache = dict()

    def execute(self):
        try:
            with uva2.uva_reader(self.source) as rows:
                for r in rows:
                    self.process_row(r)
        finally:
            self.cache.clear()

    def process_row(self, r):
        raise NotImplementedError()


class AbstractWktTask(AbstractOrmTask):
    """
    Basic task for processing WKT files
    """

    source_file = None

    def __init__(self, source_path):
        super().__init__()
        self.source = os.path.join(source_path, self.source_file)

    def execute(self):
        with open(self.source) as f:
            rows = csv.reader(f, delimiter='|')
            for row in rows:
                self.process_row(row[0], GEOSGeometry(row[1]))

    def process_row(self, row_id, geom):
        raise NotImplementedError()