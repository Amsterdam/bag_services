import logging

import elasticsearch
import elasticsearch_dsl as es
from django.conf import settings
from django.db.models import BigIntegerField, F
from django.db.models.functions import Cast
from elasticsearch import helpers
from elasticsearch.client import IndicesClient
from elasticsearch.exceptions import NotFoundError
from elasticsearch_dsl.connections import connections

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
    name = None
    queryset = None
    sequential = False  # Non integer PK
    last_id = None

    def get_queryset(self):
        return self.queryset.order_by('id')
        # return self.queryset.iterator()

    def convert(self, obj):
        raise NotImplementedError()

    def batch_qs(self):
        """
        Returns a (queryset, progress) tuple
        for each batch in the given queryset.
        by filtering out records by

            id % modulo = modulo_value

        now it's easy to devide the work acros a few workers

        Usage:
            # Make sure to order your querset!
            article_qs = Article.objects.order_by('id')
            for qs progress in batch_qs(article_qs):
                do_someting_with_batch(qs)

        """
        qs = self.get_queryset()

        log.info('ITEMS %d', qs.count())

        numerator = settings.PARTIAL_IMPORT['numerator']
        denominator = settings.PARTIAL_IMPORT['denominator']

        log.info("PART: %s OF %s" % (numerator+1, denominator))

        return self.return_qs_parts(qs, denominator, numerator)

    def convert_model_to_dict(self, qs):
        """
        Convert django models to elasticsearch documents
        """

        batch = list()

        for obj in qs:
            batch.append(self.convert(obj).to_dict(include_meta=True))
            # store last id
            self.last_id = obj.id

        return batch

    def execute(self):
        """
        Index data of specified queryset
        """
        client = elasticsearch.Elasticsearch(
            hosts=settings.ELASTIC_SEARCH_HOSTS,
            retry_on_timeout=True,
            refresh=True
        )

        for qs in self.batch_qs():

            helpers.bulk(
                client,
                self.convert_model_to_dict(qs),
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
        Build qs

        modulo and modulo_value determin which chuncks
        are teturned.

        if partial = 1/3

        then this function only returns chuncks index id for which
        modulo id % 3 == 1

        Sometimes the ID field is a string with a number.
        In that case the Indexer can define a substring
        which will extract the number part of the ID field
        """

        if modulo != 1:
            if self.sequential:
                total = qs.count()
                chunk_size = int(total / modulo)
                start = chunk_size * modulo_value
                all_ids = qs.all().values('id')
                start_id = all_ids[start]['id']
                qs_s = qs.filter(id__gte=start_id)

                if modulo > modulo_value + 1:
                    end = chunk_size * (modulo_value + 1)
                    end_id = all_ids[end]['id']
                    qs_s = qs_s.filter(id__lt=end_id)
                    log.info('PART %d/%d start_id : %s end_id : %s', modulo_value + 1, modulo, start_id, end_id)
                else:
                    log.info('PART %d/%d start_id : %s ', modulo_value + 1, modulo, start_id)

            else:
                qs_s = (
                    qs.annotate(idmod=Cast('id', BigIntegerField()))
                    .annotate(idmod=F('idmod') % modulo)
                    .filter(idmod=modulo_value)
                )
        else:
            qs_s = qs

        qs_count = qs_s.count()

        log.debug('PART %d/%d Count: %d', modulo_value + 1, modulo, qs_count)

        if not qs_count:
            return

        batch_size = settings.BATCH_SETTINGS['batch_size']
        loopidx = 0

        # gets updates when we save object in es
        self.last_id = None

        while True:
            loopidx += 1

            if not self.last_id:
                qs_ss = qs_s[:batch_size]
            else:
                qs_ss = qs_s.filter(id__gt=self.last_id)[:batch_size]

            percentage = int(min(qs_count, (loopidx * batch_size - 1)) / qs_count * 100)
            log.debug(
                'Batch %4d %6d %3d%% %s  %s',
                loopidx, loopidx * batch_size, percentage, self.name,
                self.last_id if loopidx > 1 else ''
            )

            yield qs_ss

            if qs_ss.count() < batch_size:
                # no more data
                break

