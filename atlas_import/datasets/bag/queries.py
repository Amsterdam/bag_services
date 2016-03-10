"""
==================================================
 Individual search queries
--------------------------------------------------
 Each of these functions builds a query and,
 if needed an aggregation as well.
 They all return a dict with the Q and A keyes
==================================================
"""

def address_Q(query):
    """Create query/aggregation for complete address search"""
    pass

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
        'Q': Q("prefix", field="huisnummer_variation")
    }


def name_Q(query):
    """Create query/aggregation for name search"""
    return {
        'A': None,
        'Q': Q(
            "multi_match",
            query=query,
            boost=1,
            type="phrase_prefix",
            fields=[
                "geslachtsnaam",
                "kadastraal_subject.naam",
            ]
        )
    }


def postcode_Q(query):
    """Create query/aggregation for postcode search"""
    return {
        "Q": Q("prefix",postcode=query),
        "A": A("terms", field="postcode")
    }

def multimatch_nummeraanduiding_Q(query):
    """Create query/aggregation for nummeraanduiding search"""
    log.debug('%20s %s', multimatch_nummeraanduiding_Q.__name__, query)

    """
    "straatnaam": "Eerste Helmersstraat",
    "buurtcombinatie": "Helmersbuurt",
    "huisnummer": 104,
    "huisnummer_variation": 104,
    "subtype": "Verblijfsobject",
    "postcode": "1054EG-104G",
    "adres": "Eerste Helmersstraat 104G",
    """

    return {
        'A': None,
        'Q': Q(
            "multi_match",
            query=query,
            # type="most_fields",
            # type="phrase",
            type="phrase_prefix",
            slop=12,  # match "stephan preeker" with "stephan jacob preeker"
            max_expansions=12,
            fields=[
                'naam',
                'straatnaam',
                'straatnaam_nen',
                'straatnaam_ptt',
                'aanduiding',
                'adres',
                'postcode',
                'huisnummer'
                'huisnummer_variation',
            ]
        )
    }