from django.db import connection
from django.test import TestCase


class ViewsTest(TestCase):
    fixtures = ['dataset.json']

    def get_row(self, view_name):
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM {} LIMIT 1".format(view_name))
        row = dict(zip([col[0] for col in cursor.description], cursor.fetchone()))
        return row

    def test_ligplaats(self):
        row = self.get_row('geo_bag_ligplaats')
        self.assertIn("id", row)
        self.assertIn("geometrie", row)

    def test_standplaats(self):
        row = self.get_row('geo_bag_standplaats')
        self.assertIn("id", row)
        self.assertIn("geometrie", row)

    def test_verblijfsobject(self):
        row = self.get_row('geo_bag_verblijfsobject')
        self.assertIn("id", row)
        self.assertIn("geometrie", row)

    def test_pand(self):
        row = self.get_row('geo_bag_pand')
        self.assertIn("id", row)
        self.assertIn("geometrie", row)

