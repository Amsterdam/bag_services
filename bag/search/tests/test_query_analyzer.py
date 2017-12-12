from unittest import TestCase

from search.query_analyzer import QueryAnalyzer, KadastraalObjectQuery


class QueryAnalyzerTest(TestCase):
    def _check(self, method, name, true_cases, false_cases):
        for query in true_cases:
            analyzed_query = QueryAnalyzer(query)
            self.assertTrue(
                method(analyzed_query),
                "{} should be {}".format(query, name))

        for query in false_cases:
            analyzed_query = QueryAnalyzer(query)
            self.assertFalse(
                method(analyzed_query),
                "{} should be {}".format(query, name))

    def test_is_kadastraal_object(self):
        self._check(QueryAnalyzer.is_kadastraal_object_prefix,
                    "kadastraal object prefix",
                    true_cases=[
                        'ASD15',
                        'ASD15 S',
                        'ASD15 S 00045',
                        'Amsterdam s',
                        'Amsterdam ak',
                        'Amsterdam s 001',
                        'Sloten G 00045',
                    ],
                    false_cases=[
                        'ASDE15 S',
                        'AS',
                        'ASD150 S 00045',
                        'ASD 15 S',
                        'ASD 15',
                        'Amsterdam 15S',
                        'Amsterdam 3',
                        'A SDX 15',
                    ])

    def test_get_kadastraal_object_query(self):
        test_cases = [
            ('ASD15', 'asd15', None, None, None, None, None),
            ('ASD15 S', 'asd15', None, 's', None, None, None),
            ('ASD15 S 00045', 'asd15', None, 's', '00045', None, None),
            ('Amsterdam s', None, 'amsterdam', 's', None, None, None),
            ('Amsterdam ak', None, 'amsterdam', 'ak', None, None, None),
            ('Amsterdam s 001', None, 'amsterdam', 's', '001', None, None),
            ('Sloten G 00045', None, 'sloten', 'g', '00045', None, None),
        ]

        for case in test_cases:
            analyzer = QueryAnalyzer(case[0])
            kot_query = analyzer.get_kadastraal_object_query()
            self.assertEqual(case[1], kot_query.gemeente_code)
            self.assertEqual(case[2], kot_query.gemeente_naam)
            self.assertEqual(case[3], kot_query.sectie)
            self.assertEqual(case[4], kot_query.object_nummer)
            self.assertEqual(case[5], kot_query.index_letter)
            self.assertEqual(case[6], kot_query.index_nummer)

    def test_is_bouwblow_prefix(self):
        self._check(QueryAnalyzer.is_bouwblok_prefix,
                    "bouwblok prefix",
                    true_cases=[
                        'AA1',
                        'A',
                        'AB-99',
                    ],
                    false_cases=[
                        '12ABC',
                        '12',
                        'A9 CA',
                        '99 CA BB',
                        '999 C',
                    ])

    def test_is_bouwblow_exact(self):
        self._check(QueryAnalyzer.is_bouwblok_exact,
                    "bouwblok",
                    true_cases=[
                        'AA12',
                        'CA 99',
                        'CA-99',
                    ],
                    false_cases=[
                        '12A',
                        'A12',
                        'A9 CA',
                        '99 CA BB',
                    ])

    def test_is_postcode_prefix(self):
        self._check(QueryAnalyzer.is_postcode_prefix,
                    "postcode prefix",
                    true_cases=[
                        "1013AW",
                        "1013 AW",
                        "1013",
                        "0001",
                    ],
                    false_cases=[
                        "10",
                        "101",
                        "101 AW",
                        "1013 AWX",
                        "10134",
                        "1013 56",
                        "1013 ABC",
                    ])

    def test_is_postcode_huisnummer(self):
        self._check(QueryAnalyzer.is_postcode_huisnummer_prefix,
                    "postcode/huisnummer",
                    true_cases=[
                        "1013 AW 1",
                        "1013 AW 105",
                        "1074XV 50-2RA",
                    ],
                    false_cases=[
                        "1013 A 1",
                        "1013 AZ X",
                        "101 AW 1",
                        "1013 AWX 1",
                    ])

    def test_get_postcode_huisnummer_toevoeging(self):
        test_cases = [
            ("1013 AW 1", "1013aw", 1, "1"),
            ("1013 AW 105", "1013aw", 105, "105"),
            ("1074XV 50-2RA", "1074xv", 50, "50 2 r a"),
        ]
        for case in test_cases:
            analyzer = QueryAnalyzer(case[0])
            postcode, huisnummer, toevoeging = analyzer.get_postcode_huisnummer_toevoeging()  # noqa
            self.assertEqual(case[1], postcode)
            self.assertEqual(case[2], huisnummer)
            self.assertEqual(case[3], toevoeging)

    def test_is_straat_huisnummer(self):
        self._check(QueryAnalyzer.is_straatnaam_huisnummer_prefix,
                    "straatnaam/huisnummer",
                    true_cases=[
                        'ABC 1',
                        'Nieuwe achtergracht 105 2',
                        'Nieuwe achtergracht 105',
                        'P C HOOFT 10',
                    ],
                    false_cases=[
                        'Nieuwe achtergracht',
                        '1013WR 5',
                    ])

    def test_get_straat_huisnummer_toevoeging(self):
        test_cases = [
            ('ABC 1', 'abc', 1, '1'),
            ('Nieuwe achtergracht 105 2', 'nieuwe achtergracht', 105, '105 2'),
            ('Nieuwe achtergracht 105', 'nieuwe achtergracht', 105, '105'),
            ('P C HOOFT 10', 'p c hooft', 10, '10'),
            ('Eerste Jan van der Heijdenstraat 22-2A', 'eerste jan van der heijdenstraat', 22, '22 2 a'),  # noqa

        ]

        for case in test_cases:
            analyzer = QueryAnalyzer(case[0])
            straat, huisnummer, toevoeging = analyzer.get_straatnaam_huisnummer_toevoeging()
            self.assertEqual(case[1], straat)
            self.assertEqual(case[2], huisnummer)
            self.assertEqual(case[3], toevoeging)


class KadastraalObjectQueryTest(TestCase):
    def test_parsing(self):
        test_cases = [
            # tokens, gemeente_code, gemeente_naam, sectie, object_nummer, index_letter, index_nummer     # noqa
            (['asd', '15', 's', '00045'],
              'asd15', None, 's', '00045', None, None),                      # noqa
            (['asd', '15', 's', '00045', 'g'],
             'asd15', None, 's', '00045', 'g', None),
            (['asd', '15', 's', '00045', 'g', '0000'],
             'asd15', None, 's', '00045', 'g', '0000'),
            (['aalsmeer', 'b'], None, 'aalsmeer', 'b',
              None, None, None, None),
            (['amr', '03'], 'amr03', None, None, None, None, None),
            (['amr', '03', 'b'], 'amr03', None, 'b', None, None, None),
            (['amr', '03', 'b', '334'], 'amr03', None, 'b', '334', None, None),
            (['amr', '03', 'b', '03347'],
              'amr03', None, 'b', '03347', None, None),
            (['amr', '03', 'b', '3347'],
              'amr03', None, 'b', '3347', None, None),
            (['amr', '03', 'b', '03347', 'g', '0000'],
              'amr03', None, 'b', '03347', 'g', '0000'),
            (['amr', '03', 'b', '05054', 'a', '0002'],
              'amr03', None, 'b', '05054', 'a', '0002'),
            (['amr', '03', 'b', '5054', 'a', '2'],
              'amr03', None, 'b', '5054', 'a', '2'),
            (['amr', '03', 'b', '05054', '0002'],
              'amr03', None, 'b', '05054', 'a', '0002'),
            (['amr', '03', 'b', '5054', '2'],
              'amr03', None, 'b', '5054', 'a', '2'),

            (['aalsmeer', 'b', '03347'], None, 'aalsmeer', 'b', '03347', None, None),
            (['aalsmeer', 'b', '3347'],
             None, 'aalsmeer', 'b', '3347', None, None),
            (['aalsmeer', 'b', '03347', 'g', '0000'],
             None, 'aalsmeer', 'b', '03347', 'g', '0000'),
            (['aalsmeer', 'b', '05054', 'a', '0002'],
             None, 'aalsmeer', 'b', '05054', 'a', '0002'),
            (['aalsmeer', 'b', '5054', 'a', '2'],
             None, 'aalsmeer', 'b', '5054', 'a', '2'),
            (['aalsmeer', 'b', '05054', '0002'],
             None, 'aalsmeer', 'b', '05054', 'a', '0002'),
            (['aalsmeer', 'b', '5054', '2'],
             None, 'aalsmeer', 'b', '5054', 'a', '2'),
            (['amr', '03', 'b', '47'], 'amr03', None, 'b', '47', None, None),
            (['aalsmeer', 'b', '47'], None, 'aalsmeer', 'b', '47', None, None),
            (['asd', '15', 'ar', '45', 'g', '0'],
             'asd15', None, 'ar', '45', 'g', '0'),
            (['asd', '15', 'a', 'konijn', 'g', 'eend'], 'asd15', None, 'a', None, 'g', None),  # noqa
        ]

        for case in test_cases:
            q = KadastraalObjectQuery(case[0])
            message = " ".join(case[0])
            self.assertEqual(case[1], q.gemeente_code, message)
            self.assertEqual(case[2], q.gemeente_naam, message)
            self.assertEqual(case[3], q.sectie, message)
            self.assertEqual(case[4], q.object_nummer, message)
            self.assertEqual(case[5], q.index_letter, message)
            self.assertEqual(case[6], q.index_nummer, message)
