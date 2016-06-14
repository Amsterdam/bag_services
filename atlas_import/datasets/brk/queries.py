"""
==================================================
 Individual search queries
--------------------------------------------------
 Each of these functions builds a query and,
 if needed an aggregation as well.
 They all return a dict with the Q and A keyes
==================================================
"""
from elasticsearch_dsl import Q, A
from django.conf import settings

BRK = settings.ELASTIC_INDICES['BRK']


def kadaster_object_Q(query, tokens=None, num=None):
    """Create query/aggregation for kadaster object search"""
    return {
        'A': A('terms', field='aanduiding.raw'),
        'Q': Q('match_phrase_prefix', aanduiding=query)
    }


def kadaster_subject_Q(query, tokens=None, num=None):
    """Create query/aggregation for kadaster subject search"""
    return {
        'A': A('terms', field='naam.raw'),
        'Q': Q(
            'multi_match',
            slop=12,  # match "stephan preeker" with "stephan jacob preeker"
            max_expansions=12,
            query=query,
            type='phrase_prefix',
            fields=[
                "naam"]
            ),
        'size': 5,
        'Index': [BRK]
    }
