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

import logging

log = logging.getLogger(__name__)

BRK = settings.ELASTIC_INDICES['BRK']


def add_object_nummer_query(must, should, kad_code_tokens):
    """
    """
    objectnummer = kad_code_tokens[2]

    should.extend([
        Q('match', objectnummer=objectnummer),
        {
                'term': {
                    'objectnummer.int': int(objectnummer)
                }
        },
        Q(
            'multi_match',
            type='phrase_prefix',
            fields=[
                "objectnummer",
                "objectnummer.ngram",
                "objectnummer.raw"
            ],
            query=objectnummer,
        )
    ])

    if objectnummer.isdigit():
        should.append(Q('match', objectnummer=int(objectnummer)))

    if len(kad_code_tokens) > 3 or len(objectnummer) == 5:
        if objectnummer.isdigit():
            must.append({
                'term': {
                    'objectnummer.int': int(objectnummer)}
                }
            )


def specialize_kad_code_search(must, should, kad_code_tokens):
    """
    Given kad_code_tokens detemine how precise the elastic query
    should be
    """
    if len(kad_code_tokens) >= 2:
        sectieletter = kad_code_tokens[1]
        must.append(Q('term', sectie=sectieletter))

    # if there is an indexl we must mach it
    if len(kad_code_tokens) >= 4:
        indexl = kad_code_tokens[3]

        if indexl.isdigit():
            if int(indexl) == 0:
                kad_code_tokens.insert(3, 'g')
            else:
                kad_code_tokens.insert(3, 'a')

        indexl = kad_code_tokens[3]
        must.append(Q('term', indexletter=indexl))

    # if there is an object nummer try to mach it
    if len(kad_code_tokens) >= 3:
        add_object_nummer_query(must, should, kad_code_tokens)


def kadaster_object_Q(query, tokens=None, num=None):
    """
    Create query/aggregation for kadaster object search

    kad_code = ['ASD15','S', '00000','A','0000']

    ASD15     S      00000         A    0000
    gem_code  Sectie objectnr indexl indexnr
    City      L1     D1           L2      D2
    0         1      2             3       4

    *NOTE* ASD15 will be joined to one token
    """

    assert tokens

    # ASD 15 -> ASD15
    gemeente_code = "".join(tokens[:2])
    # ASD 15 G 12345 A 0001
    kad_code_tokens = tokens[2:]
    kad_code_tokens.insert(0, gemeente_code)
    kad_code = " ".join(kad_code_tokens)

    # kad_code = ASD15 G 12345 A 0001

    must = [
      Q('term', gemeente_code=gemeente_code)
    ]

    should = [
        Q(
            'multi_match',
            type='phrase_prefix',
            fields=[
                "aanduiding.raw",
                "aanduiding.ngram",
                "aanduiding"],
            query=kad_code,
        ),
        Q('match', aanduiding=kad_code)
    ]

    specialize_kad_code_search(must, should, kad_code_tokens)

    return {
        'Q': Q(
            'bool',
            must=must,
            should=should
            )

    }


def match_code_object_Q(query, tokens=None, num=None):
    """
    For normal search try to match some part of aanduiding
    """

    must = []
    should = [
        Q(
            'multi_match',
            type='phrase_prefix',
            fields=[
                "aanduiding.raw",
                "aanduiding.ngram",
                "aanduiding"],
            query=query,
        ),
        Q('match', aanduiding=query)
    ]

    return {
        'Q': Q(
            'bool',
            must=must,
            should=should
            )
    }


def gemeente_object_Q(query, tokens=None, num=None):
    """
    Amsterdam S      00000         A    0000
    Stad      Sectie objectnr indexl indexnr
    City      L1     D1           L2      D2
    0         1      2             3       4
    """

    assert tokens

    kad_code_tokens = tokens
    kad_code = " ".join(kad_code_tokens[1:])

    must = [Q('term', gemeente=tokens[0])]

    should = [
        Q(
            'multi_match',
            type='phrase_prefix',
            fields=[
                "short_aanduiding.ngram",
                "short_aanduiding"],
            query=kad_code,
        ),
        Q('match', short_aanduiding=kad_code)
    ]

    # replace gemeente token with None
    kad_code_tokens[0] = None
    specialize_kad_code_search(must, should, kad_code_tokens)

    return {
        'Q': Q(
            'bool',
            must=must,
            should=should
        )
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
