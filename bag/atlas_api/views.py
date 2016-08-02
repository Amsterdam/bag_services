# Python
import json
import logging
from collections import OrderedDict
from collections import defaultdict
from urllib.parse import quote, urlparse

from django.conf import settings
from django.contrib.gis.geos import Point
from elasticsearch import Elasticsearch
from elasticsearch.exceptions import TransportError
from elasticsearch_dsl import Search
from rest_framework import viewsets, metadata
from rest_framework.response import Response
from rest_framework.reverse import reverse

from atlas_api.input_handling import clean_tokenize
from atlas_api.input_handling import first_number
from datasets.bag import queries as bagQ
from datasets.brk import queries as brkQ
from datasets.generic import queries as genQ
from datasets.generic import rest
from datasets.generic.queries import ElasticQueryWrapper
from datasets.generic.query_analyzer import QueryAnalyzer

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

    'buurt': 'buurt-detail',
    'unesco': 'unesco-detail',
    'buurtcombinatie': 'buurtcombinatie-detail',
    'gebiedsgerichtwerken': 'gebiedsgerichtwerken-detail',
    'stadsdeel': 'stadsdeel-detail',

    'grootstedelijk': 'grootstedelijkgebied-detail',
    'woonplaats': 'woonplaats-detail',
}

# autocomplete_group_sizes
_autocomplete_group_sizes = {
    'Straatnamen': 8,
    'Adres': 8,
    'Gebieden': 5,
    'Kadastrale objecten': 8,
    'Kadastrale subjecten': 5,
    'Bouwblok': 5,
    'Meetbouten': 5,
}

_autocomplete_group_order = [
    'Straatnamen',
    'Adres',
    'Gebieden',
    'Kadastrale objecten',
    'Kadastrale subjecten',
    'Bouwblok',
    'Meetbouten',
]

_subtype_mapping = {
    'weg': 'Straatnamen',
    'verblijfsobject': 'Adres',
    'ligplaats': 'Adres',
    'standplaats': 'Adres',
    'kadastraal_object': 'Kadastrale objecten',
    'kadastraal_subject': 'Kadastrale subjecten',
    'gemeente': 'Gebieden',
    'woonplaats': 'Gebieden',
    'unesco': 'Gebieden',
    'grootstedelijk': 'Gebieden',
    'stadsdeel': 'Gebieden',
    'gebiedsgerichtwerken': 'Gebieden',
    'buurtcombinatie': 'Gebieden',
    'buurt': 'Gebieden',
    'bouwblok': 'Bouwblok',
    'meetbout': 'Meetbouten',
}


def prepare_input(query_string: str):
    """
    -Cleanup string
    -Tokenize create tokens
    -Find first occurence of number, NOTE in the future give array of numbers?
    """
    qs, tokens = clean_tokenize(query_string)
    i, num = first_number(tokens)
    return qs, tokens, i


def select_queries(query_string: str) -> [ElasticQueryWrapper]:
    """
    Looks at the query string being filled and tries
    to make conclusions about what is actually being searched.
    This is useful to reduce the number of queries and reduce the result size

    Returns a list of queries that should be used
    """
    # Too little information to search on
    if len(query_string) < 2:
        return []

    analyzer = QueryAnalyzer(query_string)

    # A collection of regex and the query they generate
    query_selectors = [
        {
            'test': analyzer.is_postcode_prefix,
            'query': bagQ.postcode_query,
        },
        {
            'test': analyzer.is_bouwblok_exact,
            'query': bagQ.bouwblok_query,
        },
        {
            'test': analyzer.is_meetbout_prefix,
            'query': genQ.meetbout_query,
        },
        {
            'test': analyzer.is_postcode_huisnummer_prefix,
            'query': bagQ.postcode_huisnummer_query,
        },
        {
            'test': analyzer.is_kadastraal_object_prefix,
            'query': brkQ.kadastraal_object_query,
        },
        {
            'test': analyzer.is_straatnaam_huisnummer_prefix,
            'query': bagQ.straatnaam_huisnummer_query,
        },
    ]

    queries = [s['query'] for s in query_selectors if s['test']()]
    if len(queries) > 1:
        # beperk tot 1 query. Voor nu in elk geval.
        queries = queries[:1]

    # Checking for a case in which no matches are found.
    # In which case, defaulting to address/openbare ruimte
    if not queries:
        queries = [
            bagQ.weg_query,
            bagQ.gebied_query,
            brkQ.kadastraal_subject_query,
        ]

    return [q(analyzer) for q in queries]


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
        if hit.subtype in ['gemeente']:
            return rest.get_links(
                view_name=_details[hit.subtype],
                kwargs={'pk': hit.naam}, request=request)
        return rest.get_links(
            view_name=_details[hit.subtype],
            kwargs={'pk': id}, request=request)

    return {
        'self': {
            'href': '/{}/{}/{}/notworking'.format(doc_type, hit.subtype, id)
        }
    }


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
        """provide autocomplete suggestions"""

        query_components = select_queries(query)

        result_data = []

        # Ignoring cache in case debug is on
        ignore_cache = settings.DEBUG

        # create elk queries
        for q in query_components:  # type: ElasticQueryWrapper

            search = q.to_elasticsearch_object(self.client)

            # get the result from elastic
            try:
                result = search.execute(ignore_cache=ignore_cache)
            except:
                log.exception('FAILED ELK SEARCH: %s', json.dumps(search.to_dict()))
                continue

            # apply custom sorting.
            if q.custom_sort_function:
                # i = index first number in tokens
                query_clean, tokens, i = prepare_input(query)
                result = q.custom_sort_function(result, query_clean, tokens, i)

            # Get the datas!
            result_data.append(result)

        return result_data

    def _get_uri(self, request, hit):
        # Retrieves the uri part for an item
        url = _get_url(request, hit)['self']['href']
        uri = urlparse(url).path[1:]
        return uri

    def _group_elk_results(self, request, results):
        """
        Group the elk results in their pretty name groups
        """
        flat_results = (hit for r in results for hit in r)
        result_groups = defaultdict(list)

        for hit in flat_results:
            group = _subtype_mapping[hit.subtype]
            result_groups[group].append({
                '_display': hit._display,
                'uri': self._get_uri(request, hit)
            })

        return result_groups

    def _order_results(self, results, request):
        """
        Group the elastic search results and order these groups

        @Params
        result - the elastic search result object
        query_string - the query string used to search for. This is for exact
                       match recognition
        """

        # put the elk results in subtype groups
        result_groups = self._group_elk_results(request, results)

        ordered_results = []

        for group in _autocomplete_group_order:
            if group not in result_groups:
                continue

            size = _autocomplete_group_sizes[group]

            ordered_results.append({
                'label': group,
                'content': result_groups[group][:size]
            })

        return ordered_results

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

        query = request.query_params['q']
        if not query:
            return Response([])

        results = self.autocomplete_queries(query)
        response = self._order_results(results, request)

        return Response(response)


class SearchViewSet(viewsets.ViewSet):
    """
    Base class for ViewSets implementing search.
    """

    metadata_class = QueryMetadata
    page_size = 100
    url_name = 'search-list'
    page_limit = 10

    def search_query(self, client, analyzer: QueryAnalyzer) -> Search:
        """
        Construct the search query that is executed by this view set.
        """
        raise NotImplementedError

    def _set_followup_url(self, request, result, end,
                          response, query, page):
        """
        Add paging links for result set to response object
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

        query = request.query_params['q']
        analyzer = QueryAnalyzer(query)
        query, tokens, i = prepare_input(query)

        client = Elasticsearch(
            settings.ELASTIC_SEARCH_HOSTS,
            raise_on_error=True
        )

        search = self.search_query(client, analyzer)[start:end]

        if not search:
            log.debug('no elk query')
            return Response([])

        ignore_cache = settings.DEBUG

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

        ordered_results = self.custom_sorting(result.hits, query, tokens, i)

        response['results'] = [self.normalize_hit(h, request)
                               for h in ordered_results]

        return Response(response)

    def custom_sorting(self, result_hits: list,
                       query: str, tokens: [str], i: int):
        return result_hits

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

    def search_query(self, client, analyzer: QueryAnalyzer) -> Search:
        """
        Execute search on Subject
        """
        search = brkQ.kadastraal_subject_query(analyzer).to_elasticsearch_object(client)
        return search.filter('terms', subtype=['kadastraal_subject'])


class SearchObjectViewSet(SearchViewSet):
    """
    Given a query parameter `q`, this function returns a subset of all
    grond percelen objects that match the elastic search query.
    """

    url_name = 'search/kadastraalobject-list'

    def search_query(self, client, analyzer: QueryAnalyzer) -> Search:
        """
        Execute search in Objects
        """
        if not analyzer.is_kadastraal_object_prefix():
            return []

        search = brkQ.kadastraal_object_query(analyzer).to_elasticsearch_object(client)
        return search.filter('terms', subtype=['kadastraal_object'])


class SearchBouwblokViewSet(SearchViewSet):
    """
    Given a query parameter `q`, this function returns a subset of all
    grond percelen objects that match the elastic search query.
    """

    url_name = 'search/bouwblok-list'

    def search_query(self, client, analyzer: QueryAnalyzer) -> Search:
        """
        Execute search in Objects
        """
        if not analyzer.is_bouwblok_prefix():
            return []

        search = bagQ.bouwblok_query(analyzer).to_elasticsearch_object(client)
        return search.filter('terms', subtype=['bouwblok'])


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

    def search_query(self, client, analyzer: QueryAnalyzer) -> Search:
        """
        Execute search in Objects
        """
        search_data = bagQ.openbare_ruimte_query(analyzer)
        return search_data.to_elasticsearch_object(client)

    def custom_sorting(self, elk_results, query, tokens, i):
        """
        Sort by prefix match and then relevance
        """
        return bagQ.weg_sorting(elk_results, query, tokens, i)


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

    def search_query(self, client, analyzer: QueryAnalyzer) -> Search:
        """
        Execute search in Objects
        """
        q = None

        if analyzer.is_postcode_huisnummer_prefix():
            q = bagQ.postcode_huisnummer_exact_query(analyzer)

        elif analyzer.is_straatnaam_huisnummer_prefix():
            q = bagQ.straatnaam_huisnummer_query(analyzer)

        if not q:
            q = bagQ.straatnaam_query(analyzer)

        # default response search roads
        return q.to_elasticsearch_object(client)


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

    def search_query(self, client, analyzer: QueryAnalyzer) -> Search:
        """Creating the actual query to ES"""

        if analyzer.is_postcode_huisnummer_prefix():
            return bagQ.postcode_huisnummer_query(analyzer).to_elasticsearch_object(client)
        else:
            return bagQ.weg_query(analyzer).to_elasticsearch_object(client)


class SearchExactPostcodeToevoegingViewSet(viewsets.ViewSet):
    """
    Exact match lookup for a postcode and house number with extensions.

    Returns either 1 result for the exact match or 0 if non is found.
    This endpoint is used for the geocodering of addresses for the
    afvalophalgebieden.
    """

    metadata_class = QueryMetadata

    def search_query(self, client, analyzer: QueryAnalyzer) -> Search:
        """
        Execute search in Objects
        """
        return bagQ.postcode_huisnummer_exact_query(analyzer).to_elasticsearch_object(client)

    def list(self, request, *args, **kwargs):
        """
        Show search results

        ---
        parameters:
            - name: q
              description: Zoek specifiek adres / nummeraanduiding
              required: true
              type: string
              paramType: query
        """

        if 'q' not in request.query_params:
            return Response([])

        analyzer = QueryAnalyzer(request.query_params['q'])

        # Making sure a house number is present
        # There should be a minimum of 3 tokens:
        # postcode number, postcode letters and house number
        if not analyzer.is_postcode_huisnummer_prefix():
            return Response([])

        client = Elasticsearch(
            settings.ELASTIC_SEARCH_HOSTS,
            raise_on_error=True
        )

        # Ignoring cache in case debug is on
        ignore_cache = settings.DEBUG
        search = self.search_query(client, analyzer)
        response = search.execute(ignore_cache=ignore_cache)

        # Getting the first response.
        # Either there is only one, or a housenumber was given
        # where only extensions are available, in which case any result will do
        if response and response.hits:
            response = response.hits[0].to_dict()
            # Adding RD gepopoint
            if 'centroid' in response:
                rd_point = Point(*response['centroid'], srid=4326)
                # Using the newly generated point to
                # replace the elastic results
                # with geojson
                response['geometrie'] = json.loads(rd_point.geojson)
                rd_point.transform(28992)
                response['geometrie_rd'] = json.loads(rd_point.geojson)
                # Removing the poscode based fields from the results
                # del(response['postcode_toevoeging'])
                # del(response['postcode_huisnummer'])
        else:
            response = []
        return Response(response)
