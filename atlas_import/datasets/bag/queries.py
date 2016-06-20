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
# Packages
# from elasticsearch_dsl import Search, Q, A
from elasticsearch_dsl import Q, A

log = logging.getLogger('bag_Q')


def address_Q(query):
    """Create query/aggregation for complete address search"""
    pass


def comp_address_pcode_Q(query, tokens=None):

    """Create query/aggregation for postcode house number search"""

    return {
        'Q': Q(
            'bool',
            must=[
                Q('term', postcode="".join(tokens[:2])),
            ]
        ),
        # 'S': ['huisnummer', 'toevoeging.raw']
    }


def split_toevoeging(tokens, num):
    """
    """
    extra_tv = []

    # split toevoeging in a way
    for token in tokens[num:]:
        if token[0].isdigit():
            extra_tv.append(token)
        else:
            for c in token:
                extra_tv.append(c)

    return " ".join(extra_tv)


def postcode_huisnummer_Q(query, tokens=None, num=None):

    """Create query/aggregation for postcode house number search"""

    assert tokens

    num = int(tokens[2])
    split_tv = split_toevoeging(tokens, 2)

    print(split_tv)

    # Third token must be house number

    return {
        'Q': Q(
            'bool',
            must=[
                Q('term', postcode="".join(tokens[:2])),
                Q('match_phrase', toevoeging=split_tv),
            ],
            should=[
                Q('term', huisnummer=num, boost=3),
            ]
        ),
        'sorting': postcode_huisnummer_sorting,
        'size': 50  # sample size for custom sort
    }


def comp_address_Q(query, tokens=None, num=None):
    """Create query/aggregation for complete address search"""

    return {
        'A': A('terms', field='adres.raw'),
        'Q': Q(
            'query_string',
            fields=[
                'comp_address',
                'comp_address_nen',
                'comp_address_ptt',
                'comp_address_pcode^4'],
            query=query,
            default_operator='AND',
        ),
        # 'S': ['_display']
    }


def search_streetname_Q(query, tokens=None, num=None):
    """Create query/aggregation for address search"""

    return {
        'Q': Q(
            'bool',
            should=[
                Q('query_string',
                    fields=[
                        'comp_address',
                        'comp_address_nen',
                        'comp_address_ptt',
                        'postcode^3',
                    ],
                    query=query,
                    default_operator='AND'),
                Q(
                    'multi_match',
                    query=query,
                    type="phrase_prefix",
                    # other streets
                    fields=[
                        'comp_address',
                        'comp_address_nen',
                        'comp_address_ptt',
                        'postcode^3',
                    ]
                ),
            ])
    }


def tokens_comp_address_Q(query, tokens=None, num=None):
    """Create query/aggregation for complete address search"""

    assert tokens
    assert num

    street_part = " ".join(tokens[:num])
    num = tokens[num]

    return {
        'A': A('terms', field='adres.raw'),
        'Q': Q(
            'bool',
            must=[
                Q('query_string', fields=[
                    'comp_address',
                    'comp_address_nen',
                    'comp_address_ptt',
                    'comp_address_pcode^2'],
                  query=street_part,
                  default_operator='AND'),
                Q('term', huisnummer=num),
            ]
        ),
        # 'S': ['_display']
    }


def postcode_and_num_Q(query, tokens=None, num=None):
    """
    """

    assert tokens


# ambetenaren sort
def vbo_natural_sort(l):

    def alphanum_key(key):
        return [t for t in re.split('([0-9]+)', key[0])]

    return sorted(l, key=alphanum_key)


def built_sort_key(toevoeging, extra):
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


def built_vbo_buckets(elk_results, extra):
    """
    Build buckets per street-num for the elk results
    keeping the results in order or the elk_score/relevance
    """
    rbs = relevant_bucket_sorted = OrderedDict()

    for r in elk_results:

        straatnaam = r.straatnaam_keyword
        bucket = straatnaam + str(r.huisnummer)

        # create sortkey for vbo street sorting
        sort_key = built_sort_key(r.toevoeging, extra)
        # group results by streetnames
        street_result = rbs.setdefault(bucket, [])
        # add sortkey and result to street selection
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


def postcode_huisnummer_sorting(elk_results, query, tokens, i):
    # The house number is for sure the 3rd token.
    return straat_huisnummer_sorting(elk_results, query, tokens, 2)


def straat_huisnummer_sorting(elk_results, query, tokens, i):
    """
    Sort by relevant and 'logical' steet - huisnummer - toevoeging
    """
    end_result = []

    extra = tokens[i+1:]  # toevoeginen

    # bucket vbo's by streetnames in order of elk results/relevance
    sorted_results = built_vbo_buckets(elk_results, extra)

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

    return end_result[:10]


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


def straat_huisnummer_Q(query, tokens=None, num=None):
    """
    # Breaking the query to street name and house number
    # --------------------------------------------------
    # Finding the housenumber part

    # Quering exactly on street name and prefix on house number
    """
    assert tokens
    assert num

    street_part = " ".join(tokens[:num])

    split_tv = split_toevoeging(tokens, num)

    # huisnummer is/should be first number
    num = tokens[num]

    return {
        'Q': Q(
            'bool',
            must=[
            ],

            should=[
                Q('match', straatnaam=street_part),
                Q('match', straatnaam_nen=street_part),
                Q('match', straatnaam_ptt=street_part),

                Q('match', straatnaam_keyword=street_part),
                Q('match', straatnaam_nen_keyword=street_part),
                Q('match', straatnaam_ptt_keyword=street_part),

                # Q('match', huisnummer=num),
                Q('term', huisnummer=num, boost=3),
                Q('match_phrase', toevoeging=split_tv),
            ],
            minimum_should_match=3
        ),
        'sorting': straat_huisnummer_sorting,
        'size': 60
    }


def street_name_Q(query):
    """Create query/aggregation for street name search"""
    return {
        'A': A('terms', field="straatnaam.raw"),
        'Q': Q(
                "multi_match",
                query=query,
                type='phrase_prefix',
                fields=[
                    "straatnaam.ngram_edge",
                    "straatnaam_nen.ngram_edge",
                    "straatnaam_ptt.ngram_edge",
                ],
            ),
    }


def house_number_Q(query):
    """Create query/aggregation for house number search"""

    return {
        'Q': Q("match_phrase_prefix", huisnummer_variation=query),
    }


def bouwblok_Q(query, tokens=None, num=None):
    """ Create query/aggregation for bouwblok search"""

    assert tokens

    return {
        'Q': Q('match_phrase_prefix', code=query),
    }


def postcode_Q(query, tokens=None, num=None):
    """
    Create query/aggregation for postcode search

    The postcode query uses a prefix query which is a not
    analyzed query. Therefore, in order to find matches when an uppercase
    letter is given the string is changed to lowercase, and remove whitespaces
    """

    return {
        "Q": Q("prefix", postcode=query),
        "A": A("terms", field="straatnaam.raw"),
    }


def is_postcode_Q(query: str, tokens=None, num=None):
    """ create query/aggregation for public area"""

    assert tokens

    postcode = "".join(tokens[:2])

    return {
        'Q': Q(
            'bool',
            must=[
                Q(
                    'multi_match',
                    query=postcode,
                    type="phrase_prefix",
                    # other streets
                    fields=['postcode']
                ),
                Q('term', subtype='weg'),
            ],
        ),
        's': ['_display']
    }


def bucket_weg_results(elk_results: list, prefix: str):
    """
    split results in prefix matches and not prefixmatches
    """

    prefix_results = []
    label_results = []

    for r in elk_results:
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

    prefix_results.sort()

    # labeled_results.sort()

    for l, r in prefix_results:
        end_result.append(r)

    for l, r in labeled_results:
        end_result.append(r)

    return end_result


def weg_Q(query: str, tokens=None, num=None):
    """ create query/aggregation for public area"""

    return {
        'Q': Q(
            'bool',
            must=[
                Q('term', subtype='weg'),
            ],
            should=[
                Q(
                    'multi_match',
                    query=query,
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
                    query=query,
                    default_operator='AND'),
            ],
            minimum_should_match=1,
        ),
        'sorting': weg_sorting,
        'size': 10
    }


def public_area_Q(query):
    """ Create query/aggregation for public area"""
    return {
        'Q': Q(
            "multi_match",
            query=query,
            type="phrase_prefix",
            slop=12,
            max_expansions=12,
            fields=[
                'naam',
                'postcode',
                'subtype',
            ],
        ),
    }


def exact_postcode_house_number_Q(query):
    """Create a query form an exact match on the address"""
    return Q(
        'bool',
        should=[
            Q('term', postcode_huisnummer=query),
            Q('term', postcode_toevoeging=query)],
        minimum_should_match=1,
    )
