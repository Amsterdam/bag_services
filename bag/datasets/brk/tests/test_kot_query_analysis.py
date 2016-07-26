from django.test import TestCase

from datasets.brk.queries import KadastraalObjectQuery


class KadastraalObjectQueryTest(TestCase):

    def test_parsing(self):
        test_cases = [
            # tokens, gemeente_code, gemeente_naam, sectie, object_nummer, index_letter, index_nummer
            (['asd', '15', 's', '00045'], 'asd15', None, 's', '00045', None, None),
            (['asd', '15', 's', '00045', 'g'], 'asd15', None, 's', '00045', 'g', None),
            (['asd', '15', 's', '00045', 'g', '0000'], 'asd15', None, 's', '00045', 'g', '0000'),
            (['aalsmeer', 'b'], None, 'aalsmeer', 'b', None, None, None, None),
            (['amr', '03'], 'amr03', None, None, None, None, None),
            (['amr', '03', 'b'], 'amr03', None, 'b', None, None, None),
            (['amr', '03', 'b', '334'], 'amr03', None, 'b', '334', None, None),
            (['amr', '03', 'b', '03347'], 'amr03', None, 'b', '03347', None, None),
            (['amr', '03', 'b', '3347'], 'amr03', None, 'b', '3347', None, None),
            (['amr', '03', 'b', '03347', 'g', '0000'], 'amr03', None, 'b', '03347', 'g', '0000'),
            (['amr', '03', 'b', '05054', 'a', '0002'], 'amr03', None, 'b', '05054', 'a', '0002'),
            (['amr', '03', 'b', '5054', 'a', '2'], 'amr03', None, 'b', '5054', 'a', '2'),
            (['amr', '03', 'b', '05054', '0002'], 'amr03', None, 'b', '05054', 'a', '0002'),
            (['amr', '03', 'b', '5054', '2'], 'amr03', None, 'b', '5054', 'a', '2'),
            (['aalsmeer', 'b', '03347'], None, 'aalsmeer', 'b', '03347', None, None),
            (['aalsmeer', 'b', '3347'], None, 'aalsmeer', 'b', '3347', None, None),
            (['aalsmeer', 'b', '03347', 'g', '0000'], None, 'aalsmeer', 'b', '03347', 'g', '0000'),
            (['aalsmeer', 'b', '05054', 'a', '0002'], None, 'aalsmeer', 'b', '05054', 'a', '0002'),
            (['aalsmeer', 'b', '5054', 'a', '2'], None, 'aalsmeer', 'b', '5054', 'a', '2'),
            (['aalsmeer', 'b', '05054', '0002'], None, 'aalsmeer', 'b', '05054', 'a', '0002'),
            (['aalsmeer', 'b', '5054', '2'], None, 'aalsmeer', 'b', '5054', 'a', '2'),
            (['amr', '03', 'b', '47'], 'amr03', None, 'b', '47', None, None),
            (['aalsmeer', 'b', '47'], None, 'aalsmeer', 'b', '47', None, None),
            (['asd', '15', 'ar', '45', 'g', '0'], 'asd15', None, 'ar', '45', 'g', '0'),
            (['asd', '15', 'a', 'konijn', 'g', 'eend'], 'asd15', None, 'a', None, 'g', None),
        ]

        for t in test_cases:
            q = KadastraalObjectQuery(t[0])
            message = " ".join(t[0])
            self.assertEqual(t[1], q.gemeente_code, message)
            self.assertEqual(t[2], q.gemeente_naam, message)
            self.assertEqual(t[3], q.sectie, message)
            self.assertEqual(t[4], q.object_nummer, message)
            self.assertEqual(t[5], q.index_letter, message)
            self.assertEqual(t[6], q.index_nummer, message)


