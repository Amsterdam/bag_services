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

log = logging.getLogger(__name__)

BRK = settings.ELASTIC_INDICES['BRK']


class KadastraalObjectQuery(object):
    """
    Combines all KOT query analysis into a single helper class.
    """

    gemeente_code = None  # Example: ASD15
    gemeente_naam = None  # Example: Amsterdam
    sectie = None  # Example: S
    object_nummer = None  # Example: 0002
    index_letter = None  # Example: A
    index_nummer = None  # Example: 0000

    def __init__(self, tokens: [str]):
        """
        Initialize the query with the individual Kadastraal Object tokens.

        Examples:
        ['asd', 15','s', '00000','a','0000']
        ['amsterdam', 's', '00000', 'a', '0000']

        ['gemeente', 'sectie', 'object-nummer', 'index-letter', 'index-nummer']

        :param tokens:
        """
        if len(tokens) < 2:
            # Hier kunnen we niets mee
            return

        # We zorgen ervoor dat alle indices bestaan. Dit om te voorkomen dat we de hele tijd moeilijk
        # lopen te checken
        tokens = tokens[:] + [None, None, None]

        # Gemeente-code (twee tokens, waarvan het eerste drie letters) of Gemeente-naam (één token)
        if len(tokens[0]) == 3:
            self.gemeente_code = tokens[0] + tokens[1]
            tokens = tokens[2:]
        else:
            self.gemeente_naam = tokens[0]
            tokens = tokens[1:]

        self.sectie = tokens[0]
        self.object_nummer = tokens[1]

        # Vermoedelijk: index-letter, maar het kan ook een getal zijn met een impliciete index-letter 'A'
        index_thingie = tokens[2]
        if index_thingie in ['a', 'g']:
            self.index_letter = index_thingie
            self.index_nummer = tokens[3]
        elif index_thingie:
            self.index_letter = 'a'
            self.index_nummer = index_thingie

        # clean-up index nummer and object nummer
        if self.object_nummer and not self.object_nummer.isdigit():
            self.object_nummer = None

        if self.index_nummer and not self.index_nummer.isdigit():
            self.index_nummer = None

    def object_nummer_is_exact(self):
        """
        Returns true if the object nummer is an exact query (i.e. 5 digits long)
        """
        return self.object_nummer and len(self.object_nummer) == 5

    def index_nummer_is_exact(self):
        """
        Returns true if the index nummer is an exact query (i.e. 4 digits long)
        """
        return self.index_nummer and len(self.index_nummer) == 4


# noinspection PyPep8Naming
def kadaster_object_Q(query: str, tokens: [str] = None, num: int = None):
    """
    Create query/aggregation for kadaster object search

    kad_code = ['ASD15','S', '00000','A','0000']

    ASD15     S      00000         A    0000
    gem_code  Sectie objectnr indexl indexnr
    City      L1     D1           L2      D2
    0         1      2             3       4

    """
    kot_query = KadastraalObjectQuery(tokens)
    must = []

    if kot_query.gemeente_code:
        must.append({'term': {'gemeente_code': kot_query.gemeente_code}})

    if kot_query.gemeente_naam:
        must.append({'term': {'gemeente': kot_query.gemeente_naam}})

    if kot_query.sectie:
        must.append({'term': {'sectie': kot_query.sectie}})

    if kot_query.object_nummer and int(kot_query.object_nummer):
        if kot_query.object_nummer_is_exact():
            must.append({'term': {'objectnummer.int': int(kot_query.object_nummer)}})
        else:
            must.append({'prefix': {'objectnummer.raw': int(kot_query.object_nummer)}})

    if kot_query.index_letter:
        must.append(Q('term', indexletter=kot_query.index_letter))

    if kot_query.index_nummer and int(kot_query.index_nummer):
        if kot_query.index_nummer_is_exact():
            must.append({'term': {'indexnummer.int': int(kot_query.index_nummer)}})
        else:
            must.append({'prefix': {'indexnummer.raw': int(kot_query.index_nummer)}})

    return {
        'Q': Q(
            'bool',
            must=must
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
