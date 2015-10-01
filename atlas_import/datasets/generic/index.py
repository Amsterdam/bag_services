import logging

from django.conf import settings
from elasticsearch import helpers
import elasticsearch
import elasticsearch_dsl as es
from elasticsearch_dsl.connections import connections

log = logging.getLogger(__name__)


class RecreateIndexTask(object):
    index = ''
    doc_types = []
    name = 'remove index'

    def __init__(self):
        if not self.index:
            raise ValueError("No index specified")

        if not self.doc_types:
            raise ValueError("No doc_types specified")

        connections.create_connection(hosts=settings.ELASTIC_SEARCH_HOSTS)

    def execute(self):
        idx = es.Index(self.index)

        try:
            idx.delete(ignore=404)
            log.info("Deleted index %s", self.index)
        except AttributeError:
            log.warning("Could not delete index '%s', ignoring", self.index)

        for dt in self.doc_types:
            idx.doc_type(dt)

        idx.create()


class ImportIndexTask(object):
    queryset = None

    def get_queryset(self):
        return self.queryset.all()

    def convert(self, obj):
        raise NotImplementedError()

    def execute(self):
        client = elasticsearch.Elasticsearch(hosts=settings.ELASTIC_SEARCH_HOSTS)
        helpers.bulk(client, (self.convert(obj).to_dict(include_meta=True) for obj in self.get_queryset()))
