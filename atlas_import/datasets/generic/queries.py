"""
==================================================
 Individual search queries for external systems
--------------------------------------------------
 Each of these functions builds a query and,
 if needed an aggregation as well.
 They all return a dict with the Q and A keyes
==================================================
"""
# Python
# Packages
# from elasticsearch_dsl import Search, Q, A

from elasticsearch_dsl import Q


def normalize_address(query):
    """
    In cases when using non analyzed queries this makes sure
    the address, if in the query, does not contain bad characters
    """
    query = query.lower()
    query = query.replace('/', ' ').replace('.', ' ')
    return query


def meetbout_Q(query, tokens=None):
    """Searching for meetbout in autocomplete"""
    return {
        'Q': Q("phrase_prefix", meetboutnummer=query)
    }
