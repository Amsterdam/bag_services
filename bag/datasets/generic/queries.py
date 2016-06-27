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

import logging

log = logging.getLogger(__name__)


def meetbout_Q(query, tokens=None, num=None):
    """
    Main 'One size fits all' search query used
    """
    log.debug('%20s %s', meetbout_Q.__name__, query)

    return {
        'Q': Q(
            "multi_match",
            query=query,
            # type="most_fields",
            # type="phrase",
            type="phrase_prefix",
            slop=12,
            max_expansions=12,
            fields=[
                "meetboutnummer",
            ]
        ),
        'Index': ['meetbouten']
    }
