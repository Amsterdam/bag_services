import logging

from django.conf import settings
from elasticsearch import helpers
import elasticsearch
import elasticsearch_dsl as es

from django.db.models.functions import Cast
from django.db.models import F
from django.db.models.functions import Substr
from django.db.models import BigIntegerField

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
    substring = 0  # subtring of id field to parse to integer

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

        log.info('ITEMS %d', qs.count())

        numerator = settings.PARTIAL_IMPORT['numerator']
        denominator = settings.PARTIAL_IMPORT['denominator']

        log.info("PART: %s OF %s" % (numerator+1, denominator))

        for qs_p, progres in self.return_qs_parts(qs, denominator, numerator):
            yield qs_p, progres

    def execute(self):
        """
        Index data of specified queryset
        """
        client = elasticsearch.Elasticsearch(
            hosts=settings.ELASTIC_SEARCH_HOSTS,
            retry_on_timeout=True,
            refresh=True
        )

        start_time = time.time()

        for qs, progress in self.batch_qs():

            elapsed = time.time() - start_time

            total_left = (1 / (progress + 0.001)) * elapsed - elapsed

            progres_msg = \
                '%.3f : duration: %.2f left: %.2f' % (
                    progress, elapsed, total_left
                )

            log.info(progres_msg)

            helpers.bulk(
                client, (self.convert(obj).to_dict(include_meta=True) for obj in qs),
                raise_on_error=True,
                refresh=True
            )

        # When testing put all docs in one shard to make sure we have
        # correct scores/doc counts and test will succeed
        # because relavancy score will make more sense
        if settings.TESTING:
            es_index = IndicesClient(client)
            es_index.forcemerge('*test', max_num_segments=1)

    def return_qs_parts(self, qs, modulo, modulo_value):
        """
        build qs

        modulo and modulo_value determin which chuncks
        are teturned.

        if partial = 1/3

        then this function only returns chuncks index i for which
        modulo i % 3 == 1

        Sometimes the ID field is a string with a number.
        In that case the Indexer can define a substring
        which will extract the number part of the ID field
        """

        if modulo != 1:
            if self.substring:
                qs_s = (
                    qs.annotate(idmod=Substr('id', self.substring))
                    .annotate(idmod=Cast('idmod', BigIntegerField()))
                    .annotate(idmod=F('idmod') % modulo)
                    .filter(idmod=modulo_value)
                )
            else:
                qs_s = (
                    qs.annotate(idmod=Cast('id', BigIntegerField()))
                    .annotate(idmod=F('idmod') % modulo)
                    .filter(idmod=modulo_value)
                )
        else:
            qs_s = qs

        qs_count = qs_s.count()

        log.debug('PART %d/%d Count: %d', modulo, modulo_value, qs.count())

        if not qs_count:
            raise StopIteration

        log.debug(f'PART {modulo_value}/{modulo} {qs_count}')

        batch_size = settings.BATCH_SETTINGS['batch_size']

        for i in range(0, qs_count+batch_size, batch_size):

            print(i)

            if i > qs_count:
                qs_ss = qs_s[i:]
            else:
                qs_ss = qs_s[i:i+batch_size]

            log.debug('Batch %4d %4d', i, i + batch_size)

            yield qs_ss, i/qs_count

        raise StopIteration
