"""
==================================================
 Individual search queries
--------------------------------------------------
 Each of these functions builds a query and,
 if needed an aggregation as well.
 They all return a dict with the Q and A keyes
==================================================
"""

def kadaster_object_Q(query):
    """Create query/aggregation for kadaster search"""
    return {
        'A': None,
        'Q': Q(
        "multi_match",
        query=query,
        boost=3,
        type="phrase_prefix",
        fields=[
            "aanduiding"]
        )
    }

def kadaster_subject_Q(query):
    """Create query/aggregation for kadaster search"""
    return {
        'A': None,
        'Q': Q(
        "multi_match",
        query=query,
        boost=3,
        type="phrase_prefix",
        fields=[
            "aanduiding"]
        )
    }

