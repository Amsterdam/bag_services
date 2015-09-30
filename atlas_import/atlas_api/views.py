# Create your views here.
from collections import OrderedDict

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

    if doc_type == "kadastraal_subject":
        return reverse('kadastraalsubject-detail', args=(id,), request=request)

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


def search_query(client, query):
    wildcard = '*{}*'.format(query)

    return (
        Search(client)
            .index('bag', 'brk')
            .query(Q("multi_match", type="phrase_prefix", query=query,
                     fields=['naam', 'adres', 'postcode', 'geslachtsnaam'])
                   | Q("wildcard", naam=dict(value=wildcard))
                   )
            .sort({"straatnaam": {"order": "asc", "missing": "_first", "unmapped_type": "string"}},
                  {"huisnummer": {"order": "asc", "missing": "_first", "unmapped_type": "long"}},
                  {"adres": {"order": "asc", "missing": "_first", "unmapped_type": "string"}},
                  '-_score',
                  'naam',
                  )
    )


def autocomplete_query(client, query):
    return (
        Search(client)
            .index('bag', 'brk')
            .query("function_score",
                   query=Q("multi_match", type="phrase_prefix", query=query, fields=['completions'])
                         | Q("wildcard", naam=dict(value="*{}*".format(query))),
                   functions=[
                       {'filter': {'type': {'value': 'openbare_ruimte'}},
                        'weight': 30}
                   ])
            .highlight('completions', pre_tags=[''], post_tags=[''])
    )


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

        result = autocomplete_query(self.client, query)[0:20].execute()
        matches = []
        seen = set()
        for h in result:
            for m in h.meta.highlight.completions:
                if m not in seen:
                    matches.append(m)
                seen.add(m)

        return Response([dict(item=m) for m in matches][:5])


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
        search = search_query(client, query)[0:100]

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
