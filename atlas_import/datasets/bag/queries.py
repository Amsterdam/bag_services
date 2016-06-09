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

    log.info('postcode_huisnummer_Q')

    split_tv = split_toevoeging(tokens, 2)

    log.info(split_tv)

    return {
        'Q': Q(
            'bool',
            must=[
                Q('term', postcode="".join(tokens[:2])),
                Q({
                    'match_phrase_prefix': {
                        'toevoeging': split_tv}
                })
            ]
        ),
        # 'S': ['huisnummer', 'toevoeging.raw']
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
                        'comp_address_ptt'
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
                    ]
                ),
                # Q('prefix', naam=query)
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
                Q('bool', should=[

                    Q('match', straatnaam=street_part),
                    Q('match', straatnaam_nen=street_part),
                    Q('match', straatnaam_ptt=street_part),

                    Q('match', straatnaam_keyword=street_part),
                    Q('match', straatnaam_nen_keyword=street_part),
                    Q('match', straatnaam_ptt_keyword=street_part),

                    Q('match', huisnummer=num),

                ],
                    minimum_should_match=1),
            ],
            should=[
                Q('match_phrase', toevoeging=split_tv),
            ]
        ),
        # 'S': ['huisnummer']  # , 'toevoeging.raw']
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


def is_postcode_Q(query, tokens=None, num=None):
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
        # 's': ['_display']
    }


def weg_Q(query, tokens=None, num=None):
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
        # 's': ['_display']
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
