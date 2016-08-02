"""
==================================================
 Individual search queries
--------------------------------------------------
 Each of these functions builds a query and,
 if needed an aggregation as well.
 They all return a dict with the Q and A keyes
==================================================
"""

# Python
import logging
import re
from collections import OrderedDict

from django.conf import settings
from elasticsearch_dsl import Q

from datasets.generic.queries import ElasticQueryWrapper
from datasets.generic.query_analyzer import QueryAnalyzer

log = logging.getLogger('bag_Q')

BAG = settings.ELASTIC_INDICES['BAG']
NUMMERAANDUIDING = settings.ELASTIC_INDICES['NUMMERAANDUIDING']


def postcode_huisnummer_query(analyzer: QueryAnalyzer) -> ElasticQueryWrapper:
    """Create query/aggregation for postcode house number search"""

    postcode, huisnummer, toevoeging = analyzer.get_postcode_huisnummer_toevoeging()

    return ElasticQueryWrapper(
        query={
            'bool': {
                'must': [
                    {
                        'term': {
                            'postcode': postcode,
                        }
                    },
                    {
                        'prefix': {
                            'toevoeging': toevoeging,
                        }
                    },
                ],
            },
        },
        indexes=[BAG, NUMMERAANDUIDING],
        sort_fields=['straatnaam.raw', 'huisnummer', 'toevoeging.raw'],
    )


def postcode_huisnummer_exact_query(analyzer: QueryAnalyzer):
    """Create query/aggregation for postcode house number search"""

    postcode, huisnummer, toevoeging = analyzer.get_postcode_huisnummer_toevoeging()

    return ElasticQueryWrapper(
        query=Q(
            'bool',
            must=[
                Q('term', postcode=postcode),
                Q('match_phrase', toevoeging=toevoeging),
                Q('term', huisnummer=huisnummer)
            ],
        ),
        sort_fields=['straatnaam.raw', 'huisnummer', 'toevoeging.raw'],
        indexes=[NUMMERAANDUIDING],

        size=1
    )


# ambtenaren sort
def vbo_natural_sort(l):
    def alphanum_key(key):
        return [t for t in re.split('([0-9]+)', key[0])]

    return sorted(l, key=alphanum_key)


def _build_sort_key(toevoeging, extra):
    # remove what user already typed
    end_part = toevoeging.replace(" ", "")

    for et in extra:
        et = et.upper()
        end_part = end_part.replace(et, '')

    return end_part


def add_to_end_result(end_result, bucket, ordered_vbo_street_num):
    """
    Add hits of ordered vbo street results to end_result
    """
    for end_p, hit in ordered_vbo_street_num:
        # flatten the endresult
        end_result.append(hit)


def _build_vbo_buckets(elk_results, extra):
    """
    Build buckets per street-num for the elk results
    keeping the results in order or the elk_score/relevance
    """
    rbs = relevant_bucket_sorted = OrderedDict()

    for r in elk_results:
        straatnaam = r.straatnaam_keyword
        bucket = straatnaam + str(r.huisnummer)

        # create sortkey for vbo street sorting
        sort_key = _build_sort_key(r.toevoeging, extra)
        # group results by streetnames
        street_result = rbs.setdefault(bucket, [])
        # add sortkey and result to street selection
        street_result.append((sort_key, r))

    return relevant_bucket_sorted


def built_vbo_postcode_buckets(elk_results, extra):
    """
    Build buckets per street-num for the elk results
    keeping the results in order or the elk_score/relevance
    """
    rbs = relevant_bucket_sorted = OrderedDict()

    for r in elk_results:
        # determin bucket key
        postcode = r.postcode
        bucket = postcode + str(r.huisnummer)
        # create sortkey for vbo street sorting
        sort_key = _build_sort_key(r.toevoeging, extra)
        # group results by postcodes
        street_result = rbs.setdefault(bucket, [])
        # add sortkey and result to postcode selection
        street_result.append((sort_key, r))

    return relevant_bucket_sorted


def find_next_10_best_results(end_result, best_bucket, sorted_results):
    for i in range(10):
        # bucket N0, N1, N2, N3..
        logic_bucket = '%s%s' % (best_bucket, i)
        street_result = sorted_results.get(logic_bucket, [])

        if street_result:
            # append bucket to endresults
            ordered_vbo_street_num = vbo_natural_sort(street_result)
            add_to_end_result(end_result, logic_bucket, ordered_vbo_street_num)
            # remove bucket it
            sorted_results.pop(logic_bucket)


def postcode_huisnummer_sorting(elk_results, query, tokens, i, limit=10):
    """
    Sort vbo / nummeraanduiding restult in a 'logical' way
    """
    # The house number is for sure the 3rd token.
    i = 3

    end_result = []

    extra = tokens[i + 1:]  # toevoeginen

    # bucket vbo's by streetnames in order of elk results/relevance
    sorted_results = built_vbo_postcode_buckets(elk_results, extra)

    # The first highest scoreing result
    if sorted_results:
        best_bucket, street_result = list(sorted_results.items())[0]
        ordered_vbo_street_num = vbo_natural_sort(street_result)
        # add the highest scored hit to fist result
        add_to_end_result(end_result, best_bucket, ordered_vbo_street_num)
        sorted_results.pop(best_bucket)
    else:
        return []

    # Add The next (10) most logical results (number wise)
    # derived from the best bucket
    find_next_10_best_results(end_result, best_bucket, sorted_results)

    # Add what is leftover of high scoring bucket to the end of endresults
    for bucket, street_result in sorted_results.items():
        ordered_vbo_street_num = vbo_natural_sort(street_result)
        add_to_end_result(end_result, bucket, ordered_vbo_street_num)
        # first result

    # limit
    if limit:
        return end_result[:limit]

    return end_result


def straat_huisnummer_sorting(elk_results, query, tokens, i, limit=10):
    """
    Sort by relevant and 'logical' street - huisnummer - toevoeging
    """
    end_result = []

    extra = tokens[i + 1:]  # toevoegingen

    # bucket vbo's by streetnames in order of elk results/relevance
    sorted_results = _build_vbo_buckets(elk_results, extra)

    # The first highest scoring result
    if sorted_results:
        best_bucket, street_result = list(sorted_results.items())[0]
        ordered_vbo_street_num = vbo_natural_sort(street_result)
        # add the highest scored hit to first result
        add_to_end_result(end_result, best_bucket, ordered_vbo_street_num)
        sorted_results.pop(best_bucket)
    else:
        return []

    # Add the next (10) most logical results (number wise)
    # derived from the best bucket
    find_next_10_best_results(end_result, best_bucket, sorted_results)

    # Add what is leftover of high scoring bucket to the end of endresults
    for bucket, street_result in sorted_results.items():
        ordered_vbo_street_num = vbo_natural_sort(street_result)
        add_to_end_result(end_result, bucket, ordered_vbo_street_num)
        # first result

    # limit
    if limit:
        return end_result[:limit]
    return end_result


def bucket_vbo_weg_results(elk_results: list, prefix: str):
    """
    split results in prefix matches and not prefixmatches
    group vbo's by street and order by toevoeging
    """
    prefix_streetnames = set()
    other_streetnames = set()

    street_buckets = {}

    for r in elk_results:
        straatnaam = r.straatnaam.lower()
        street_result = street_buckets.setdefault(straatnaam, [])

        street_result.append((r.toevoeging, r))

        if straatnaam.startswith(prefix):
            prefix_streetnames.add(straatnaam)
        else:
            other_streetnames.add(straatnaam)

    prefix_streetnames = sorted(prefix_streetnames)
    other_streetnames = sorted(other_streetnames)

    return street_buckets, prefix_streetnames, other_streetnames


def vbo_straat_sorting(
        elk_results: list, query: str, tokens: list, i: int):
    """
    Sort results by prefix street and housenumber
    """
    assert i <= 1

    end_result = []

    buckets, prefix, the_rest = bucket_vbo_weg_results(elk_results, query)

    def add_to_endresult(straatnamen):
        for straatnaam in straatnamen:
            street_bucket = buckets[straatnaam]
            street_bucket.sort(key=lambda x: x[0])
            for t, hit in street_bucket:
                end_result.append(hit)

    add_to_endresult(prefix)
    add_to_endresult(the_rest)

    return end_result


def bouwblok_query(analyzer: QueryAnalyzer) -> ElasticQueryWrapper:
    """ Create query/aggregation for bouwblok search"""
    return ElasticQueryWrapper(
        query={
            "prefix": {
                "code.raw": analyzer.get_bouwblok(),
            },
        },
        sort_fields=['_display'],

        indexes=[BAG],
    )


def postcode_query(analyzer: QueryAnalyzer) -> ElasticQueryWrapper:
    """ create query/aggregation for public area"""

    return ElasticQueryWrapper(
        query=Q(
            'bool',
            must=[
                Q(
                    'multi_match',
                    query=analyzer.get_postcode(),
                    type="phrase_prefix",
                    # other streets
                    fields=['postcode']
                ),
                Q('term', subtype='weg'),
            ],
        ),
        sort_fields=['_display'],
        indexes=[BAG]
    )


def bucket_weg_results(elk_results: list, prefix: str):
    """
    split results in prefix matches and not prefixmatches
    """

    prefix_results = []
    label_results = []

    for r in elk_results:
        if not hasattr(r, 'naam'):
            continue

        straatnaam = r.naam
        if straatnaam.lower().startswith(prefix):
            label = straatnaam.replace(prefix, "")
            prefix_results.append((label, r))
        else:
            label_results.append((straatnaam, r))

    return prefix_results, label_results


def weg_sorting(elk_results: list, query: str, tokens: list, num: int):
    """
    Sort the most relevant prefix items, the rest leave elk relevance
    """
    end_result = []

    prefix_results, labeled_results = bucket_weg_results(elk_results, query)

    prefix_results.sort(key=lambda x: x[0])

    # labeled_results.sort()

    for l, r in prefix_results:
        end_result.append(r)

    for l, r in labeled_results:
        end_result.append(r)

    return end_result


def weg_query(analyzer: QueryAnalyzer) -> ElasticQueryWrapper:
    """ create query/aggregation for public area"""

    return ElasticQueryWrapper(
        query=Q(
            'bool',
            must=[
                Q('term', subtype='weg'),
            ],
            should=[
                Q(
                    'multi_match',
                    query=analyzer.get_straatnaam(),
                    type="phrase_prefix",
                    # other streets
                    fields=[
                        'naam',
                        'naam_nen',
                        'naam_ptt',
                        'postcode']
                ),
                Q(
                    'query_string',
                    fields=[
                        'naam',
                        'naam_nen',
                        'naam_ptt'
                    ],
                    query=analyzer.get_straatnaam(),
                    default_operator='AND'),
            ],
            minimum_should_match=1,
        ),
        indexes=[BAG],
        custom_sort_function=weg_sorting,
        size=10,
    )


def openbare_ruimte_query(analyzer: QueryAnalyzer) -> ElasticQueryWrapper:
    """
    Find all openbare ruimtes
    """
    return ElasticQueryWrapper(
        query=Q(
            'bool',

            must_not=[
                Q('term', _type='gebied'),
            ],

            should=[
                Q(
                    'multi_match',
                    query=analyzer.get_straatnaam(),
                    type="phrase_prefix",
                    # other streets
                    fields=[
                        'naam',
                        'naam_nen',
                        'naam_ptt',
                        'subtype',
                        'postcode']
                ),
                Q(
                    'query_string',
                    fields=[
                        'naam',
                        'naam_nen',
                        'subtype',
                        'naam_ptt'
                    ],
                    query=analyzer.get_straatnaam(),
                    default_operator='AND'),
            ],

            minimum_should_match=1,
        ),
        indexes=[BAG],
        custom_sort_function=weg_sorting,
    )


def gebied_query(analyzer: QueryAnalyzer) -> ElasticQueryWrapper:
    """
    Create public
    """

    return ElasticQueryWrapper(
        query=Q(
            'bool',
            must=[
                Q('term', _type='gebied'),
            ],
            should=[
                {'match': {'naam.ngram': analyzer.query}},
                {'match': {'naam.raw': analyzer.query}},
                Q(
                    'multi_match',
                    query=analyzer.query,
                    type="phrase_prefix",
                    # other streets
                    fields=[
                        'naam',
                        'naam.ngram',
                        'naam.raw',
                        'code']
                ),
                Q(
                    'query_string',
                    fields=[
                        'naam',
                        'code',
                    ],
                    query=analyzer.query,
                    default_operator='AND'),
            ],
            minimum_should_match=1,
        ),
        indexes=[BAG],
        custom_sort_function=weg_sorting,
        size=5,
    )


def straatnaam_query(analyzer: QueryAnalyzer) -> ElasticQueryWrapper:
    street_part = analyzer.get_straatnaam()
    return ElasticQueryWrapper(
        query={
            'multi_match': {
                'query': street_part,
                'type': 'phrase_prefix',
                'fields': [
                    'straatnaam',
                    'straatnaam_nen',
                    'straatnaam_ptt',
                ]
            },
        },
        sort_fields=['straatnaam.raw', 'huisnummer', 'toevoeging.raw'],
        indexes=[NUMMERAANDUIDING]
    )


def straatnaam_huisnummer_query(analyzer: QueryAnalyzer) -> ElasticQueryWrapper:
    straat, huisnummer, toevoeging = analyzer.get_straatnaam_huisnummer_toevoeging()

    return ElasticQueryWrapper(
        query={
            'bool': {
                'must': [
                    {
                        'multi_match': {
                            'query': straat,
                            'type': 'phrase_prefix',
                            'fields': [
                                'straatnaam',
                                'straatnaam_nen',
                                'straatnaam_ptt',
                            ]
                        },
                    },
                    {
                        'prefix': {
                            'toevoeging': toevoeging,
                        }
                    },
                ],
            },
        },
        sort_fields=['straatnaam.raw', 'huisnummer', 'toevoeging.raw'],
        indexes=[NUMMERAANDUIDING]
    )
