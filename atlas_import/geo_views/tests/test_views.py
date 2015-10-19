from django.db import connection
from django.test import TestCase

from datasets.bag.tests import factories as bag_factories
from datasets.lki.tests import factories as lki_factories
from datasets.wkpb.tests import factories as wkpb_factories



class ViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        bag_factories.LigplaatsFactory.create()
        bag_factories.StandplaatsFactory.create()
        bag_factories.VerblijfsobjectFactory.create()
        bag_factories.PandFactory.create()
        lki_factories.GemeenteFactory.create()
        lki_factories.KadastraleGemeenteFactory.create()
        lki_factories.KadastraalObjectFactory.create()
        lki_factories.SectieFactory.create()
        wkpb_factories.BeperkingKadastraalObjectFactory.create()



    def get_row(self, view_name):
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM " + str(view_name) + " LIMIT 1")
        row = dict(zip([col[0] for col in cursor.description], cursor.fetchone()))
        return row

    def test_bag_ligplaats(self):
        row = self.get_row('geo_bag_ligplaats')
        self.assertIn("id", row)
        self.assertIn("geometrie", row)

    def test_bag_standplaats(self):
        row = self.get_row('geo_bag_standplaats')
        self.assertIn("id", row)
        self.assertIn("geometrie", row)

    def test_bag_verblijfsobject(self):
        row = self.get_row('geo_bag_verblijfsobject')
        self.assertIn("id", row)
        self.assertIn("geometrie", row)

    def test_bag_pand(self):
        row = self.get_row('geo_bag_pand')
        self.assertIn("id", row)
        self.assertIn("geometrie", row)

    def test_lki_gemeente(self):
        row = self.get_row('geo_lki_gemeente')
        self.assertIn("id", row)
        self.assertIn("geometrie", row)
        self.assertIn("gemeentenaam", row)

    def test_lki_kadastrale_gemeente(self):
        row = self.get_row('geo_lki_kadastralegemeente')
        self.assertIn("id", row)
        self.assertIn("geometrie", row)
        self.assertIn("code", row)

    def test_lki_sectie(self):
        row = self.get_row('geo_lki_sectie')
        self.assertIn("id", row)
        self.assertIn("geometrie", row)
        self.assertIn("code", row)

    def test_lki_kadastraal_object(self):
        row = self.get_row('geo_lki_kadastraalobject')
        self.assertIn("id", row)
        self.assertIn("geometrie", row)
        self.assertIn("perceelnummer", row)

    def test_wkpb(self):
        row = self.get_row('geo_wkpb')
        self.assertIn("id", row)
        self.assertIn("geometrie", row)
        self.assertIn("beperkingtype_id", row)
