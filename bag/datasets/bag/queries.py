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

from django.conf import settings
from elasticsearch_dsl import Q

from datasets.generic.queries import ElasticQueryWrapper
from datasets.generic.query_analyzer import QueryAnalyzer

log = logging.getLogger('bag_Q')

BAG = settings.ELASTIC_INDICES['BAG']
NUMMERAANDUIDING = settings.ELASTIC_INDICES['NUMMERAANDUIDING']


def postcode_huisnummer_query(analyzer: QueryAnalyzer) -> ElasticQueryWrapper:
    """Create query/aggregation for postcode house number search"""

    postcode, huisnummer, toevoeging = \
        analyzer.get_postcode_huisnummer_toevoeging()

    return ElasticQueryWrapper(
        query={
            'bool': {
                'must': [
                    {
                        'term': {
                            'postcode': postcode,
                        }
                    },
                    {
                        'prefix': {
                            'toevoeging': toevoeging,
                        }
                    },
                ],
            },
        },
        indexes=[BAG, NUMMERAANDUIDING],
        sort_fields=['straatnaam.raw', 'huisnummer', 'toevoeging.raw'],
    )


def postcode_huisnummer_exact_query(analyzer: QueryAnalyzer):
    """Create query/aggregation for postcode house number search"""

    postcode, huisnummer, toevoeging = \
        analyzer.get_postcode_huisnummer_toevoeging()

    return ElasticQueryWrapper(
        query=Q(
            'bool',
            must=[
                Q('term', postcode=postcode),
                Q('match_phrase', toevoeging=toevoeging),
                Q('term', huisnummer=huisnummer)
            ],
        ),
        sort_fields=['straatnaam.raw', 'huisnummer', 'toevoeging.raw'],
        indexes=[NUMMERAANDUIDING],

        size=1
    )


def bouwblok_query(analyzer: QueryAnalyzer) -> ElasticQueryWrapper:
    """ Create query/aggregation for bouwblok search"""
    return ElasticQueryWrapper(
        query={
            "match": {
                # upper, want raw is case-sensitive
                # "code.raw": analyzer.get_bouwblok().upper(),
                "code": analyzer.get_bouwblok()
            },
        },
        sort_fields=['_display'],

        indexes=[BAG],
    )


def postcode_query(analyzer: QueryAnalyzer) -> ElasticQueryWrapper:
    """ create query/aggregation for public area"""

    return ElasticQueryWrapper(
        query=Q(
            'bool',
            must=[
                Q(
                    'multi_match',
                    query=analyzer.get_postcode(),
                    type="phrase_prefix",
                    # other streets
                    fields=['postcode']
                ),
                Q('term', subtype='weg'),
            ],
        ),
        sort_fields=['_display'],
        indexes=[BAG]
    )


def _basis_openbare_ruimte_query(
        analyzer: QueryAnalyzer,
        must: [dict] = None,
        must_not: [dict] = None,
        useorder: [bool] = False) -> ElasticQueryWrapper:
    """
    Basis openbare-ruimte query.

    Het resultaat ordent pure prefix matches vóór phrase_prefix matches.
    """

    # Logica:
    # Het doel is om 'echte' prefix-matches te sorteren vóór phrase-prefix
    # matches.  Met alleen phrase-prefix kan dat niet, dus we gebruiken twee
    # 'should' queries waarvan er minimaal één moet matchen. Met de
    # constant_score wrapper zorgen we ervoor dat alle 'prefix' matches een
    # score van 10 krijgen, en alle 'phrase_prefix' matches een score van 5.
    # De 'constant_score' op de 'must' voorkomt dat die in de weg zit.  Op
    # basis van deze output kunnen we vervolgens ordenen op score, gevolgd
    # door naam.
    #
    # Voorbeelden: Zoeken op Weesp, geeft eerst Weesperstraat, dan pas
    # Metrostation Weesperstraat.  Zoeken op Prinsen, geeft eerst
    # Prinsengracht, dan pas Korte Prinsengracht.

    _must = [{'constant_score': {'query': q}} for q in (must or [])]
    _must_not = [{'constant_score': {'query': q}} for q in (must_not or [])]

    sort_fields = ['_score', 'naam.keyword']
    if useorder:
        sort_fields = ['order', '_score', 'naam']
    return ElasticQueryWrapper(
        query={
            'bool': {
                'must': _must,
                'must_not': _must_not,
                'should': [
                    {
                        'constant_score': {
                            'query': {
                                'prefix': {
                                    'naam.keyword': analyzer.get_straatnaam(),
                                }
                            },
                            'boost': 10,
                        },
                    },
                    {
                        'constant_score': {
                            'query': {
                                'multi_match': {
                                    'query': analyzer.get_straatnaam(),
                                    'type': 'phrase_prefix',
                                    'fields': [
                                        'naam',
                                        'naam_nen',
                                        'naam_ptt',
                                        'postcode',
                                    ]
                                }
                            },
                            'boost': 5,
                        }
                    }
                ],
                'minimum_should_match': 1,
            }
        },
        indexes=[BAG],
        sort_fields=sort_fields,
        size=10,
    )


def weg_query(analyzer: QueryAnalyzer) -> ElasticQueryWrapper:
    """
    Maak een query voor openbare ruimtes van het type 'weg'.
    """

    return _basis_openbare_ruimte_query(analyzer, must=[{
        'term': {'subtype': 'weg'}
    }])


def openbare_ruimte_query(analyzer: QueryAnalyzer) -> ElasticQueryWrapper:
    """
    Maak een query voor openbare ruimte.
    """
    return _basis_openbare_ruimte_query(analyzer, must_not=[{
        'term': {'_type': 'gebied'}
    }])


def gebied_query(analyzer: QueryAnalyzer) -> ElasticQueryWrapper:
    """
    Maak een query voor gebieden.
    """
    return _basis_openbare_ruimte_query(analyzer, useorder=True, must=[{
        'term': {'_type': 'gebied'}
    }])


def straatnaam_query(analyzer: QueryAnalyzer) -> ElasticQueryWrapper:
    street_part = analyzer.get_straatnaam()
    return ElasticQueryWrapper(
        query={
            'multi_match': {
                'query': street_part,
                'type': 'phrase_prefix',
                'fields': [
                    'straatnaam',
                    'straatnaam_nen',
                    'straatnaam_ptt',
                ]
            },
        },
        sort_fields=['straatnaam.raw', 'huisnummer', 'toevoeging.raw'],
        indexes=[NUMMERAANDUIDING]
    )


def straatnaam_huisnummer_query(
        analyzer: QueryAnalyzer) -> ElasticQueryWrapper:
    straat, huisnummer, toevoeging = \
        analyzer.get_straatnaam_huisnummer_toevoeging()

    return ElasticQueryWrapper(
        query={
            'bool': {
                'must': [
                    {
                        'multi_match': {
                            'query': straat,
                            'type': 'phrase_prefix',
                            'fields': [
                                'straatnaam',
                                'straatnaam_nen',
                                'straatnaam_ptt',
                            ]
                        },
                    },
                    {
                        'prefix': {
                            'toevoeging': toevoeging,
                        }
                    },
                ],
            },
        },
        sort_fields=['straatnaam.raw', 'huisnummer', 'toevoeging.raw'],
        indexes=[NUMMERAANDUIDING]
    )
