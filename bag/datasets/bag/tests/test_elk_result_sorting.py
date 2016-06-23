"""
Test Helper methods for sorting endresutls
and give 'logical' answers what end user want
"""


from django.test import TestCase
from datasets.bag import queries

# elk eerste jan van der heidenstraat 2 results
from .testresult_data import test_elk_vbo_result

from atlas_api import input_handling as ih


class Hit(object):

    def __init__(self, **entries):
        self.__dict__.update(entries)


test_elk_vbo_result = [Hit(**h) for h in test_elk_vbo_result]


class SortingNummeraanduidingTest(TestCase):
    """
    test the logical sorting
    """

    def test_postcode_sort(self):

        query = "1072 tt 2"
        query, tokens = ih.clean_tokenize(query)

        sorted_result = queries.straat_huisnummer_sorting(
                test_elk_vbo_result, query, tokens, 2)

        self.assertEqual(len(sorted_result), 10)

        self.assertEqual(sorted_result[0].toevoeging, "2")
        self.assertEqual(sorted_result[1].toevoeging, "2 A")
        self.assertEqual(sorted_result[2].toevoeging, "20 H")
        self.assertEqual(sorted_result[3].toevoeging, "20 1")

    def test_straatnaam_sort(self):
        query = "Eerste Jan van der Heijdenstraat 2"

        query, tokens = ih.clean_tokenize(query)
        numbers = ih.number_list(tokens)

        i = numbers[0][0]

        sorted_result = queries.straat_huisnummer_sorting(
                test_elk_vbo_result, query, tokens, i)

        self.assertEqual(len(sorted_result), 10)

        self.assertEqual(sorted_result[0].toevoeging, "2")
        self.assertEqual(sorted_result[1].toevoeging, "2 A")
        self.assertEqual(sorted_result[2].toevoeging, "20 H")
        self.assertEqual(sorted_result[3].toevoeging, "20 1")
