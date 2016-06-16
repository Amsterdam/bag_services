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


def smart_expand_kot_codes(tokens):
    """
    expand kot codes
    """
    # fill first number with zeros
    if len(tokens) >= 3:
        tokens[2] = tokens[2].zfill(5)

    # fill second number with zeros
    if len(tokens) == 5:
        tokens[4] = tokens[4].zfill(4)
    # if 3rd token is digit then rewrite notation to
    # City L1 D1 l2 = A, D2 = token[3]
    elif len(tokens) == 4:
        if tokens[3].isdigit():
            d2 = tokens[3].zfill(4)
            l2 = 'a'
            # replace third number with letter
            tokens[3] = l2
            # add back the zerod 3
            tokens.append(d2)


def kadaster_object_Q(query, tokens=None, num=None):
    """Create query/aggregation for kadaster object search"""

    assert tokens

    # ASD15
    gemeente_code = "".join(tokens[:2])

    # ..... G 12345 A 0001
    kad_code = tokens[2:]
    kad_code.insert(0, gemeente_code)

    smart_expand_kot_codes(kad_code)

    kad_code = " ".join(kad_code)
    # smart_code = " ".join(

    return {
        'Q': Q(
            'bool',

            must=[
                Q('term', gemeente_code=gemeente_code)
            ],

            should=[
                Q(
                    'multi_match',
                    type='phrase_prefix',
                    fields=[
                        "aanduiding.ngram",
                        "aanduiding"],
                    query=kad_code,
                ),
                Q('match', aanduiding=kad_code)
            ]
        )

    }


def gemeente_object_Q(query, tokens=None, num=None):
    """
    Amsterdam S   00000 A  0000

    City      L1  D1    L2 D2
    0         1   2     3  4
    """

    assert tokens

    smart_expand_kot_codes(tokens)

    code = " ".join(tokens[1:])

    return {
        'Q': Q(
            'bool',

            must=[
                Q('term', gemeente=tokens[0])
            ],

            should=[
                Q(
                    'multi_match',
                    type='phrase_prefix',
                    fields=[
                        "short_aanduiding.ngram",
                        "short_aanduiding"],
                    query=code,
                ),
                Q('match', short_aanduiding=code)
                #,
                #Q(
                #    'multi_match',
                #    fields=["short_aanduiding.raw"],
                #    query=code
                #)
            ]
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
