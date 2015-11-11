# Create your views here.
from collections import OrderedDict

from django.conf import settings
from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search, Q
from rest_framework import viewsets, metadata
from rest_framework.response import Response
from rest_framework.reverse import reverse

from datasets.generic import rest

_details = {
    'ligplaats': 'ligplaats-detail',
    'standplaats': 'standplaats-detail',
    'verblijfsobject': 'verblijfsobject-detail',
    'openbare_ruimte': 'openbareruimte-detail',
    'kadastraal_subject': 'kadastraalsubject-detail',
    'kadastraal_object': 'kadastraalobject-detail',
}


def _get_url(request, doc_type, id):
    if doc_type in _details:
        return rest.get_links(view_name=_details[doc_type], kwargs=dict(pk=id), request=request)

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
                     fields=['naam', 'adres', 'postcode', 'geslachtsnaam', 'aanduiding'])
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
        "kadastraal_subject.naam",
        "kadastraal_object.aanduiding",
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
        "aanduiding",
    ]

    return (
        Search(client)
            .index('bag', 'brk')
            .query(Q("multi_match", query=query, type="phrase_prefix", fields=match_fields)
                   | Q("multi_match", query=query, fuzziness="auto", prefix_length=1, fields=fuzzy_fields))
            .highlight(*completions, pre_tags=[''], post_tags=[''])
    )


def get_autocomplete_response(client, query):
    result = autocomplete_query(client, query)[0:20].execute()
    matches = OrderedDict()
    for r in result:
        h = r.meta.highlight
        for key in h:
            highlights = h[key]
            for match in highlights:
                matches[match] = 1
    response = [dict(item=m) for m in matches.keys()][:5]
    return response


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

        response = get_autocomplete_response(self.client, query)
        return Response(response)


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
            prev_page = "{}?q={}&page={}".format(followup_url, query, page - 1)

        total = result.hits.total
        if end >= total:
            next_page = None
        else:
            next_page = "{}?q={}&page={}".format(followup_url, query, page + 1)

        res = OrderedDict()
        res['_links'] = OrderedDict([
            ('self', dict(href=followup_url)),
        ])
        if next_page:
            res['_links']['next'] = dict(href=next_page)
        else:
            res['_links']['next'] = None

        if prev_page:
            res['_links']['previous'] = dict(href=prev_page)
        else:
            res['_links']['previous'] = None

        res['count'] = result.hits.total
        res['results'] = [self.normalize_hit(h, request) for h in result.hits]

        return Response(res)

    def normalize_hit(self, hit, request):
        result = OrderedDict()
        result['_links'] = _get_url(request, hit.meta.doc_type, hit.meta.id)
        result['type'] = hit.meta.doc_type
        result['dataset'] = hit.meta.index
        # result['uri'] = _get_url(request, hit.meta.doc_type, hit.meta.id) + "?full"
        result.update(hit.to_dict())

        return result
