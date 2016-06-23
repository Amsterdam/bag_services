import datetime
from django.test import TestCase
from .. import uva2


class UvaHelperTest(TestCase):

    def test_uva_datum(self):
        self.assertEqual(uva2.uva_datum("19000101"), datetime.date(1900, 1, 1))
        self.assertEqual(uva2.uva_datum("19770724"), datetime.date(1977, 7, 24))
        self.assertEqual(uva2.uva_datum(""), None)

    def test_uva_indicatie(self):
        self.assertFalse(uva2.uva_indicatie(''))
        self.assertFalse(uva2.uva_indicatie('N'))
        self.assertTrue(uva2.uva_indicatie('J'))

    def test_uva_geldig(self):
        self.assertTrue(uva2.uva_geldig("", ""))
        self.assertTrue(uva2.uva_geldig("19000101", ""))
        self.assertTrue(uva2.uva_geldig("19000101", "20251201"))
        self.assertFalse(uva2.uva_geldig("19000101", "19801101"))
        self.assertFalse(uva2.uva_geldig("20301113", "20311113"))

