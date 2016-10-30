"""
==================================================
 Individual search queries
--------------------------------------------------
 Each of these functions builds a query and,
 if needed an aggregation as well.
 They all return a dict with the Q and A keyes
==================================================
"""
import logging

from django.conf import settings
from elasticsearch_dsl import Q, A

from datasets.generic.queries import ElasticQueryWrapper
from datasets.generic.query_analyzer import QueryAnalyzer

log = logging.getLogger(__name__)

BRK = settings.ELASTIC_INDICES['BRK']


def kadastraal_object_query(analyzer: QueryAnalyzer) -> ElasticQueryWrapper:
    """
    Create query/aggregation for kadaster object search

    kad_code = ['ASD15','S', '00000','A','0000']

    ASD15     S      00000         A    0000
    gem_code  Sectie objectnr indexl indexnr
    City      L1     D1           L2      D2
    0         1      2             3       4

    """
    kot_query = analyzer.get_kadastraal_object_query()
    if kot_query.is_empty():
        return ElasticQueryWrapper(query=None)

    must = []

    if kot_query.gemeente_code:
        must.append({'term': {'gemeente_code': kot_query.gemeente_code}})

    if kot_query.gemeente_naam:
        must.append({'term': {'gemeente': kot_query.gemeente_naam}})

    if kot_query.sectie:
        must.append({'term': {'sectie': kot_query.sectie}})

    if kot_query.object_nummer and int(kot_query.object_nummer):
        if kot_query.object_nummer_is_exact():
            must.append(
                {'term': {'objectnummer.int': int(kot_query.object_nummer)}})
        else:
            must.append(
                {'prefix': {'objectnummer.raw': int(kot_query.object_nummer)}})

    if kot_query.index_letter:
        must.append(Q('term', indexletter=kot_query.index_letter))

    if kot_query.index_nummer and int(kot_query.index_nummer):
        if kot_query.index_nummer_is_exact():
            must.append(
                {'term': {'indexnummer.int': int(kot_query.index_nummer)}})
        else:
            must.append(
                {'prefix': {'indexnummer.raw': int(kot_query.index_nummer)}})

    return ElasticQueryWrapper(
        query=Q('bool', must=must),
        sort_fields=['aanduiding'],
        indexes=[BRK],
    )


def kadastraal_subject_query(analyzer: QueryAnalyzer) -> ElasticQueryWrapper:
    """Create query/aggregation for kadaster subject search"""
    return ElasticQueryWrapper(
        query=Q(
            'multi_match',
            slop=12,  # match "stephan preeker" with "stephan jacob preeker"
            max_expansions=12,
            query=analyzer.query,
            type='phrase_prefix',
            fields=["naam"]
        ),
        sort_fields=['naam.raw'],
        indexes=[BRK],
    )
