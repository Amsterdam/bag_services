"""
Helper methods for validating user input and deciding
what end user want

https://datapunt.atlassian.net/wiki/display/ATLAS/Zoeken
"""

from atlas_api import input_handling as ih

# import string
# import random


from django.test import TestCase


class TokenizeTest(TestCase):

    def test_tokenize(self):
        """
        """
        s = "aaa bbb ccc ddd"

        _, tokens = ih.clean_tokenize(s)
        self.assertEqual(
            ["aaa", "bbb", "ccc", "ddd"],
            tokens)

    def test_dirty_adres(self):
        """
        """
        s = "Nieuwe achtergracht 105-3HA2"
        _, tokens = ih.clean_tokenize(s)

        self.assertEqual(
            ["nieuwe", "achtergracht", "105", "3", "ha", "2"],
            tokens)

        s = "Nieuwe achtergracht 105-3 HA 2"
        _, tokens = ih.clean_tokenize(s)

        self.assertEqual(
            [
                'nieuwe', 'achtergracht',
                '105', '3', 'ha', '2'],
            tokens
        )

    def test_postcode_check(self):
        """
        """
        self.assertTrue(
            ih.is_postcode("", ["1013", "AW"]))

        self.assertTrue(
            ih.is_postcode("", ["1013", "A"]))

        self.assertTrue(
            ih.is_postcode("", ["1013"]))

        # yep still valid..
        self.assertTrue(
            ih.is_postcode("", ["0001", ]))

        self.assertFalse(
            ih.is_postcode("", ["101"]))

        self.assertFalse(
            ih.is_postcode("", ["1013", "AWX"]))

    def test_true_token_and_test(self):
        """
        """
        true_test_cases = [
            "1013",
            "1013AW",
            "1013 AW",
        ]

        for test in true_test_cases:
            _, tokens = ih.clean_tokenize(test)
            self.assertTrue(ih.is_postcode(test, tokens))

    def test_false_token_and_postcode(self):

        false_test_cases = [
            "10",
            "101",
            "101 AW",
            "10134",
            "1013 56",
            "1013 ABC",
        ]

        for test in false_test_cases:
            _, tokens = ih.clean_tokenize(test)
            self.assertFalse(ih.is_postcode(test, tokens))

    def test_postcode_huisnummer(self):
        """
        """
        test = "1013 AW 1"
        _, tokens = ih.clean_tokenize(test)
        self.assertTrue(ih.is_postcode_huisnummer(test, tokens))

        test = "1013 AW 105"
        _, tokens = ih.clean_tokenize(test)
        self.assertTrue(ih.is_postcode_huisnummer(test, tokens))

        test = "1013 A 1"
        _, tokens = ih.clean_tokenize(test)
        self.assertFalse(ih.is_postcode_huisnummer(test, tokens))

        test = "1013 AZ X"
        _, tokens = ih.clean_tokenize(test)
        self.assertFalse(ih.is_postcode_huisnummer(test, tokens))

        test = "101 AW 1"
        _, tokens = ih.clean_tokenize(test)
        self.assertFalse(ih.is_postcode_huisnummer(test, tokens))

        test = "1013 AWX 1"
        _, tokens = ih.clean_tokenize(test)
        self.assertFalse(ih.is_postcode_huisnummer(test, tokens))

    def test_first_number(self):
        test = "ABD-10!CD"
        _, tokens = ih.clean_tokenize(test)
        self.assertEqual(
            ih.first_number(tokens), (1, '10'))

        test = "ABD10CD"
        _, tokens = ih.clean_tokenize(test)
        self.assertEqual(
            ih.first_number(tokens), (1, '10'))

        test = "ABD CD"
        _, tokens = ih.clean_tokenize(test)
        self.assertEqual(
            ih.first_number(tokens), (-1, ''))

    def test_true_meetbout(self):

        true_cases = [
            '10234',
            '102345',
            '1023456',
            '10234568',
        ]

        for test in true_cases:
            clean_qs, tokens = ih.clean_tokenize(test)
            self.assertTrue(ih.is_meetbout(clean_qs, tokens))

    def test_false_meetbout(self):

        false_cases = [
            '10',
            '101',
            '1014',
            '101S2334',
            '1O122334',
            '102A4568 AKJS',
            '102A4568 AKJS',

        ]

        for test in false_cases:
            clean_qs, tokens = ih.clean_tokenize(test)
            self.assertFalse(ih.is_meetbout(clean_qs, tokens))

    def test_true_bouwblok(self):

        true_cases = [
            'AA12',
            'CA 99',
            'CA-99',
        ]

        for test in true_cases:
            clean_qs, tokens = ih.clean_tokenize(test)
            self.assertTrue(ih.is_bouwblok(clean_qs, tokens))

    def test_false_bouwblok(self):

        false_cases = [
            '12A',
            'A12',
            'A9 CA',
            '99 CA BB',
        ]

        for test in false_cases:
            clean_qs, tokens = ih.clean_tokenize(test)
            self.assertFalse(ih.is_bouwblok(clean_qs, tokens))

    def test_true_could_be_bouwblok(self):

        true_cases = [
            'AA1',
            'A',
            'AB-99',
        ]

        for test in true_cases:
            clean_qs, tokens = ih.clean_tokenize(test)
            self.assertTrue(ih.could_be_bouwblok(clean_qs, tokens))

    def test_false_could_be_bouwblok(self):

        false_cases = [
            '12ABC',
            '12',
            'A9 CA',
            '99 CA BB',
            '999 C',
        ]

        for test in false_cases:
            clean_qs, tokens = ih.clean_tokenize(test)
            self.assertFalse(ih.could_be_bouwblok(clean_qs, tokens))

    def test_true_street_name_and_huisnummer(self):
        true_cases = [
            'ABC 1'
            'Nieuwe achtergracht 105 2'
            'Nieuwe achtergracht 105'
            'P C HOOFT 10'
        ]

        for test in true_cases:
            qs, tokens = ih.clean_tokenize(test)
            self.assertTrue(ih.is_straat_huisnummer(qs, tokens))

    def test_false_street_name_and_huisnummer(self):

        false_cases = [
            'Nieuwe achtergracht',
            '1013WR 5',
        ]

        for test in false_cases:
            qs, tokens = ih.clean_tokenize(test)
            self.assertFalse(ih.is_straat_huisnummer(qs, tokens))

    def test_true_kadaster(self):
        """
        """
        true_cases = [
            'ASD15',
            'ASD15 S',
            'ASD15 S 00045',
        ]

        for test in true_cases:
            qs, tokens = ih.clean_tokenize(test)
            self.assertTrue(ih.is_kadaster_object(qs, tokens))

    def test_false_kadaster(self):
        """
        """
        false_cases = [
            'ASDE15 S',
            'AS',
            'ASD150 S 00045',
            'ASD 15 S'
            'ASD 15'
        ]

        for test in false_cases:
            _, tokens = ih.clean_tokenize(test)
            self.assertFalse(ih.is_kadaster_object(test, tokens))

    def test_true_gemeente_kadaster(self):
            """
            """
            true_cases = [
                'Amsterdam s',
                'Amsterdam ak',
                'Amsterdam s 001',
                'Sloten G 00045',
            ]

            for test in true_cases:
                qs, tokens = ih.clean_tokenize(test)
                self.assertTrue(
                    ih.is_gemeente_kadaster_object(qs, tokens))

    def test_false_gemeente_kadaster(self):
        """
        """
        false_cases = [
            'Amsterdam 15S',
            'Amsterdam 3',
            'ASD15 S 00045',
            'ASD 15 S'
            'ASD 15'
            'A SDX 15'
        ]

        for test in false_cases:
            _, tokens = ih.clean_tokenize(test)
            self.assertFalse(ih.is_gemeente_kadaster_object(test, tokens))
