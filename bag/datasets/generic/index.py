import logging

from django.conf import settings
from elasticsearch import helpers
import elasticsearch
import elasticsearch_dsl as es

from elasticsearch.client import IndicesClient

from elasticsearch.exceptions import NotFoundError

from elasticsearch_dsl.connections import connections

import time

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

        connections.create_connection(
            hosts=settings.ELASTIC_SEARCH_HOSTS,
            # sniff_on_start=True,
            retry_on_timeout=True,
        )

    def execute(self):

        idx = es.Index(self.index)

        try:
            idx.delete(ignore=404)
            log.info("Deleted index %s", self.index)
        except AttributeError:
            log.warning("Could not delete index '%s', ignoring", self.index)
        except NotFoundError:
            log.warning("Could not delete index '%s', ignoring", self.index)

        for dt in self.doc_types:
            idx.doc_type(dt)

        idx.create()


class ImportIndexTask(object):
    queryset = None
    batch_size = 10000

    def get_queryset(self):
        return self.queryset.order_by('id')
        # return self.queryset.iterator()

    def convert(self, obj):
        raise NotImplementedError()

    def batch_qs(self):
        """
        Returns a (start, end, total, queryset) tuple
        for each batch in the given queryset.

        Usage:
            # Make sure to order your querset!
            article_qs = Article.objects.order_by('id')
            for start, end, total, qs in batch_qs(article_qs):
                print "Now processing %s - %s of %s" % (start + 1, end, total)
                for article in qs:
                    print article.body
        """
        qs = self.get_queryset()

        batch_size = settings.BATCH_SETTINGS['batch_size']
        numerator = settings.PARTIAL_IMPORT['numerator']
        denominator = settings.PARTIAL_IMPORT['denominator']

        log.info("PART: %s OF %s" % (numerator+1, denominator))

        end_part = count = total = qs.count()
        chunk_size = batch_size

        start_index = 0

        # Do partial import
        if denominator > 1:
            chunk_size = int(total / denominator)
            start_index = numerator * chunk_size
            end_part = (numerator + 1) * chunk_size
            total = end_part - start_index

        log.info("START: %s END %s COUNT: %s CHUNK %s TOTAL_COUNT: %s" % (
            start_index, end_part, chunk_size, batch_size, count))

        # total batches in this (partial) bacth job
        total_batches = int(chunk_size / batch_size)

        for i, start in enumerate(range(start_index, end_part, batch_size)):
            end = min(start + batch_size, end_part)
            yield (i+1, total_batches+1, start, end, total, qs[start:end])

    def execute(self):
        """
        Index data of specified queryset
        """
        client = elasticsearch.Elasticsearch(
            hosts=settings.ELASTIC_SEARCH_HOSTS,
            # sniff_on_start=True,
            retry_on_timeout=True,
            refresh=True
        )

        start_time = time.time()
        duration = time.time()
        loop_time = elapsed = duration - start_time

        for batch_i, total_batches, start, end, total, qs in self.batch_qs():

            loop_start = time.time()
            total_left = ((total_batches - batch_i) * loop_time) + 1 / 60

            progres_msg = \
                '%s of %s : %8s %8s %8s duration: %.2f left: %.2f' % (
                    batch_i, total_batches, start, end, total, elapsed,
                    total_left
                )

            log.debug(progres_msg)

            helpers.bulk(
                client, (self.convert(obj).to_dict(include_meta=True)
                         for obj in qs),
                raise_on_error=True,
                refresh=True
            )

            now = time.time()
            elapsed = now - start_time
            loop_time = now - loop_start

        # When testing put all docs in one shard to make sure we have
        # correct scores/doc counts and test will succeed
        # because relavancy score will make more sense
        if settings.TESTING:
            es_index = IndicesClient(client)
            es_index.optimize('*test', max_num_segments=1)


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
            hosts=settings.ELASTIC_SEARCH_HOSTS,
            # sniff_on_start=True,
            retry_on_timeout=True
        )

        log.debug('Backup index %s to %s ', self.index, self.target)
        helpers.reindex(client, self.index, self.target)

