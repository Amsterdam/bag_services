# Python
import logging
from collections import OrderedDict
import re
# Packages
from django.conf import settings
from elasticsearch import Elasticsearch
from elasticsearch.exceptions import TransportError
from elasticsearch_dsl import Search, Q, A
from rest_framework import viewsets, metadata
from rest_framework.response import Response
from rest_framework.reverse import reverse
# Project
from datasets.bag import queries as bagQ
from datasets.brk import queries as brkQ
from datasets.generic import rest


log = logging.getLogger('search')
# Regexes for query analysis
#-----------------------------
# Postcode regex matches 4 digits, possible dash or space then 0-2 letters
PCODE_REGEX = re.compile('^[1-9]\d{3}[ \-]?[a-zA-Z]?[a-zA-Z]?$')
KADASTRAL_NUMMER_REGEX = re.compile('^$')

MAX_AGG_RES = 7
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


def analyze_query(query_string):
    """
    Looks at the query string being filled and tryes
    to make conclusions about what is actually being searched.
    This is useful to reduce number of queries and reduce result size

    Looking for:
    - Only a number
    - 4 digit number and 1 or 2 letters
    - String and number

    returns a list of queryes that should be used
    """
    # If its only numbers and it is 3 digits or less its probably postcode
    # but can also be kadestral
    num = None
    try:
        num = int(query_string)
        if len(query_string) < 4:
            # Its a number so it can be either postcode or kadaster
            return [bagQ.postcode_Q]
    except ValueError:
        # Not a number
        pass
    # Checking postcode
    pcode = PCODE_REGEX.match(query_string)
    if pcode:
        return [bagQ.postcode_Q]
    # Could not draw conclussions
    return [brkQ.kadaster_subject_Q, brkQ.kadaster_object_Q, bagQ.street_name_Q, bagQ.comp_address_Q]
    
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



def wildcard_Q(query):
    """Create query/aggregation for wildcard search"""
    wildcard = '*{}*'.format(query)
    return {
        'A': None,
        'Q': Q(
            "wildcard",
            naam=dict(value=wildcard),
        )
    }


def fuzzy_Q(query):
    """Create query/aggregation for fuzzy search"""
    fuzzy_fields = [
        'openbare_ruimte.naam',
        'kadastraal_subject.geslachtsnaam',
        'adres',
        'straatnaam',
        'straatnaam_nen',
        'straatnaam_ptt',
        'postcode^2',
    ]

    return {
        'A': None,
        'Q': Q(
            "multi_match",
            query=query, fuzziness="auto",
            type="cross_fields",
            max_expansions=50,
            prefix_length=2, fields=fuzzy_fields
        )
    }

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




#=============================================
# Search view sets
#=============================================
class TypeaheadViewSet(viewsets.ViewSet):
    """
    Given a query parameter `q`, this function returns a
    subset of all objects
    that (partially) match the specified query.

    *NOTE*

    We assume spelling errors and therefore it is possible
    to have unexpected results

    """
    metadata_class = QueryMetadata
    #def get_autocomplete_response(self, client, query):
    #    return get_autocomplete_response(client, query)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.client = Elasticsearch(settings.ELASTIC_SEARCH_HOSTS)
            
    def autocomplete_query(self, query):
        """provice autocomplete suggestions"""
        query_componentes = analyze_query(query)
        quries = []
        aggs = {}
        for q in query_componentes:
            qa = q(query)
            quries.append(qa['Q'])
            if qa['A']:
                # Determining agg name
                agg_name = 'by_{}'.format(q.__name__[:-2])
                aggs[agg_name] = qa['A']
        search = (
            Search()
            .using(self.client)
            .index(BAG, BRK, NUMMERAANDUIDING)
            .query(
                'bool',
                should=quries,
            )
            #.sort(*add_sorting())
        )
        for agg_name, agg in aggs.items():
            search.aggs.bucket(agg_name, agg)

        if settings.DEBUG:
            sq = search.to_dict()
            import json
            print(json.dumps(sq, indent=4))
        return search

    def _order_agg_results(self, result, query_string, alphabetical):
        """
        Arrange the aggregated results, possibly sorting them
        alphabetically

        @Params
        result - the elastic search result object
        query_string - the query string used to search for. This is for exact match recognition
        alphabetical - flag for sorting alphabetical
        """
        max_agg_res = MAX_AGG_RES  # @TODO this should be a settings
        aggs = {}
        pcode = PCODE_REGEX.match(query_string)
        for agg in result.aggregations:
            order = []
            aggs[agg] = []
            exact = None
            for bucket in result.aggregations[agg]['buckets']:
                if bucket.key.lower() == query_string.lower() and pcode:
                    exact = bucket.key
                else:
                    order.append(bucket.key)
            # Sort the list if required
            if alphabetical:
                order.sort()
            # If there was an exact match, add it at the head of the list
            if exact:
                order = [exact] + order
            for item in order:
                aggs[agg].append({"item": item})
                max_agg_res -= 1
                if max_agg_res == 0:
                    break
            max_agg_res = MAX_AGG_RES
                        
        return aggs

    def get_autocomplete_response(self, query, alphabetical=True):
        """
        Sends a request for auto complete and returns the result
        @ TODO there are more efficent ways to return the data

        Optional flag alphabetical is used to determine if the results
        should be alphabetically ordered. Defaults to True
        """
        # Ignoring cache in case debug is on
        ignore_cache = settings.DEBUG

        result = self.autocomplete_query(query).execute(ignore_cache=ignore_cache)

        # Checking if there was aggregation in the autocomplete.
        # If there was that is what should be used for resutls
        # Trying aggregation as most autocorrect will have them
        matches = OrderedDict()
        aggs = self._order_agg_results(result, query, alphabetical)
        return aggs

    def list(self, request, *args, **kwargs):
        if 'q' not in request.query_params:
            return Response([])

        query = request.query_params['q']
        # query = query.lower()

        response = self.get_autocomplete_response(query)

        return Response(response)


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
    url_name = 'search-list'
    page_limit = 10

    def search_query(self, client, query):
        """
        Execute search.

        ./manage.py test atlas_api.tests.test_query --keepdb

        """
        log.debug('using indices %s %s %s', BAG, BRK, NUMMERAANDUIDING)

        return (
            Search()
            .using(client)
            .index(NUMMERAANDUIDING, BAG, BRK)
            .query(
                multimatch_Q(query)
            )
            .sort(*add_sorting())
        )

    def _set_followup_url(self, request, result, end,
                          response, query, page):
        """
        Add pageing links for result set to response object
        """
        # Finding link to self via reverse url search
        followup_url = reverse(self.url_name, request=request)
        response['_links'] = OrderedDict([
            ('self', {'href': followup_url}),
            ('next', {'href': None}),
            ('prev', {'href': None})
        ])

        # Finding and setting prev and next pages
        if end < result.hits.total:
            # There should be a next
            response['_links']['next']['href'] = "{}?q={}&page={}".format(followup_url, query, page + 1)
        if page == 2:
            response['_links']['previous']['href'] = "{}?q={}".format(followup_url, query)
        elif page > 2:
            response['_links']['previous']['href'] = "{}?q={}&page={}".format(followup_url, query, page - 1)

    def list(self, request, *args, **kwargs):
        """Create a response list"""
        if 'q' not in request.query_params:
            return Response([])

        page = 1
        if 'page' in request.query_params:
            # limit search results pageing in elastic is slow
            page = int(request.query_params['page'])
            if page > self.page_limit:
                page = self.page_limit

        start = ((page - 1) * self.page_size)
        end = (page * self.page_size)

        query = request.query_params['q']

        client = Elasticsearch(
            settings.ELASTIC_SEARCH_HOSTS,
            raise_on_error=True
        )

        search = self.search_query(client, query)[start:end]

        if settings.DEBUG:
            log.debug(search.to_dict())
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

        count = result.hits.total
        response['count_hits'] = count
        max_count = self.page_size * (self.page_limit + 1)
        if count > max_count:
            count = max_count
        response['count'] = count

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
        # result['uri'] = _get_url(
        #     request, hit.meta.doc_type, hit.meta.id) + "?full"
        result.update(hit.to_dict())

        return result


class SearchAdresViewSet(SearchViewSet):
    """
    Given a query parameter `q`, this function returns a subset of
    all adressable objects that match the adres elastic search query.
    """
    url_name = 'search/adres-list'

    def search_query(self, client, query):
        """
        Execute search on adresses
        """
        return (
            Search()
            .using(client)
            .index(BAG, BRK, NUMMERAANDUIDING)
            .query(
                multimatch_adres_Q(query)
            )
            .sort(*add_sorting())
        )


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

    def search_query(self, client, query):
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
                brkQ.kadaster_subject_Q(query)['Q']
            ).sort('naam.raw')
            #.sort(*add_sorting())
        )

    def list(self, request, *args, **kwargs):
        """
        Show search results

        ---
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

    def search_query(self, client, query):
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
                brkQ.kadaster_object_Q(query)['Q']
            )
            .sort('aanduiding')
        )

    def list(self, request, *args, **kwargs):
        """
        Show search results

        ---
        parameters:
            - name: q
              description: Zoek op kadastraal object
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

    def search_query(self, client, query):
        """
        Execute search in Objects
        """
        return (
            Search()
            .using(client)
            .index(BAG)
            .query(
                bagQ.public_area_Q(query)['Q']
            )
            .sort(*add_sorting())
        )

    def list(self, request, *args, **kwargs):
        """
        Show search results

        ---
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

    def search_query(self, client, query):
        """
        Execute search in Objects
        """
        return (
            Search()
            .using(client)
            .index(NUMMERAANDUIDING)
            .query(
                #multimatch_nummeraanduiding_Q(query)
                bagQ.comp_address_Q(query)['Q']
            )
        )


class SearchPostcodeViewSet(SearchViewSet):
    """
    Given a query parameter `q`, this function returns a subset
    of nummeraanduiding objects that match the elastic search query.

    Een nummeraanduiding, in de volksmond ook wel adres genoemd, is een door
    het bevoegde gemeentelijke orgaan als
    zodanig toegekende aanduiding van een verblijfsobject,
    standplaats of ligplaats.

    http://www.amsterdam.nl/stelselpedia/bag-index/catalogus-bag/objectklasse-2/

    """
    url_name = 'search/postcode-list'
    def search_query(self, client, query_string):
        """Creating the actual query to ES"""
        query = bagQ.postcode_Q(query_string)['Q']
        return (
            Search()
            .using(client)
            .index(NUMMERAANDUIDING)
            .query(query)
        ).sort('postcode.raw')

    def list(self, request, *args, **kwargs):
        """
        Show search results

        ---
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

    def search_query(self, client, query):
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
                      'straatnaam',
                      'straatnaam_nen',
                      'straatnaam_ptt',
                      'aanduiding',
                      'adres',

                      'postcode',
                      'huisnummer'
                      'huisnummer.variation',
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