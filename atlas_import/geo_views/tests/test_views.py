from django.db import connection
from django.test import TestCase

from datasets.bag.tests import factories as bag_factories
from datasets.lki.tests import factories as lki_factories
from datasets.wkpb.tests import factories as wkpb_factories


class ViewsTest(TestCase):

    def get_row(self, view_name):
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM " + str(view_name) + " LIMIT 1")
        result = cursor.fetchone()
        self.assertIsNotNone(result)

        return dict(zip([col[0] for col in cursor.description], result))

    def test_bag_ligplaats(self):
        bag_factories.LigplaatsFactory.create()
        row = self.get_row('geo_bag_ligplaats')
        self.assertIn("id", row)
        self.assertIn("geometrie", row)
        # self.assertIn("display", row)
        # self.assertIn("type", row)
        # self.assertIn("uri", row)

    def test_bag_standplaats(self):
        bag_factories.StandplaatsFactory.create()
        row = self.get_row('geo_bag_standplaats')
        self.assertIn("id", row)
        self.assertIn("geometrie", row)
        # self.assertIn("display", row)
        # self.assertIn("type", row)
        # self.assertIn("uri", row)

    def test_bag_verblijfsobject(self):
        bag_factories.VerblijfsobjectFactory.create()
        row = self.get_row('geo_bag_verblijfsobject')
        self.assertIn("id", row)
        self.assertIn("geometrie", row)
        # self.assertIn("display", row)
        # self.assertIn("type", row)
        # self.assertIn("uri", row)

    def test_bag_pand(self):
        bag_factories.PandFactory.create()
        row = self.get_row('geo_bag_pand')
        self.assertIn("id", row)
        self.assertIn("geometrie", row)
        # self.assertIn("display", row)
        # self.assertIn("type", row)
        # self.assertIn("uri", row)

    def test_bag_bouwblok(self):
        bag_factories.BouwblokFactory.create()
        row = self.get_row('geo_bag_bouwblok')
        self.assertIn("id", row)
        self.assertIn("geometrie", row)
        # self.assertIn("display", row)
        # self.assertIn("type", row)
        # self.assertIn("uri", row)

    def test_bag_buurt(self):
        bag_factories.BuurtFactory.create()
        row = self.get_row('geo_bag_buurt')
        self.assertIn("id", row)
        self.assertIn("geometrie", row)
        # self.assertIn("display", row)
        # self.assertIn("type", row)
        # self.assertIn("uri", row)

    def test_bag_buurtcombinatie(self):
        bag_factories.BuurtcombinatieFactory.create()
        row = self.get_row('geo_bag_buurtcombinatie')
        self.assertIn("id", row)
        self.assertIn("geometrie", row)
        # self.assertIn("display", row)
        # self.assertIn("type", row)
        # self.assertIn("uri", row)

    def test_bag_gebiedsgerichtwerken(self):
        bag_factories.GebiedsgerichtwerkenFactory.create()
        row = self.get_row('geo_bag_gebiedsgerichtwerken')
        self.assertIn("id", row)
        self.assertIn("geometrie", row)
        # self.assertIn("display", row)
        # self.assertIn("type", row)
        # self.assertIn("uri", row)

    def test_bag_grootstedelijkgebied(self):
        bag_factories.GrootstedelijkGebiedFactory.create()
        row = self.get_row('geo_bag_grootstedelijkgebied')
        self.assertIn("id", row)
        self.assertIn("geometrie", row)
        # self.assertIn("display", row)
        # self.assertIn("type", row)
        # self.assertIn("uri", row)

    def test_bag_stadsdeel(self):
        bag_factories.StadsdeelFactory.create()
        row = self.get_row('geo_bag_stadsdeel')
        self.assertIn("id", row)
        self.assertIn("geometrie", row)
        # self.assertIn("display", row)
        # self.assertIn("type", row)
        # self.assertIn("uri", row)

    def test_bag_unesco(self):
        bag_factories.UnescoFactory.create()
        row = self.get_row('geo_bag_unesco')
        self.assertIn("id", row)
        self.assertIn("geometrie", row)
        # self.assertIn("display", row)
        # self.assertIn("type", row)
        # self.assertIn("uri", row)

    def test_lki_gemeente(self):
        lki_factories.GemeenteFactory.create()
        row = self.get_row('geo_lki_gemeente')
        self.assertIn("id", row)
        self.assertIn("geometrie", row)
        self.assertIn("gemeentenaam", row)
        # self.assertIn("display", row)
        # self.assertIn("type", row)
        # self.assertIn("uri", row)

    def test_lki_kadastrale_gemeente(self):
        lki_factories.KadastraleGemeenteFactory.create()
        row = self.get_row('geo_lki_kadastralegemeente')
        self.assertIn("id", row)
        self.assertIn("geometrie", row)
        self.assertIn("code", row)
        # self.assertIn("display", row)
        # self.assertIn("type", row)
        # self.assertIn("uri", row)

    def test_lki_sectie(self):
        lki_factories.SectieFactory.create()
        row = self.get_row('geo_lki_sectie')
        self.assertIn("id", row)
        self.assertIn("geometrie", row)
        self.assertIn("code", row)
        # self.assertIn("display", row)
        # self.assertIn("type", row)
        # self.assertIn("uri", row)

    def test_lki_kadastraal_object(self):
        lki_factories.KadastraalObjectFactory.create()
        row = self.get_row('geo_lki_kadastraalobject')
        self.assertIn("id", row)
        self.assertIn("geometrie", row)
        self.assertIn("perceelnummer", row)
        # self.assertIn("display", row)
        # self.assertIn("type", row)
        # self.assertIn("uri", row)

    def test_wkpb(self):
        wkpb_factories.BeperkingKadastraalObjectFactory.create()
        row = self.get_row('geo_wkpb')
        self.assertIn("id", row)
        self.assertIn("geometrie", row)
        self.assertIn("beperkingtype_id", row)
        # self.assertIn("display", row)
        # self.assertIn("type", row)
        # self.assertIn("uri", row)
