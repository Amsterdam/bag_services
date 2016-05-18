# Python
from collections import OrderedDict
import json
import logging
from urllib.parse import quote
import re
# Packages
from django.conf import settings
from django.contrib.gis.geos import Point
from elasticsearch import Elasticsearch
from elasticsearch.exceptions import TransportError
from elasticsearch_dsl import Search
# from elasticsearch_dsl import Q
from rest_framework import viewsets, metadata
from rest_framework.response import Response
from rest_framework.reverse import reverse
# Project
from datasets.bag import queries as bagQ
from datasets.brk import queries as brkQ
from datasets.generic import queries as genQ
from datasets.generic import rest


log = logging.getLogger('search')

# Regexes for query analysis
# The regex are bulit on the assumption autocomplete starts at 3 characters
# Postcode regex matches 4 digits, possible dash or space then 0-2 letters
PCODE_REGEX = re.compile('^[1-9]\d{2}\d?[ \-]?[a-zA-Z]?[a-zA-Z]?$')
# Bouwblok regex matches 2 digits a letter and an optional second letter
BOUWBLOK_REGEX = re.compile('^[a-zA-Z][a-zA-Z]\d{0,2}$')
# Meetbout regex matches up to 8 digits
MEETBOUT_REGEX = re.compile('^\d{3,8}\b$')
# Address postcode regex
ADDRESS_PCODE_REGEX = re.compile('^[1-9]\d{3}[ \-]?[a-zA-Z]{2}[ \-](\d+[a-zA-Z]*)?$')

#KADASTRAL_NUMMER_REGEX = re.compile('^$')

MAX_AGG_RES = 7
# Mapping of subtypes with detail views
_details = {
    'ligplaats': 'ligplaats-detail',
    'standplaats': 'standplaats-detail',
    'verblijfsobject': 'verblijfsobject-detail',
    'openbare_ruimte': 'openbareruimte-detail',
    'kadastraal_subject': 'kadastraalsubject-detail',
    'kadastraal_object': 'kadastraalobject-detail',
    'bouwblok': 'bouwblok-detail',
}

BAG = settings.ELASTIC_INDICES['BAG']
BRK = settings.ELASTIC_INDICES['BRK']
NUMMERAANDUIDING = settings.ELASTIC_INDICES['NUMMERAANDUIDING']
MEETBOUTEN = settings.ELASTIC_INDICES['MEETBOUTEN']

def analyze_query(query_string):
    """
    Looks at the query string being filled and tries
    to make conclusions about what is actually being searched.
    This is useful to reduce number of queries and reduce result size

    Looking for:
    - Only a number, 5 digits or more -> nap bout
    - 4 digit number and 1 or 2 letters.
        space between the numer and letters is possible -> postcode
    - Two letters followed by 1 or 2 digits -> bouwblok

    returns a list of queries that should be used
    """
    # A collection of regex and the query they generate
    query_selector = [
        {
            'regex': PCODE_REGEX,
            'query': [bagQ.postcode_Q],
        }, {
            'regex': BOUWBLOK_REGEX,
            'query': [bagQ.bouwblok_Q],
        }, {
            'regex': MEETBOUT_REGEX,
            'query': [genQ.meetbout_Q],
        }, {
            'regex': ADDRESS_PCODE_REGEX,
            'query': [bagQ.comp_address_pcode_Q],
        }
    ]
    queries = []
    for option in query_selector:
        match = option['regex'].match(query_string)
        if match:
            print(option)
            queries.extend(option['query'])
    # Checking for a case in which no regex matches were
    # found. In which case, defaulting to address
    if not queries:
        queries = [
           #bagQ.street_name_and_num_Q,
           # brkQ.kadaster_subject_Q, brkQ.kadaster_object_Q, bagQ.street_name_and_num_Q,
    ]
    return queries

def prepare_query_string(query_string):
    """
    Prepares the query string for search.
    Cleaning up unsupported signes, normalize the search
    query to something we can better use etc.

    Workings:
    - Strip whitespace/EOF from the string
    - Remove '\' at the end of the string
    - Replace '"' with whitespace
    """
    query_string = query_string.strip()
    # Making sure there is a query string to work with before
    # and during \ stripping
    while query_string and (query_string[-1] == '\\'):
        query_string = query_string[:-1]
    query_string = query_string.replace('"', ' ')
    # Last strop to make sure no extra spaces are present
    query_string = query_string.strip()
    return query_string


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
    )


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


# =============================================
# Search view sets
# =============================================
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

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.client = Elasticsearch(settings.ELASTIC_SEARCH_HOSTS)

    def autocomplete_query(self, query):
        """provice autocomplete suggestions"""
        query_componentes = analyze_query(query)
        queries = []
        aggs = {}
        sorting = []
        # collect aggreagations
        for q in query_componentes:
            qa = q(query)
            queries.append(qa['Q'])
            if 'A' in qa:
                # Determining agg name
                agg_name = 'by_{}'.format(q.__name__[:-2])
                aggs[agg_name] = qa['A']
            if 'S' in qa:
                sorting.extend(qa['S'])
        search = (
            Search()
            .using(self.client)
            .index(BAG, BRK, NUMMERAANDUIDING)
            .query(
                'bool',
                should=queries,
            )
            .sort(*sorting)
        )

        # add aggregations to query
        for agg_name, agg in aggs.items():
            search.aggs.bucket(agg_name, agg)

        # nice prety printing
        if settings.DEBUG:
            sq = search.to_dict()
            import json
            print(json.dumps(sq, indent=4))

        return search

    def _choose_display_field(self, item):
        """Returns the value to set in the display field based on the object subtype"""
        try:
            if item.subtype == 'bouwblok':
                return item.code
            elif item.subtype == 'verblijfsobject':
                return item.comp_address
            else:
                print(item.subtype)
        except Exception as exp:
            # Some default
            print(exp)
            return 'def'
        return '_display'

    def _order_agg_results(self, result, query_string, alphabetical):
        """
        Arrange the aggregated results, possibly sorting them
        alphabetically

        @Params
        result - the elastic search result object
        query_string - the query string used to search for. This is for exact
                       match recognition
        alphabetical - flag for sorting alphabetical
        """
        max_agg_res = MAX_AGG_RES  # @TODO this should be a settings
        aggs = {}
        ordered_aggs = OrderedDict()
        result_order = [
            'by_postcode', 'by_street_name', 'by_comp_address', 'by_street_name_and_num',
            'by_kadaster_object', 'by_kadaster_subject']
        # This might be better handled on the front end
        pretty_names = [
            'Straatnamen', 'Straatnamen', 'Adres', 'Straatnamen',
            'Kadaster Object', 'Kadaster Subject']
        postcode = PCODE_REGEX.match(query_string)
        try:
            for agg in result.aggregations:
                order = []
                aggs[agg] = {
                    'label': 'NAME',
                    'content': []
                }
                exact = None
                for bucket in result.aggregations[agg]['buckets']:
                    if postcode and bucket.key.lower() == query_string.lower():
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
                    aggs[agg]['content'].append({
                        '_display': item,
                        'query': item,
                        'uri': 'LINK'
                    })
                    max_agg_res -= 1
                    if max_agg_res == 0:
                        break
                max_agg_res = MAX_AGG_RES
        except AttributeError:
            # No aggregation
            aggs['by_comp_address'] = {
                'label': 'Adressen',
                'content': []
            }
            for hit in result:
                disp = self._choose_display_field(hit)
                aggs['by_comp_address']['content'].append({
                    '_display': disp,
                    'query': disp,
                    'uri': 'LINK'
                })
        # Now ordereing the result groups
        # @TODO improve the working
        for i in range(len(result_order)):
            if result_order[i] in aggs:
                ordered_aggs[pretty_names[i]] = aggs[result_order[i]]
        return ordered_aggs

    def get_autocomplete_response(self, query, alphabetical=True):
        """
        Sends a request for auto complete and returns the result
        @ TODO there are more efficent ways to return the data

        Optional flag alphabetical is used to determine if the results
        should be alphabetically ordered. Defaults to True
        """
        # Ignoring cache in case debug is on
        ignore_cache = settings.DEBUG

        result = self.autocomplete_query(query).execute(
            ignore_cache=ignore_cache)

        # Checking if there was aggregation in the autocomplete.
        # If there was that is what should be used for resutls
        # Trying aggregation as most autocorrect will have them
        # matches = OrderedDict()
        print(result)
        aggs = self._order_agg_results(result, query, alphabetical)
        return aggs

    def list(self, request, *args, **kwargs):
        """
        returns result options
        ---
        parameters:
            - name: q
              description: givven search q give Result suggestions
              required: true
              type: string
              paramType: query
        """
        if 'q' not in request.query_params:
            return Response([])

        query = prepare_query_string(request.query_params['q'])
        if not query:
            return Response([])
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

        raise NotImplementedError

    def _set_followup_url(self, request, result, end,
                          response, query, page):
        """
        Add pageing links for result set to response object
        """
        # make query url friendly again
        url_query = quote(query)
        # Finding link to self via reverse url search
        followup_url = reverse(self.url_name, request=request)

        self_url = "{}?q={}&page={}".format(
            followup_url, url_query, page)

        response['_links'] = OrderedDict([
            ('self', {'href': self_url}),
            ('next', {'href': None}),
            ('prev', {'href': None})
        ])

        # Finding and setting prev and next pages
        if end < result.hits.total:
            if end < (self.page_size * self.page_limit):
                # There should be a next
                response['_links']['next']['href'] = "{}?q={}&page={}".format(
                    followup_url, url_query, page + 1)
        if page == 2:
            response['_links']['prev']['href'] = "{}?q={}".format(
                followup_url, url_query)
        elif page > 2:
            response['_links']['prev']['href'] = "{}?q={}&page={}".format(
                followup_url, url_query, page - 1)

    def list(self, request, *args, **kwargs):
        """
        Create a response list

        ---
        parameters:
            - name: q
              description: Zoek op kadastraal object
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
            if page > self.page_limit:
                page = self.page_limit

        start = ((page - 1) * self.page_size)
        end = (page * self.page_size)

        query = prepare_query_string(request.query_params['q'])

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

    def search_query(self, client, query):
        """
        Execute search on Subject
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


class SearchBouwblokViewSet(SearchViewSet):
    """
    Given a query parameter `q`, this function returns a subset of all
    grond percelen objects that match the elastic search query.
    """

    url_name = 'search/bouwblok-list'

    def search_query(self, client, query):
        """
        Execute search in Objects
        """
        return (
            Search()
            .using(client)
            .index(BAG)
            .filter(
                'terms',
                subtype=['bouwblok']
            )
            .query(
                bagQ.bouwblok_Q(query)['Q']
            )
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

        return super(SearchBouwblokViewSet, self).list(
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
                # multimatch_nummeraanduiding_Q(query)
                bagQ.comp_address_Q(query)['Q']
                # bagQ.comp_address_f_Q(query)['Q']
                # bagQ.comp_address_fuzzy_Q(query)['Q']
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

        return super(SearchPostcodeViewSet, self).list(
            request, *args, **kwargs)


class SearchExactPostcodeToevoegingViewSet(viewsets.ViewSet):
    """
    Given a query parameter `q`, this function returns a subset of all
    grond percelen objects that match the elastic search query.
    """

    metadata_class = QueryMetadata

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.client = Elasticsearch(settings.ELASTIC_SEARCH_HOSTS)

    def normalize_postcode_housenumber(self, pc_num):
        """
        Normalizes the poste code and house number so that it
        will allways look the same to the query
        Actions:
        - convert lower case to uppercase letters
        - makes sure postcode and house number are seperated by a space

        If the normalization fails, the original value is returned.
        """
        norm = pc_num.upper()
        if norm[6] in ['-', '_', '/', '.', ',']:
            norm = "{0} {1}".format(norm[:6], norm[7:])
        elif norm[6] != ' ':
            # It seems that the house nummer is directly attached
            try:
                int(norm[6])
            except ValueError:
                # The format is unclear
                norm = pc_num
        return norm

    def search_query(self, query):
        """
        Execute search in Objects
        """
        search = Search().using(self.client).index(BAG).query(
                bagQ.exact_postcode_house_number_Q(query)
            )

        if settings.DEBUG:
            sq = search.to_dict()
            import json
            print(json.dumps(sq, indent=4))
        return search

    def get_exact_response(self, query):
        """
        Sends a request for auto complete and returns the result
        @ TODO there are more efficent ways to return the data

        Optional flag alphabetical is used to determine if the results
        should be alphabetically ordered. Defaults to True
        """
        # Ignoring cache in case debug is on
        ignore_cache = settings.DEBUG

        result = self.search_query(query).execute(
            ignore_cache=ignore_cache)

        return result

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

        if 'q' not in request.query_params:
            return Response([])

        query = self.normalize_postcode_housenumber(
            prepare_query_string(request.query_params['q']))
        if not query:
            return Response([])
        response = self.get_exact_response(query)
        # Getting the first response.
        # Either there is only one, or a housenumber was given
        # where only extensions are available, in which case any result will do
        if response and response.hits:
            print(response.hits[0].to_dict())
            response = response.hits[0].to_dict()
            # Adding RD gepopoint
            rd_point = Point(*response['geometrie'], srid=4326)
            # Using the newly generated point to replace the elastic results
            # with geojson
            response['geometrie'] = json.loads(rd_point.geojson)
            rd_point.transform(28992)
            response['geometrie_rd'] = json.loads(rd_point.geojson)
            # Removing the poscode based fields from the results
            del(response['postcode_toevoeging'])
            del(response['postcode_huisnummer'])
        else:
            response = []
        return Response(response)
