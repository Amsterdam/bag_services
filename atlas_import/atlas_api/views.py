# Create your views here.
from collections import OrderedDict
import re

from django.conf import settings
from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search, Q, A
from rest_framework import viewsets, metadata
from rest_framework.response import Response
from rest_framework.reverse import reverse


def _get_url(request, doc_type, id):
    if doc_type == "ligplaats":
        return reverse('ligplaats-detail', args=(id,), request=request)

    if doc_type == "standplaats":
        return reverse('standplaats-detail', args=(id,), request=request)

    if doc_type == "verblijfsobject":
        return reverse('verblijfsobject-detail', args=(id,), request=request)

    if doc_type == "openbare_ruimte":
        return reverse('openbareruimte-detail', args=(id,), request=request)

    return None


class QueryMetadata(metadata.SimpleMetadata):
    def determine_metadata(self, request, view):
        result = super().determine_metadata(request, view)
        result['parameters'] = dict(
            q=dict(
                type="string",
                description="The query to search for",
                required=False
            )
        )
        return result


def adres_query(client, query):
    wildcard = '*{}*'.format(query)

    return (
        Search(client)
            .index('bag')
            .query(Q("match_phrase_prefix", naam=dict(query=query))
                   | Q("wildcard", naam=dict(value=wildcard))
                   | Q("match_phrase_prefix", adres=dict(query=query))
                   | Q("match_phrase_prefix", postcode=dict(query=query))
                   )
            .sort({"straatnaam": {"order": "asc", "missing": "_first"}},
                  {"huisnummer": {"order": "asc", "missing": "_first"}},
                  {"adres": {"order": "asc", "missing": "_first"}},
                  '-_score',
                  'naam',
                  )
    )


def postcode_autocomplete(client, query):
    s = (
        Search(client)
            .index('bag')
            .query(Q("match_phrase_prefix", postcode=dict(query=query)))
    )
    s.aggs.bucket('by_postcode', A('terms', field='postcode'))
    return s


class TypeaheadViewSet(viewsets.ViewSet):
    """
    Given a query parameter `q`, this function returns a subset of all objects that (partially) match the
    specified query.
    """

    metadata_class = QueryMetadata

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.client = Elasticsearch(settings.ELASTIC_SEARCH_HOSTS)

    def list(self, request, *args, **kwargs):
        if 'q' not in request.query_params:
            return Response([])

        query = request.query_params['q']

        if re.match("^\d", query):
            return self.autocomplete_by_postcode(query)

        return self.autocomplete_by_adres(query)

    def autocomplete_by_adres(self, query):
        s = adres_query(self.client, query)[0:5]

        result = s.execute()

        data = [dict(item=h.naam if 'naam' in h else h.adres) for h in result]
        return Response(data)

    def autocomplete_by_postcode(self, query):
        s = postcode_autocomplete(self.client, query)[0:1]
        result = s.execute()

        data = [dict(item=b.key.upper()) for b in result.aggregations.by_postcode.buckets][:5]
        return Response(data)


class SearchViewSet(viewsets.ViewSet):
    """
    Given a query parameter `q`, this function returns a subset of all object that match the elastic search query.
    """

    metadata_class = QueryMetadata

    def list(self, request, *args, **kwargs):
        if 'q' not in request.query_params:
            return Response([])

        query = request.query_params['q']
        query = query.lower()

        client = Elasticsearch(settings.ELASTIC_SEARCH_HOSTS)
        search = adres_query(client, query)[0:100]

        result = search.execute()

        res = OrderedDict()
        res['total'] = result.hits.total
        res['hits'] = [self.normalize_hit(h, request) for h in result.hits]

        return Response(res)

    def normalize_hit(self, hit, request):
        result = OrderedDict()
        result['type'] = hit.meta.doc_type
        result['dataset'] = hit.meta.index
        result['uri'] = _get_url(request, hit.meta.doc_type, hit.meta.id) + "?full"
        result.update(hit.to_dict())

        return result
