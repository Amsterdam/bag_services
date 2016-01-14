import logging

from django.conf import settings
from elasticsearch import helpers
import elasticsearch
import elasticsearch_dsl as es
from elasticsearch_dsl.connections import connections

from tqdm import tqdm

log = logging.getLogger(__name__)


class DeleteIndexTask(object):
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
        # return self.queryset.iterator()

    def convert(self, obj):
        raise NotImplementedError()

    def execute(self):
        client = elasticsearch.Elasticsearch(
            hosts=settings.ELASTIC_SEARCH_HOSTS)
        helpers.bulk(
            client, (self.convert(obj).to_dict(include_meta=True)
                     for obj in tqdm(self.get_queryset())))


class CopyIndexTask(object):
    """
    Backup index from already loaded documents in elastic

    Building index from existing documents is a lot faster
    then doing if directly from the database

    Especialy userfull when editing/testing analyzers
    and change production environment on the fly
    """
    index = ''
    target = ''
    name = 'copy index elastic'

    def __init__(self):
        """
        """
        if not self.index:
            raise ValueError("No index specified")

        if not self.target:
            raise ValueError("No target index specified")

    def execute(self):
        """
        Reindex elastic index using existing documents
        """
        client = elasticsearch.Elasticsearch(
            hosts=settings.ELASTIC_SEARCH_HOSTS)

        log.debug('Backup index %s to %s ', self.index, self.target)
        helpers.reindex(client, self.index, self.target)

