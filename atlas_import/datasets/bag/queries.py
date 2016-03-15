"""
==================================================
 Individual search queries
--------------------------------------------------
 Each of these functions builds a query and,
 if needed an aggregation as well.
 They all return a dict with the Q and A keyes
==================================================
"""
from elasticsearch_dsl import Search, Q, A


def address_Q(query):
    """Create query/aggregation for complete address search"""
    pass

def comp_address_Q(query):
    """Create query/aggregation for complete address search"""
    return {
        'A': A('terms', field='adres.raw'),
        'Q': Q(
            'query_string',
            default_field='comp_address',
            query=query,
            default_operator='AND',
            fuzziness='AUTO')
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
                ]
            )

    }


def house_number_Q(query):
    """Create query/aggregation for house number search"""

    return {
        'A': None,
        'Q': Q("match_phrase_prefix", field="huisnummer_variation")
    }


def postcode_Q(query):
    """
    Create query/aggregation for postcode search

    The postcode query uses a prefix query which is a not
    analyzed query. Therefore, in order to find matches when an uppercase
    letter is given the string is changed to lowercase
    """
    query = query.lower()
    return {
        "Q": Q("prefix", postcode=query),
        "A": A("terms", field="postcode")
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
            ]
        )
    }