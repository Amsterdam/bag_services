# Create your views here.
import logging
from collections import OrderedDict

from django.conf import settings
from elasticsearch import Elasticsearch
from elasticsearch.exceptions import TransportError
from elasticsearch_dsl import Search, Q, A
from elasticsearch_dsl import query as query_dsl

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


def multimatch_adres_Q(query):
    """
    Adres search query used
    """
    log.debug('%20s %s', multimatch_adres_Q.__name__, query)
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
            'straatnaam_all',
            'adres',
            'postcode',
            'huisnummer_variation',
            'toevoeging_variation',
            'kadastraal_object.aanduiding']
    )


def multimatch_subject_Q(query):
    """
    Adres search query used
    """
    log.debug('%20s %s', multimatch_subject_Q.__name__, query)
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


def match_object_Q(query):
    """
    Object search
    """
    log.debug('%20s %s', match_object_Q.__name__, query)

    return Q(
        'match',
        _all=query,
    )


def multimatch_openbare_ruimte_Q(query):
    """
    Openbare ruimte search
    """
    log.debug('%20s %s', multimatch_openbare_ruimte_Q.__name__, query)

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
            'naam_var',
            'postcode',
            'subtype',
        ]
    )


def multimatch_nummeraanduiding_Q(query):
    """
    Nummeraanduiding search
    """
    log.debug('%20s %s', multimatch_nummeraanduiding_Q.__name__, query)

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
        slop=12,  # match "stephan preeker" with "stephan jacob preeker"
        max_expansions=12,
        fields=[
            'naam',
            'straatnaam_all',
            'aanduiding',
            'adres',

            'postcode',
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


def fuzzy_Q(query):

    fuzzy_fields = [
        'naam',
        'kadastraal_subject.geslachtsnaam',
        'adres',

        'straatnaam_all',

        'postcode',
    ]

    return Q(
        "multi_match",
        query=query, fuzziness="auto",
        type="cross_fields",
        max_expansions=50,
        prefix_length=2, fields=fuzzy_fields)


def add_sorting():
    """
    Give human understandable sorting to the output
    """
    return (

        {"order": {
            "order": "asc", "missing": "_last", "unmapped_type": "long"}},

        '_score',

        {"straatnaam": {
            "order": "asc", "missing": "_first", "unmapped_type": "string"}},

        {"huisnummer": {
            "order": "asc", "missing": "_first", "unmapped_type": "long"}},

        {"toevoeging": {
            "order": "asc", "missing": "_first", "unmapped_type": "string"}},
    )


def add_default_sorting():
    """
    Give human understandable sorting to the output
    """
    return (

        '_score',

        {"straatnaam": {
            "order": "asc", "missing": "_first", "unmapped_type": "string"}},

        {"huisnummer": {
            "order": "asc", "missing": "_first", "unmapped_type": "long"}},

        {"toevoeging": {
            "order": "asc", "missing": "_first", "unmapped_type": "string"}},

    )


def add_sorting_ob():
    """
    Give human understandable sorting to the output
    """
    return (
        {"order": {
            "order": "asc", "missing": "_last", "unmapped_type": "long"}},

        '_score',

        {"straatnaam": {
            "order": "asc", "missing": "_first", "unmapped_type": "string"}},
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

        {"toevoeging": {
            "order": "asc", "missing": "_first", "unmapped_type": "string"}},

    )


def default_search_query(view, client, query):
    """
    Execute search.

    ./manage.py test atlas_api.tests.test_query --keepdb

    """
    log.debug('using indices %s %s %s', BAG, BRK, NUMMERAANDUIDING)

    search = (
        Search()
        .using(client)
        .index(NUMMERAANDUIDING, BAG, BRK)
        .query(
            'bool',
            should=[
                straatnaam_Q(query),
                postcode_Q(query),

                huisnummer_Q(query),
                huisletters_Q(query),

                adres_Q(query),
                aanduiding_Q(query),
                multimatch_subject_Q(query),

                huisnummer_variation_Q(query)

            ],
            minimum_should_match=1
        )
        .sort(*add_default_sorting())
    )

    if settings.TESTING:
        search.params(search_type='dfs_query_then_fetch')

    return search


def search_adres_query(view, client, query):
    """
    Execute search on adresses
    """
    return (
        Search()
        .using(client)
        .index(BAG, BRK, NUMMERAANDUIDING)
        .query(
            'bool',
            should=[
                straatnaam_Q(query),
                huisnummer_Q(query),
                postcode_Q(query),
            ],
            minimum_should_match=2)
        .sort(*add_sorting())
    )


def search_subject_query(view, client, query):
    """
    Execute search on adresses
    """
    return (
        Search()
        .using(client)
        .index(BRK)
        .filter(
            'terms',
            subtype=['kadastraal_subject']
        )
        .query(
            multimatch_subject_Q(query)
        ).sort(*add_sorting())
    )


def search_object_query(view, client, query):
    """
    Execute search in Objects
    """
    return (
        Search()
        .using(client)
        .index(BRK)
        .filter(
            'terms',
            subtype=['kadastraal_object']
        )
        .query(
            match_object_Q(query)
        )
        .sort(*add_sorting())
    )


def search_openbare_ruimte_query(view, client, query):
    """
    Execute search in Objects
    """
    return (
        Search()
        .using(client)
        .index(BAG)
        .query(
            multimatch_openbare_ruimte_Q(query)
        )
        .sort(*add_sorting_ob())
    )


def search_nummeraanduiding_query(view, client, query):
    """
    Execute search in Objects
    """

    straatnaam = query.split()[0]

    search = (
        Search()
        .using(client)
        .index(NUMMERAANDUIDING)
        .query(
            'function_score',
            query=Q(
                'bool',
                filter=[straatnaam_Q(straatnaam)],
                should=[
                    huisnummer_Q(query),
                    toevoeging_Q(query),
                    huisletters_Q(query),

                    multimatch_adres_Q(query),
                    straatnaam_Q(straatnaam),
                    postcode_Q(query),

                    adres_Q(query),

                    # huisnummer_variation_Q(query)

                ],
                minimum_should_match=2,
            )
        ).sort(*add_nummerduiding_sorting())
    )


     #functions=[
     #    query_dsl.SF(
     #        'script_score',
     #        script="_score + (_score/(doc['huisnummer'].value + 1.0))"
     #    )
     #]

    # if settings.TESTING:
    #    search.params(search_type='dfs_query_then_fetch')

    return search


def test_search_query(view, client, query):
    """
    Do test experiments here..
    """

    s = Search() \
        .using(client) \
        .index(NUMMERAANDUIDING, BAG, BRK) \
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
                  'straatnaam_all',
                  'aanduiding',
                  'adres',

                  'postcode',
                  'huisnummer_variation',
                  'type'
              ],
              ),
    )

    # .sort(*add_sorting())

    # add aggregations
    a = A('terms', field='subtype', size=100)
    # b = A('terms', field='_type', size=100)

    # tops = A('top_hits', size=1)

    s.aggs.bucket('by_subtype', a)
    # s.aggs.bucket('by_type', b)

    # give back top results
    # s.aggs.bucket('by_type', b).bucket('top', tops)

    return s


def kadaster_Q(query):

    match_fields = [
        "naam",
        "aanduiding",
    ]

    return Q(
        "multi_match",
        query=query,
        type="phrase_prefix",
        fields=match_fields)


# matches at least with a straatnaam
def straatnaam_Q(query):

    match_fields = [
        "naam",
        "straatnaam_var",
        "straatnaam_all",
        "adres",
        "postcode",
    ]

    return Q(
        "multi_match",
        type="phrase_prefix",
        query=query,
        prefix_length=1,
        fields=match_fields)


def openbare_ruimte_variation_Q(query):

    match_fields = [
        "naam_var",
    ]

    return Q(
        "multi_match",
        type="phrase_prefix",
        query=query,
        boost=3,
        prefix_length=1,
        fields=match_fields)


def straatnaam_variation_Q(query):

    match_fields = [
        "straatnaam_var",
    ]

    return Q(
        "multi_match",
        type="phrase_prefix",
        query=query,
        boost=0.1,
        prefix_length=1,
        fields=match_fields)


def nummeraanduiding_must_Q(query):

    match_fields = [
        "straatnaam_var",
        "postcode"
    ]

    return Q(
        "multi_match",
        type="phrase_prefix",
        query=query,
        boost=0.1,
        prefix_length=1,
        fields=match_fields)


# matches at least with a straatnaam
def straatnaam_auto_Q(query):

    match_fields = [
        "straatnaam_all",
    ]

    return Q(
        "multi_match",
        type="phrase_prefix",
        query=query,
        prefix_length=2,
        fields=match_fields)


def huisnummer_Q(query):

    match_fields = [
        "huisnummer_str",
        ]

    return Q(
        "multi_match",
        query=query,
        fields=match_fields)


def huisnummer_variation_Q(query):

    match_fields = [
        "huisnummer_variation",
        "toevoeging_variation",

    ]

    return Q(
        "multi_match",
        query=query,
        boost=0.1,
        fields=match_fields)


def toevoeging_Q(query):

    match_fields = [
        "toevoeging",
    ]

    return Q(
        "multi_match",
        query=query,
        boost=1.5,
        fields=match_fields)


def huisletters_Q(query):

    match_fields = [
        "huisletter",
        "huistoevoeging"
    ]

    return Q(
        "multi_match",
        query=query,
        boost=3,
        fields=match_fields)


def naam_Q(query):

    match_fields = [
        "geslachtsnaam",
        "kadastraal_subject.naam",
    ]

    return Q(
        "multi_match",
        query=query,
        type="phrase_prefix",
        slop=12,
        prefix_length=2,
        fields=match_fields)


def postcode_Q(query):

    match_fields = [
        "postcode",
    ]

    return Q(
        "multi_match",
        query=query,
        prefix_length=2,
        fields=match_fields
    )


def adres_Q(query):

    match_fields = [
        "adres",
    ]

    return Q(
        "multi_match",
        query=query,
        boost=2,
        type="phrase_prefix",
        prefix_length=2,
        fields=match_fields
    )


def aanduiding_Q(query):

    match_fields = [
        "aanduiding",
    ]

    return Q(
        "multi_match",
        query=query,
        type="phrase_prefix",
        prefix_length=2,
        fields=match_fields
    )


def autocomplete_query(client, query):
    """
    provice autocomplete suggestions
    """

    completions = [
        "naam",

        "straatnaam",
        "straatnaam_nen",
        "straatnaam_ptt",

        "adres",
        "postcode",

        "geslachtsnaam",
        "aanduiding",
    ]

    # aggregation
    a = A('terms', field='subtype', size=4)

    tops = A('top_hits', size=5)

    search = (
        Search()
        .using(client)
        .index(BAG, BRK, NUMMERAANDUIDING)
        .query(
            'bool',
            should=[

                postcode_Q(query),

                straatnaam_Q(query),
                openbare_ruimte_variation_Q(query),
                straatnaam_variation_Q(query),

                huisnummer_Q(query),
                toevoeging_Q(query),
                huisletters_Q(query),

                naam_Q(query),

                kadaster_Q(query),

                fuzzy_Q(query)
            ],
            minimum_should_match=1
        )
        .highlight(*completions, pre_tags=[''], post_tags=[''])
        # .sort(*add_sorting())
    )

    search.aggs.bucket('by_subtype', a).bucket('top', tops)

    if settings.DEBUG or settings.TESTING:
        sq = search.to_dict()
        import json
        print
        print(json.dumps(sq, indent=4))
        print

    return search


def _add_aggregation_counts(result, matches):

    # go add aggregations counts to keys
    for bucket in result.aggregations['by_subtype']['buckets']:
        items = matches.get(bucket.key, [])
        subtype_key = '%s ~ %s' % (bucket.key, bucket.doc_count)
        matches.pop(bucket.key, None)
        matches[subtype_key] = items

    # if items are empty. add top hits?


def _order_matches(matches):
    for sub_type in matches.keys():
        count_values = sorted(
            [(count, m)
                for m, count in matches[sub_type].items()], reverse=True)

        matches[sub_type] = [
            dict(item=m, score=count) for count, m in count_values[:5]]


def _filter_highlights(highlight, sub_type, query, matches):
    """
    Given auto complete highligts make sure query matches suggestion
    """
    for key in highlight:
        found_highlights = highlight[key]

        for match_field_value in found_highlights:
            # #make sure query is in the match
            q = query.lower()
            mf = match_field_value.lower()
            if not mf.startswith(q):
                if q not in mf:
                    continue

            old = matches[sub_type].setdefault(match_field_value, 0)
            # import ipdb; ipdb.set_trace()
            matches[sub_type][match_field_value] = old + 1


def _determine_sub_type(hit):

    if not hasattr(hit, 'subtype'):
        sub_type = hit.meta.doc_type
        log.debug('subtype missing %s' % hit)
    else:
        # this should always be the case
        sub_type = hit.subtype

    return sub_type


def get_autocomplete_response(client, query):

    result = autocomplete_query(client, query).execute()

    matches = OrderedDict()

    # group_sugestions by sub_type
    for hit in result:

        # import ipdb; ipdb.set_trace()
        sub_type = _determine_sub_type(hit)

        if sub_type not in matches:
            matches[sub_type] = OrderedDict()

        if 'highlight' not in hit.meta:
            continue

        highlight = hit.meta.highlight

        _filter_highlights(highlight, sub_type, query, matches)

    _order_matches(matches)

    _add_aggregation_counts(result, matches)

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

        response = get_autocomplete_response(self.client, query)

        return Response(response)


class TypeaheadViewSet(TypeaheadViewSetOld):

    def get_autocomplete_response(self, client, query):
        return get_autocomplete_response(client, query)

    def list(self, request, *args, **kwargs):
        """
        Show autocomplete results

        *NOTE*

        We assume spelling errors and therefore it is possible
        to have unexpected results

        ---
        parameters_strategy: merge

        parameters:
            - name: q
              description: Autcomplete straatnaam / kadaster..
              required: true
              type: string
              paramType: query
        """

        return super(TypeaheadViewSet, self).list(
            request, *args, **kwargs)


class SearchViewSet(viewsets.ViewSet):
    """
    Given a query parameter `q`, this function returns a subset of all objects
    that match the elastic search query in the 'basisregistratie'

    *NOTE*

    We assume the input is correct but could be incomplete

    for example: seaching for a not existing
    Rozengracht 3 will return Rozengracht 3-1 which does exist.

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
        elif page > 9:
            next_page = "pageing over search results is stupid!"
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
        """
        ---
        parameters_strategy: merge

        parameters:
            - name: q
              description: Zoek in basisregistraties
              required: true
              type: string
              paramType: query
        """

        if 'q' not in request.query_params:
            return Response([])

        page = 1
        if 'page' in request.query_params:
            # limit search results pageing in elastic is slow
            page = int(request.query_params['page'])
            if page > 10:
                page = 10

        start = ((page - 1) * self.page_size)
        end = (page * self.page_size)

        query = request.query_params['q']

        client = Elasticsearch(
            settings.ELASTIC_SEARCH_HOSTS,
            raise_on_error=True
        )

        search = self.search_query(client, query)[start:end]

        if settings.DEBUG or settings.TESTING:
            sq = search.to_dict()
            import json
            print(json.dumps(sq, indent=4))

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

    def normalize_bucket(self, field, request):
        result = OrderedDict()
        result.update(field.to_dict())
        return result

    def get_url(self, request, hit):
        """
        """
        return _get_url(request, hit)

    def normalize_hit(self, hit, request):
        result = OrderedDict()
        result['_links'] = self.get_url(request, hit)

        result['type'] = hit.meta.doc_type
        result['dataset'] = hit.meta.index
        result['score'] = hit.meta.score
        # result['uri'] = _get_url(
        #     request, hit.meta.doc_type, hit.meta.id) + "?full"
        result.update(hit.to_dict())

        return result


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

    def list(self, request, *args, **kwargs):
        """
        Show kadastraal subject search results

        ---
        parameters_strategy: merge

        parameters:
            - name: q
              description: Zoek op kadastraal subject
              required: true
              type: string
              paramType: query
        """

        return super(SearchSubjectViewSet, self).list(
            request, *args, **kwargs)


class SearchObjectViewSet(SearchViewSet):
    """
    Given a query parameter `q`, this function returns a subset of all
    grond percelen objects that match the elastic search query.
    """

    url_name = 'search/kadastraalobject-list'
    search_query = search_object_query

    def list(self, request, *args, **kwargs):
        """
        Show kadastral object search results

        ---
        parameters_strategy: merge

        parameters:
            - name: q
              description: Zoek kadastraal object
              required: true
              type: string
              paramType: query
        """

        return super(SearchObjectViewSet, self).list(
            request, *args, **kwargs)


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

    def list(self, request, *args, **kwargs):
        """
        Show openbare ruimte results

        ---
        parameters_strategy: merge

        parameters:
            - name: q
              description: Zoek op openbare ruimte
              required: true
              type: string
              paramType: query
        """

        return super(SearchOpenbareRuimteViewSet, self).list(
            request, *args, **kwargs)


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
    # search_query = search_adres_query

    def list(self, request, *args, **kwargs):
        """
        Show adres/nummeraanduiding search results

        ---
        parameters_strategy: merge

        parameters:
            - name: q
              description: Zoek op adres / nummeraanduiding
              required: true
              type: string
              paramType: query
        """

        return super(SearchNummeraanduidingViewSet, self).list(
            request, *args, **kwargs)


class SearchTestViewSet(SearchViewSet):
    url_name = 'search/test-list'
    search_query = test_search_query

    def list(self, request, *args, **kwargs):
        """
        Show test search results

        ---
        parameters_strategy: merge

        parameters:
            - name: q
              description: Zoek op met test functie..(DEVELOPMENT ONLY)
              required: true
              type: string
              paramType: query
        """

        return super(SearchTestViewSet, self).list(
            request, *args, **kwargs)
