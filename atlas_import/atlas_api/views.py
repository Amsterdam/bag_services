# Create your views here.
import logging
from collections import OrderedDict

from django.conf import settings

from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search, Q, A
from elasticsearch.exceptions import TransportError

from rest_framework import viewsets, metadata
from rest_framework.response import Response
from rest_framework.reverse import reverse

from datasets.generic import rest

log = logging.getLogger('search')

_details = {
    'ligplaats': 'ligplaats-detail',
    'standplaats': 'standplaats-detail',
    'verblijfsobject': 'verblijfsobject-detail',
    'openbare_ruimte': 'openbareruimte-detail',
    'kadastraal_subject': 'kadastraalsubject-detail',
    'kadastraal_object': 'kadastraalobject-detail',
}

BAG = settings.ELASTIC_INDICES['BAG']
BRK = settings.ELASTIC_INDICES['BRK']
NUMMERAANDUIDING = settings.ELASTIC_INDICES['NUMMERAANDUIDING']


def _get_url(request, hit):
    doc_type, id = hit.meta.doc_type, hit.meta.id

    if hasattr(hit, 'subtype_id'):
        id = hit.subtype_id if hit.subtype_id else id

    if doc_type in _details:
        return rest.get_links(
            view_name=_details[doc_type],
            kwargs=dict(pk=id), request=request)

    # hit must have subtype
    assert hit.subtype

    if hit.subtype in _details:
        return rest.get_links(
            view_name=_details[hit.subtype],
            kwargs=dict(pk=id), request=request)

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


def mulitimatch_Q(query):
    """
    main 'One size fits all' search query used
    """
    log.debug('%20s %s', mulitimatch_Q.__name__, query)

    return Q(
        "multi_match",
        query=query,
        # type="most_fields",
        # type="phrase",
        type="phrase_prefix",
        slop=12,     # match "stephan preeker" with "stephan jacob preeker"
        max_expansions=12,
        fields=[
            'naam',
            'straatnaam',
            'straatnaam_nen',
            'straatnaam_ptt',
            'aanduiding',
            'adres',

            'postcode',
            'huisnummer'
            'huisnummer_variation',
        ]
    )


def mulitimatch_adres_Q(query):
    """
    Adres search query used
    """
    log.debug('%20s %s', mulitimatch_adres_Q.__name__, query)
    log.debug('using indices %s %s', BAG, BRK)

    return Q(
            "multi_match",
            query=query,
            # type="most_fields",
            # type="phrase",
            type="phrase_prefix",
            slop=12,  # match "stephan preeker" with "stephan jacob preeker"
            max_expansions=12,
            fields=[
                'naam',
                'straatnaam',
                'straatnaam_nen',
                'straatnaam_ptt',
                'aanduiding',
                'adres',
                'postcode',
                'huisnummer_variation',
                'kadastraal_object.aanduiding']
    )


def mulitimatch_subject_Q(query):
    """
    Adres search query used
    """
    log.debug('%20s %s', mulitimatch_subject_Q.__name__, query)
    log.debug('using indices %s %s', BAG, BRK)

    return Q(
            "multi_match",
            query=query,
            type="phrase_prefix",
            slop=14,  # match "stephan preeker" with "stephan jacob preeker"
            max_expansions=12,
            fields=[
                'naam',
                'geslachtsnaam',
            ]
    )


def mulitimatch_object_Q(query):
    """
    Object search
    """
    log.debug('%20s %s', mulitimatch_object_Q.__name__, query)

    return Q(
        "multi_match",
        query=query,
        type="phrase_prefix",
        fields=[
            'aanduiding',
            'postcode',
            'huisnummer_variation',
            ]
    )


def mulitimatch_openbare_ruimte_Q(query):
    """
    Openbare ruimte search
    """
    log.debug('%20s %s', mulitimatch_openbare_ruimte_Q.__name__, query)

    return Q(
            "multi_match",
            query=query,
            # type="most_fields",
            # type="phrase",
            type="phrase_prefix",
            slop=12,  # match "stephan preeker" with "stephan jacob preeker"
            max_expansions=12,
            fields=[
                'openbare_ruimte.naam',
                'openbare_ruimte.postcode',
                'openbare_ruimte.subtype',
            ]
    )


def mulitimatch_nummeraanduiding_Q(query):
    """
    Nummeraanduiding search
    """
    log.debug('%20s %s', mulitimatch_nummeraanduiding_Q.__name__, query)

    """
    "straatnaam": "Eerste Helmersstraat",
    "buurtcombinatie": "Helmersbuurt",
    "huisnummer": 104,
    "huisnummer_variation": 104,
    "subtype": "Verblijfsobject",
    "postcode": "1054EG-104G",
    "adres": "Eerste Helmersstraat 104G",
    """

    return Q(
        "multi_match",
        query=query,
        # type="most_fields",
        # type="phrase",
        type="phrase_prefix",
        slop=12,     # match "stephan preeker" with "stephan jacob preeker"
        max_expansions=12,
        fields=[
            'naam',
            'straatnaam',
            'straatnaam_nen',
            'straatnaam_ptt',
            'aanduiding',
            'adres',

            'postcode',
            'huisnummer'
            'huisnummer_variation',
        ]
    )


def mulitimatch_nummeraanduiding_Q(query):
    """
    Nummeraanduiding search
    """
    log.debug('%20s %s', mulitimatch_nummeraanduiding_Q.__name__, query)

    """
    "straatnaam": "Eerste Helmersstraat",
    "buurtcombinatie": "Helmersbuurt",
    "huisnummer": 104,
    "huisnummer_variation": 104,
    "subtype": "Verblijfsobject",
    "postcode": "1054EG-104G",
    "adres": "Eerste Helmersstraat 104G",
    """

    return Q(
        "multi_match",
        query=query,
        # type="most_fields",
        # type="phrase",
        type="phrase_prefix",
        slop=12,     # match "stephan preeker" with "stephan jacob preeker"
        max_expansions=12,
        fields=[
            'naam',
            'straatnaam',
            'straatnaam_nen',
            'straatnaam_ptt',
            'aanduiding',
            'adres',

            'postcode',
            'huisnummer'
            'huisnummer_variation',
        ]
    )


def wildcard_Q(query):
    """
    wilcard match
    """
    wildcard = '*{}*'.format(query)
    return Q(
            "wildcard",
            naam=dict(value=wildcard),
    )


def wildcard_Q2(query):
    fuzzy_fields = [
        "openbare_ruimte.naam",
        "kadastraal_subject.geslachtsnaam",
        "adres",

        'straatnaam',
        'straatnaam_nen',
        'straatnaam_ptt',

        # "postcode",

        # "ligplaats.adres",
        # "standplaats.adres",
        # "verblijfsobject.adres",
    ]

    return Q("multi_match",
             query=query, fuzziness="auto",
             max_expansions=50,
             prefix_length=2, fields=fuzzy_fields)


def add_sorting():
    """
    Give human understandable sorting to the output
    """
    return (
        {"order": {
            "order": "asc", "missing": "_last", "unmapped_type": "long"}},
        {"straatnaam": {
            "order": "asc", "missing": "_first", "unmapped_type": "string"}},
        {"huisnummer": {
            "order": "asc", "missing": "_first", "unmapped_type": "long"}},
        {"adres": {
            "order": "asc", "missing": "_first", "unmapped_type": "string"}},
        '-_score',
        # 'naam',
    )


def add_nummerduiding_sorting():
    """
    Give human understandable sorting to the output
    """
    return (
        {"order": {
            "order": "asc", "missing": "_last", "unmapped_type": "long"}},
        {"straatnaam": {
            "order": "asc", "missing": "_first", "unmapped_type": "string"}},
        {"huisnummer": {
            "order": "asc", "missing": "_first", "unmapped_type": "long"}},
        {"adres": {
            "order": "asc", "missing": "_first", "unmapped_type": "string"}},
        '-_score',
        'adres'
    )


def default_search_query(view, client, query):

    """
    Execute search.

    ./manage.py test atlas_api.tests.test_query --keepdb

    """
    log.debug('using indices %s %s %s', BAG, BRK, NUMMERAANDUIDING)

    return (
        Search(client)
        .index(NUMMERAANDUIDING, BAG, BRK)
        .query(
            mulitimatch_Q(query)
        )
        .sort(*add_sorting())
    )


def search_adres_query(view, client, query):
    """
    Execute search on adresses
    """
    return (
        Search(client)
        .index(BAG, BRK, NUMMERAANDUIDING)
        .query(
            mulitimatch_adres_Q(query)
        )
        .sort(*add_sorting())
    )


def search_subject_query(view, client, query):
    """
    Execute search on adresses
    """
    return (
        Search(client)
            # .filter("term", category="search")
            .index(BRK)
            .query(
                mulitimatch_subject_Q(query)
        )
            .sort(*add_sorting())
    )


def search_object_query(view, client, query):
    """
    Execute search in Objects
    """
    return (
        Search(client)
        .index(BRK)
        .query(
            mulitimatch_object_Q(query)
        )
        .sort(*add_sorting())
    )


def search_openbare_ruimte_query(view, client, query):
    """
    Execute search in Objects
    """
    return (
        Search(client)
        .index(BAG)
        .query(
            mulitimatch_openbare_ruimte_Q(query)
        )
        .sort(*add_sorting())
    )


def search_nummeraanduiding_query(view, client, query):
    """
    Execute search in Objects
    """
    return (
        Search(client)
        .index(NUMMERAANDUIDING)
        .query(
            mulitimatch_nummeraanduiding_Q(query)
        )
        .sort(*add_nummerduiding_sorting())
    )


def test_search_query(view, client, query):
    """
    Do test experiments here..
    """

    s = Search(client)\
        .index(NUMMERAANDUIDING, BAG, BRK)\
        .query(
            Q("multi_match",
              query=query,
              # type="most_fields",
              # type="phrase",
              type="phrase_prefix",
              slop=12,
              # max_expansions=12,
              fields=[
                  'naam',
                  'straatnaam',
                  'straatnaam_nen',
                  'straatnaam_ptt',
                  'aanduiding',
                  'adres',

                  'postcode',
                  'huisnummer'
                  'huisnummer_variation',
                  'type'
              ],
              ),
        )

    # .sort(*add_sorting())

    # add aggregations
    a = A('terms', field='subtype', size=100)
    b = A('terms', field='_type', size=100)

    # tops = A('top_hits', size=1)

    s.aggs.bucket('by_subtype', a)
    # s.aggs.bucket('by_type', b)

    # give back top results
    # s.aggs.bucket('by_type', b).bucket('top', tops)

    return s


def autocomplete_query(client, query):
    """
    provice autocomplete suggestions
    """

    match_fields = [
        "naam",
        "postcode",

        'straatnaam',
        'straatnaam_nen',
        'straatnaam_ptt',

        "adres",

        "huisnummer_variation",

        "kadastraal_subject.geslachtsnaam",
        "kadastraal_subject.naam",
        "kadastraal_object.aanduiding",
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
        .index(BAG, BRK, NUMMERAANDUIDING)
        .query(
            Q("multi_match",
                query=query, type="phrase_prefix", fields=match_fields)
            | wildcard_Q2(query))
        .highlight(*completions, pre_tags=[''], post_tags=[''])
    )


def get_autocomplete_response(client, query):
    result = autocomplete_query(client, query)[0:20].execute()
    matches = OrderedDict()

    # group_by doc_type
    for r in result:
        doc_type = r.meta.doc_type.replace('_', ' ')

        if doc_type == 'nummeraanduiding':
            doc_type = r.subtype

        if doc_type not in matches:
            matches[doc_type] = OrderedDict()

        h = r.meta.highlight
        for key in h:
            highlights = h[key]
            for match in highlights:
                matches[doc_type][match] = 1

    for doc_type in matches.keys():
        matches[doc_type] = [
            dict(item=m) for m in matches[doc_type].keys()][:5]

    return matches


class TypeaheadViewSetOld(viewsets.ViewSet):
    """
    Given a query parameter `q`, this function returns a
    subset of all objects
    that (partially) match the specified query.

    *NOTE*

    We assume spelling errors and therefore it is possible
    to have unexpected results

    """

    def get_autocomplete_response(self, client, query):
        return {}

    metadata_class = QueryMetadata

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.client = Elasticsearch(settings.ELASTIC_SEARCH_HOSTS)

    def list(self, request, *args, **kwargs):
        if 'q' not in request.query_params:
            return Response([])

        query = request.query_params['q']
        query = query.lower()

        response = get_autocomplete_response(self.client, query)
        return Response(response)


class TypeaheadViewSet(TypeaheadViewSetOld):

    def get_autocomplete_response(self, client, query):
        return get_autocomplete_response(client, query)


class SearchViewSet(viewsets.ViewSet):
    """
    Given a query parameter `q`, this function returns a subset of all objects
    that match the elastic search query.

    *NOTE*

    We assume the input is correct but could be incomplete

    for example: seaching for a not existing
    Rozengracht 3 will rerurn Rozengracht 3-1 which does exist
    """

    metadata_class = QueryMetadata
    page_size = 100
    search_query = default_search_query
    url_name = 'search-list'

    def _set_followup_url(self, request, result, end,
                          response, query, page):
        """
        Add pageing links for result set to response object
        """

        followup_url = reverse(self.url_name, request=request)

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

        response['_links'] = OrderedDict([
            ('self', dict(href=followup_url)),
        ])

        if next_page:
            response['_links']['next'] = dict(href=next_page)
        else:
            response['_links']['next'] = None

        if prev_page:
            response['_links']['previous'] = dict(href=prev_page)
        else:
            response['_links']['previous'] = None

    def list(self, request, *args, **kwargs):
        if 'q' not in request.query_params:
            return Response([])

        page = 1
        if 'page' in request.query_params:
            page = int(request.query_params['page'])

        start = ((page - 1) * self.page_size)
        end = (page * self.page_size)

        query = request.query_params['q']
        query = query.lower()

        client = Elasticsearch(
            settings.ELASTIC_SEARCH_HOSTS,
            raise_on_error=True
        )

        search = self.search_query(client, query)[start:end]

        try:
            result = search.execute()
        except TransportError:
            log.exception("Could not execute search query " + query)
            # Todo fix this
            # https://github.com/elastic/elasticsearch/issues/11340#issuecomment-105433439
            return Response([])

        response = OrderedDict()

        self._set_followup_url(request, result, end, response, query, page)
        # import pdb; pdb.set_trace()

        response['count'] = result.hits.total

        self.create_summary_aggregations(request, result, response)

        response['results'] = [
            self.normalize_hit(h, request) for h in result.hits]

        return Response(response)

    def create_summary_aggregations(self, request, result, response):
        """
        If there are aggregations within the search result.
        show them
        """
        if not hasattr(response, 'aggregations'):
            return

        response['type_summary'] = []

        response['type_summary'] = [
            self.normalize_bucket(field, request)
            for field in result.aggregations['by_subtype']['buckets']]

    def get_url(self, request, hit):
        """
        """
        return _get_url(request, hit)

    def normalize_hit(self, hit, request):
        result = OrderedDict()
        result['_links'] = self.get_url(request, hit)

        result['type'] = hit.meta.doc_type
        result['dataset'] = hit.meta.index
        # result['uri'] = _get_url(
        #     request, hit.meta.doc_type, hit.meta.id) + "?full"
        result.update(hit.to_dict())

        return result

    def normalize_bucket(self, field, request):
        # print(field)
        result = OrderedDict()
        result.update(field.to_dict())
        return result


class SearchAdresViewSet(SearchViewSet):
    """
    Given a query parameter `q`, this function returns a subset of
    all adressable objects that match the adres elastic search query.
    """
    url_name = 'search/adres-list'
    search_query = search_adres_query


class SearchSubjectViewSet(SearchViewSet):
    """
    Given a query parameter `q`, this function returns a subset of all
    kadastraal subjects (VVE, personen) objects
    that match the elastic search query.

    Een Kadastraal Subject is een persoon die
    in de kadastrale registratie voorkomt.
    Het betreft hier zowel natuurlijk- als niet natuurlijk personen.

    https://www.amsterdam.nl/stelselpedia/brk-index/catalog-brk-levering/kadastraal-subject/

    """

    url_name = 'search/kadastraalsubject-list'
    search_query = search_subject_query


class SearchObjectViewSet(SearchViewSet):
    """
    Given a query parameter `q`, this function returns a subset of all
    grond percelen objects that match the elastic search query.
    """

    url_name = 'search/object-list'
    search_query = search_object_query


class SearchOpenbareRuimteViewSet(SearchViewSet):
    """
    Given a query parameter `q`, this function returns a subset
    of all openabare ruimte objects that match the elastic search query.

    Een OPENBARE RUIMTE is een door het bevoegde gemeentelijke orgaan als
    zodanig aangewezen en van een naam voorziene
    buitenruimte die binnen één woonplaats is gelegen.

    Als openbare ruimte worden onder meer aangemerkt weg, water,
    terrein, spoorbaan en landschappelijk gebied.

    http://www.amsterdam.nl/stelselpedia/bag-index/catalogus-bag/objectklasse-3/

    """
    url_name = 'search/openbareruimte-list'
    search_query = search_openbare_ruimte_query


class SearchNummeraanduidingViewSet(SearchViewSet):
    """
    Given a query parameter `q`, this function returns a subset
    of nummeraanduiding objects that match the elastic search query.

    Een nummeraanduiding, in de volksmond ook wel adres genoemd, is een door
    het bevoegde gemeentelijke orgaan als
    zodanig toegekende aanduiding van een verblijfsobject,
    standplaats of ligplaats.

    http://www.amsterdam.nl/stelselpedia/bag-index/catalogus-bag/objectklasse-2/

    """
    url_name = 'search/adres-list'
    search_query = search_nummeraanduiding_query


class SearchTestViewSet(SearchViewSet):
    url_name = 'search/test-list'
    search_query = test_search_query
