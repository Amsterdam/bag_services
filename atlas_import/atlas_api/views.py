# Create your views here.
from collections import OrderedDict

from django.conf import settings
from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search, Q
from rest_framework import viewsets, metadata, pagination
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
    match_fields = [
        "openbare_ruimte.naam",
        "openbare_ruimte.postcode",
        "ligplaats.adres",
        "standplaats.adres",
        "verblijfsobject.adres",
        "kadastraal_subject.geslachtsnaam",
        "kadastraal_subject.naam"
    ]

    fuzzy_fields = [
        "openbare_ruimte.naam",
        "kadastraal_subject.geslachtsnaam"
    ]

    completions = [
        "naam",
        "adres",
        "postcode",
        "geslachtsnaam",
    ]

    return (
        Search(client)
            .index('bag', 'brk')
            .query(Q("multi_match", query=query, type="phrase_prefix", fields=match_fields)
                   | Q("multi_match", query=query, fuzziness="auto", prefix_length=1, fields=fuzzy_fields))
            .highlight(*completions, pre_tags=[''], post_tags=[''])
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
        matches = OrderedDict()
        for r in result:
            h = r.meta.highlight
            for key in h:
                highlights = h[key]
                for match in highlights:
                    matches[match] = 1

        return Response([dict(item=m) for m in matches.keys()][:5])


class SearchViewSet(viewsets.ViewSet):
    """
    Given a query parameter `q`, this function returns a subset of all object that match the elastic search query.
    """

    metadata_class = QueryMetadata
    page_size = 100

    def list(self, request, *args, **kwargs):
        if 'q' not in request.query_params:
            return Response([])

        page = 1
        if 'page' in request.query_params:
            page = int(request.query_params['page'])

        start = ((page - 1) * self.page_size)
        end = (page * self.page_size)

        query = request.query_params['q']

        client = Elasticsearch(settings.ELASTIC_SEARCH_HOSTS)
        search = search_query(client, query)[start:end]

        result = search.execute()

        followup_url = reverse('search-list', request=request)
        if page == 1:
            prev_page = None
        elif page == 2:
            prev_page = "{}?q={}".format(followup_url, query)
        else:
            prev_page = "{}?q={}&page={}".format(followup_url, query, page-1)

        total = result.hits.total
        if end >= total:
            next_page = None
        else:
            next_page = "{}?q={}&page={}".format(followup_url, query, page+1)

        res = OrderedDict()
        res['count'] = result.hits.total
        res['next'] = next_page
        res['previous'] = prev_page
        res['results'] = [self.normalize_hit(h, request) for h in result.hits]

        return Response(res)

    def normalize_hit(self, hit, request):
        result = OrderedDict()
        result['type'] = hit.meta.doc_type
        result['dataset'] = hit.meta.index
        result['uri'] = _get_url(request, hit.meta.doc_type, hit.meta.id) + "?full"
        result.update(hit.to_dict())

        return result
