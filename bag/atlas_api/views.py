# Python
from collections import OrderedDict
import json
import logging
from urllib.parse import quote, urlparse

# input validation
from atlas_api.input_handling import clean_tokenize
from atlas_api.input_handling import is_postcode
from atlas_api.input_handling import is_postcode_huisnummer
from atlas_api.input_handling import is_straat_huisnummer
from atlas_api.input_handling import is_kadaster_object
from atlas_api.input_handling import is_gemeente_kadaster_object
from atlas_api.input_handling import is_bouwblok
from atlas_api.input_handling import is_meetbout
from atlas_api.input_handling import first_number


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


def prepare_input(query_string: str):
    """
    -Cleanup string
    -Tokenize create tokens
    -Find first occurence of number
    """
    qs, tokens = clean_tokenize(query_string)
    i, num = first_number(tokens)
    return qs, tokens, i


def analyze_query(query_string: str, tokens: list, i: int):
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
    # Too little informatation to search on
    if len(query_string) < 2:
        return []

    # A collection of regex and the query they generate
    query_selector = [
        {
            'test':  is_postcode,
            'query': [bagQ.is_postcode_Q],
        },
        {
            'test': is_bouwblok,
            'query': [bagQ.bouwblok_Q],
        },
        {
            'test': is_meetbout,
            'query': [genQ.meetbout_Q],
        },
        {
            'test': is_postcode_huisnummer,
            'query': [bagQ.postcode_huisnummer_Q],
        },
        {
            'test': is_kadaster_object,
            'query': [brkQ.kadaster_object_Q],
        },
        {   # support Amsterdam S .. kadaster notations
            'test': is_gemeente_kadaster_object,
            'query': [brkQ.gemeente_object_Q],
        },

        {
            'test': is_straat_huisnummer,
            'query': [
                bagQ.straat_huisnummer_Q,
                brkQ.kadaster_subject_Q,
            ],
        },
    ]

    queries = []

    for option in query_selector:
        if option['test'](query_string, tokens):
            queries.extend(
                option['query']
            )
            # only match one query!
            # this maybe needs to change in the future
            # but should be avoided if possible
            break

    # Checking for a case in which no matches are found.
    # In which case, defaulting to address/openbare ruimte
    if not queries:
        queries.extend([
            bagQ.weg_Q,
            brkQ.kadaster_subject_Q,
        ])

    result_queries = []

    # FIXME superqueries
    for q in queries:
        result_queries.append(q(query_string, tokens=tokens, num=i))

    return result_queries


def prepare_query_string(query_string: str):
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
    """
    Given an elk hit determine the uri for each hit
    """

    doc_type, id = hit.meta.doc_type, hit.meta.id

    if hasattr(hit, 'subtype_id'):
        id = hit.subtype_id if hit.subtype_id else id

    if doc_type in _details:
        return rest.get_links(
            view_name=_details[doc_type],
            kwargs={'pk': id}, request=request)

    if doc_type == 'meetbout':
        return {
            'self': {
                'href': '/meetbouten/meetbout/{}'.format(id)
            }
        }

    # hit must have subtype
    assert hit.subtype

    if hit.subtype in _details:
        return rest.get_links(
            view_name=_details[hit.subtype],
            kwargs={'pk': id}, request=request)

    return None


class QueryMetadata(metadata.SimpleMetadata):
    def determine_metadata(self, request, view):
        result = super().determine_metadata(request, view)
        result['parameters'] = {
            'q': {
                'type': 'string',
                'description': 'The query to search for',
                'required': False,
            },
        }
        return result


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

    We use many datasets by trying to guess about the input
    - adresses, public spaces, bouwblok, meetbouten

    """
    metadata_class = QueryMetadata

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.client = Elasticsearch(settings.ELASTIC_SEARCH_HOSTS)

    def autocomplete_queries(self, query):
        """provice autocomplete suggestions"""

        # i = index first number in tokens
        query_clean, tokens, i = prepare_input(query)

        query_components = analyze_query(query_clean, tokens, i)

        indexes = [BAG, BRK, NUMMERAANDUIDING]

        result_data = []

        size = 15     # default size

        # Ignoring cache in case debug is on
        ignore_cache = settings.DEBUG

        # create elk queries
        for q in query_components:

            if 'Index' in q:
                indexes = q['Index']

            search = (
                Search()
                .using(self.client)
                .index(*indexes)
                .query(q['Q'])
                )

            if 's' in q:
                search = search.sort(*q['s'])

            if 'size' in q:
                size = q['size']

            search = search[0:size]

            # get the result from elastic
            try:
                result = search.execute(ignore_cache=ignore_cache)
            except:
                log.error(
                    'FAILED ELK SEARCH: %s', json.dumps(search.to_dict()))
                continue

            # apply custom sorting.
            if 'sorting' in q:
                result = q['sorting'](result, query_clean, tokens, i)

            # Get the datas!
            result_data.append(result)

            # nice prety printing
            if settings.DEBUG:
                sq = search.to_dict()
                msg = json.dumps(sq, indent=4)
                print(msg)
                logging.debug(msg)

        return result_data

    def _get_uri(self, request, hit):
        # Retrieves the uri part for an item
        url = _get_url(request, hit)['self']['href']
        uri = urlparse(url).path[1:]
        return uri

    def _order_results(self, results, query_string, request):
        """

        @Params
        result - the elastic search result object
        query_string - the query string used to search for. This is for exact
                       match recognition
        """
        result_sets = {}

        ordered_results = []

        result_order = [
            'weg', 'verblijfsobject', 'bouwblok', 'kadastraal_subject',
            'kadastraal_object', 'meetbout']

        # This might be better handled on the front end
        pretty_names = [
            'Straatnamen', 'Adres', 'Bouwblok',
            'Kadastrale subjecten', 'Kadastrale objecten',
            'Meetbouten'
        ]

        # Organizing the results
        for elk_result in results:
            for hit in elk_result:
                disp = hit._display
                uri = self._get_uri(request, hit)
                # Only add results we generate uri for
                # @TODO this should not be used like this as result filter

                if not uri:
                    logging.debug('No uri', hit)
                    continue

                if hit.subtype not in result_sets:
                    result_sets[hit.subtype] = []

                result_sets[hit.subtype].append({
                    '_display': disp,
                    'query': disp,
                    'uri': uri
                })

        # Now ordereing the result groups
        for i in range(len(result_order)):
            if result_order[i] in result_sets:
                ordered_results.append({
                    'label': pretty_names[i],
                    'content': result_sets[result_order[i]],
                })

        return ordered_results

    def get_autocomplete_response(self, query, request, alphabetical=True):
        """
        Sends a request for auto complete and returns the result
        @ TODO there are more efficent ways to return the data

        Optional flag alphabetical is used to determine if the results
        should be alphabetically ordered. Defaults to True
        """

        results = self.autocomplete_queries(query)

        # Checking if there was aggregation in the autocomplete.
        # If there was that is what should be used for resutls
        # Trying aggregation as most autocorrect will have them
        # matches = OrderedDict()
        res = self._order_results(results, query, request)

        return res

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

        response = self.get_autocomplete_response(query, request)

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

    def search_query(self, client, query, tokens, i):
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
        query, tokens, i = prepare_input(query)

        client = Elasticsearch(
            settings.ELASTIC_SEARCH_HOSTS,
            raise_on_error=True
        )

        search = self.search_query(client, query, tokens, i)[start:end]

        ignore_cache = settings.DEBUG

        if settings.DEBUG:
            if search:
                log.debug(search.to_dict())
                sq = search.to_dict()
                print(json.dumps(sq, indent=4))

        if not search:
            log.debug('no elk query')
            return Response([])

        try:
            result = search.execute(ignore_cache=ignore_cache)
        except TransportError:
            log.exception("Could not execute search query " + query)
            # Todo fix this
            # https://github.com/elastic/elasticsearch/issues/11340#issuecomment-105433439
            return Response([])

        response = OrderedDict()

        self._set_followup_url(request, result, end, response, query, page)

        count = result.hits.total
        response['count_hits'] = count
        response['count'] = count

        self.create_summary_aggregations(request, result, response)
        # if hits are > 3 and < 1000
        # custom sorting?
        ordered_results = self.custom_sorting(result.hits, query, tokens, i)

        response['results'] = [
            self.normalize_hit(h, request) for h in ordered_results]

        return Response(response)

    def custom_sorting(self, result_hits: list,
                       query: str, tokens: list, i: int):

        return result_hits

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

    def search_query(self, client, query, tokens, i):
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

    def search_query(self, client, query, tokens, i):
        """
        Execute search in Objects
        """
        queries = []

        if is_gemeente_kadaster_object(query, tokens):
            queries = [
                brkQ.gemeente_object_Q(query, tokens=tokens, num=i)['Q']]
        elif is_kadaster_object(query, tokens):
            queries = [
                brkQ.kadaster_object_Q(query, tokens=tokens, num=i)['Q']]

        if not queries:
            return []

        return (
            Search()
            .using(client)
            .index(BRK)
            .filter(
                'terms',
                subtype=['kadastraal_object']
            )
            .query(
                *queries
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

    def search_query(self, client, query, tokens, i):
        """
        Execute search in Objects
        """
        query, tokens, i = prepare_input(query)

        return (
            Search()
            .using(client)
            .index(BAG)
            .filter(
                'terms',
                subtype=['bouwblok']
            )
            .query(
                bagQ.bouwblok_Q(query, tokens)['Q']
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

    def search_query(self, client, query, tokens, i):
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
    custom_sort = True

    def search_query(self, client, query, tokens, i):
        """
        Execute search in Objects
        """
        queries = []

        if is_postcode_huisnummer(query, tokens):
            queries = [
                bagQ.postcode_huisnummer_exact_Q(
                    query, tokens=tokens, num=i)['Q']]

        elif is_straat_huisnummer(query, tokens):
            queries = [
                bagQ.tokens_comp_address_Q(query, tokens=tokens, num=i)['Q']]

        if not queries:
            queries = [bagQ.search_streetname_Q(query)['Q']]

        # default response search roads
        return (
            Search()
            .using(client)
            .index(NUMMERAANDUIDING)
            .query(*queries)
        )

    def custom_sorting(self, elk_results, query, tokens, i):
        """
        Sort by relevant street and then numbers
        """
        if is_postcode_huisnummer(query, tokens):
            i = 2

        if i < 1:
            return bagQ.vbo_straat_sorting(elk_results, query, tokens, i)

        return bagQ.straat_huisnummer_sorting(elk_results, query, tokens, i)


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

    def search_query(self, client, query, tokens, i):
        """Creating the actual query to ES"""

        if is_postcode_huisnummer(query, tokens):
            query = [
                bagQ.postcode_huisnummer_Q(
                    query,
                    tokens=tokens, num=2)['Q'],
            ]
        else:
            postcode = "".join(tokens[:2])
            query = [
                bagQ.weg_Q(postcode)['Q']
            ]

        return (
            Search()
            .using(client)
            .index(BAG, NUMMERAANDUIDING)
            .query(
                'bool',
                should=query
            )
        )

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
        # Under 6 characters there is not enough information
        if len(norm) > 6:
            if norm[6] in ['-', '_', '/', '.', ',', '+']:
                norm = "{0} {1}".format(norm[:6], norm[7:])
            elif norm[6] != ' ':
                # It seems that the house nummer is directly attached
                try:
                    int(norm[6])
                except ValueError:
                    # The format is unclear
                    norm = pc_num
        return norm

    def search_query(self, client, query, tokens, i):
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
