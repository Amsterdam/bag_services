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
            # Make sure to order your querset
            article_qs = Article.objects.order_by('id')
            for start, end, total, qs in batch_qs(article_qs):
                print "Now processing %s - %s of %s" % (start + 1, end, total)
                for article in qs:
                    print article.body
        """
        qs = self.get_queryset()
        batch_size = settings.BATCH_SETTINGS['batch_size']
        self.total = total = qs.count()

        total_batches = int(total / batch_size)

        for i, start in enumerate(range(0, total, batch_size)):
            end = min(start + batch_size, total)
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

        for batch_i, total_batches, start, end, total, qs in self.batch_qs():

            progres_msg = 'batch %s of %s : %8s %8s %8s' % (
                batch_i, total_batches, start, end, total)

            log.debug(progres_msg)

            helpers.bulk(
                client, (self.convert(obj).to_dict(include_meta=True)
                         for obj in tqdm(qs)),
                raise_on_error=True,
                refresh=True
            )


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
