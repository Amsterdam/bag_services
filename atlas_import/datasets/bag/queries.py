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
from elasticsearch_dsl import Search, Q, A


POSTCODE = re.compile('[1-9]\d{3}[ \-]?[a-zA-Z]?[a-zA-Z]?')


def normalize_postcode(query):
    """
    In cases when using non analyzed queries this makes sure
    the postcode, if in the query, is normalized to ddddcc form
    """
    query = query.lower()
    # Checking for postcode
    pc = POSTCODE.search(query)
    if pc:
        query = query.replace(pc.group(0), \
                ((pc.group(0)).replace(' ', '')).replace('-', ''))
    return query


def normalize_address(query):
    """
    In cases when using non analyzed queries this makes sure
    the address, if in the query, does not contain bad characters
    """
    query = query.lower()
    query = query.replace('/', ' ').replace('.', ' ')
    return query


def address_Q(query):
    """Create query/aggregation for complete address search"""
    pass


def comp_address_Q(query):
    """Create query/aggregation for complete address search"""
    query = normalize_address(query)
    return {
        'A': A('terms', field='adres.raw'),
        'Q': Q(
            'query_string',
            fields=['comp_address', 'comp_address_nen', 'comp_address_ptt'],
            query=query,
            default_operator='AND',
        ),
    }


def street_name_Q(query):
    """Create query/aggregation for street name search"""
    return {
        'A': A('terms', field="straatnaam.raw"),
        'Q': Q(
                "multi_match",
                query=query,
                type="phrase_prefix",
                fields=[
                    "straatnaam.ngram",
                    "straatnaam_nen.ngram",
                    "straatnaam_ptt.ngram",
                ],
            ),
    }


def house_number_Q(query):
    """Create query/aggregation for house number search"""

    return {
        'A': None,
        'Q': Q("match_phrase_prefix", field="huisnummer_variation"),
    }


def bouwblok_Q(query):
    """ Create query/aggregation for bouwblok search"""
    return {
        'A': None,
        'Q': Q('match_phrase_prefix', code=query),
    }


def postcode_Q(query):
    """
    Create query/aggregation for postcode search

    The postcode query uses a prefix query which is a not
    analyzed query. Therefore, in order to find matches when an uppercase
    letter is given the string is changed to lowercase, and remove whitespaces
    """
    query = normalize_postcode(query)
    # Checking for whitespace to remove it

    return {
        "Q": Q("prefix", postcode=query),
        "A": A("terms", field="postcode"),
    }


def public_area_Q(query):
    """ Create query/aggregation for public area"""
    return {
        'A': None,
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
        should=[Q('term', postcode_huisnummer=query), Q('term', postcode_toevoeging=query)],
        minimum_should_match=1,
    )

