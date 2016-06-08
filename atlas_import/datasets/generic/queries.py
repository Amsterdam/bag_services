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


def meetbout_Q(query, tokens=None, num=None):
    """Searching for meetbout in autocomplete"""
    return {
        'Q': Q("match_phrase_prefix", meetboutnummer=query)
    }
