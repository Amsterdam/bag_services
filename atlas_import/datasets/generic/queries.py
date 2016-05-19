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
import re
# Packages
from elasticsearch_dsl import Search, Q, A


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

def meetbout_Q(query):
    """Searching for meetbout in autocomplete"""
    return {
        'Q': Q("phrase_prefix", meetboutnummer=query)
,
    }

