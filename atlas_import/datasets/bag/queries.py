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
import re
# Packages
# from elasticsearch_dsl import Search, Q, A
from elasticsearch_dsl import Q, A


POSTCODE = re.compile('[1-9]\d{3}[ \-]?[a-zA-Z]?[a-zA-Z]?')
# Recognise the house number part
HOUSE_NUMBER = re.compile('((\d+)((( \-)?[a-zA-Z\-]{0,3})|(( |\-)\d*)))$')


def normalize_address(query):
    """
    In cases when using non analyzed queries this makes sure
    the address, if in the query, does not contain bad characters
    """
    query = query.lower()
    query = query.replace('/', ' ').replace('.', ' ').replace('-', ' ')
    return query


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


def tokens_comp_address_pcode_Q(query, tokens=None):

    """Create query/aggregation for postcode house number search"""

    assert tokens

    return {
        'Q': Q(
            'bool',
            must=[
                Q('term', postcode="".join(tokens[:2])),
                Q({
                    'match_phrase_prefix': {
                        'toevoeging': " ".join(tokens[2:])}
                })
            ]
        ),
        # 'S': ['huisnummer', 'toevoeging.raw']
    }



def comp_address_Q(query, tokens=None):
    """Create query/aggregation for complete address search"""
    query = normalize_address(query)

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


def street_name_and_num_Q(query, tokens=None, num=None):
    """
    # Breaking the query to street name and house number
    # --------------------------------------------------
    # Finding the housenumber part

    # Quering exactly on street name and prefix on house number
    """
    assert tokens

    street_part = " ".join(tokens[:num])
    the_rest = " ".join(tokens[num:])
    # huisnummer is/should be first number
    num = tokens[num]

    return {
        'Q': Q(
            'bool',
            must=[
                Q('bool', should=[
                    Q('match', straatnaam_keyword=street_part),
                    Q('match', straatnaam_nen_keyword=street_part),
                    Q('match', straatnaam_ptt_keyword=street_part),
                ],
                    minimum_should_match=1),
                Q('match_phrase', toevoeging=the_rest),
                Q('match', huisnummer=num),
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


def bouwblok_Q(query, tokens=None):
    """ Create query/aggregation for bouwblok search"""
    return {
        'Q': Q('match_phrase_prefix', code=query),
    }


def postcode_Q(query, tokens=None):
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


def weg_Q(query, tokens=None):
    """ Create query/aggregation for public area"""
    return {
        'Q': Q(
            'bool',
            must=[
                Q(
                    'multi_match',
                    query=query,
                    type="phrase_prefix",
                    # other streets
                    fields=['naam', 'postcode']
                ),
                Q('term', subtype='weg'),
            ],
        ),
        # 'S': ['_display']

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
