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
        l = bag_factories.LigplaatsFactory.create()
        bag_factories.NummeraanduidingFactory.create(
            ligplaats=l,
            hoofdadres=True,
        )
        row = self.get_row('geo_bag_ligplaats')
        self.assertEqual(row['id'], l.id)
        self.assertIn("geometrie", row)
        self.assertEqual(row['display'], l.hoofdadres.adres())
        self.assertEqual(row['type'], 'bag/ligplaats')
        self.assertEqual(row['uri'], 'http://update.me/api/bag/ligplaats/{}/'.format(l.id))

    def test_bag_standplaats(self):
        s = bag_factories.StandplaatsFactory.create()
        bag_factories.NummeraanduidingFactory.create(
            standplaats=s,
            hoofdadres=True,
        )
        row = self.get_row('geo_bag_standplaats')
        self.assertEqual(row['id'], s.id)
        self.assertIn("geometrie", row)
        self.assertEqual(row["display"], s.hoofdadres.adres())
        self.assertEqual(row["type"], 'bag/standplaats')
        self.assertIn(row["uri"], 'http://update.me/api/bag/standplaats/{}/'.format(s.id))

    def test_bag_verblijfsobject(self):
        v = bag_factories.VerblijfsobjectFactory.create()
        bag_factories.NummeraanduidingFactory.create(
            verblijfsobject=v,
            hoofdadres=True,
        )
        row = self.get_row('geo_bag_verblijfsobject')
        self.assertEqual(row["id"], v.id)
        self.assertIn("geometrie", row)
        self.assertEqual(row['display'], v.hoofdadres.adres())
        self.assertEqual(row['type'], 'bag/verblijfsobject')
        self.assertEqual(row['uri'], 'http://update.me/api/bag/verblijfsobject/{}/'.format(v.id))

    def test_bag_pand(self):
        p = bag_factories.PandFactory.create()
        row = self.get_row('geo_bag_pand')
        self.assertEqual(row['id'], p.id)
        self.assertIn("geometrie", row)
        self.assertEqual(row['display'], p.id)
        self.assertEqual(row['type'], 'bag/pand')
        self.assertEqual(row['uri'], 'http://update.me/api/bag/pand/{}/'.format(p.id))

    def test_bag_bouwblok(self):
        bb = bag_factories.BouwblokFactory.create()
        row = self.get_row('geo_bag_bouwblok')
        self.assertEqual(row['id'], bb.id)
        self.assertIn("geometrie", row)
        self.assertEqual(row['code'], bb.code)
        self.assertEqual(row['display'], bb.code)
        self.assertEqual(row['type'], 'gebieden/bouwblok')
        self.assertEqual(row['uri'], 'http://update.me/api/gebieden/bouwblok/{}/'.format(bb.id))

    def test_bag_buurt(self):
        b = bag_factories.BuurtFactory.create()
        row = self.get_row('geo_bag_buurt')
        self.assertEqual(row['id'], b.id)
        self.assertIn("geometrie", row)
        self.assertEqual(row['code'], b.code)
        self.assertEqual(row['naam'], b.naam)
        self.assertEqual(row['display'], b.naam)
        self.assertEqual(row['type'], 'gebieden/buurt')
        self.assertEqual(row['uri'], 'http://update.me/api/gebieden/buurt/{}/'.format(b.id))

    def test_bag_buurtcombinatie(self):
        bc = bag_factories.BuurtcombinatieFactory.create()
        row = self.get_row('geo_bag_buurtcombinatie')
        self.assertEqual(row['id'], bc.id)
        self.assertIn("geometrie", row)
        self.assertEqual(row['vollcode'], bc.vollcode)
        self.assertEqual(row['naam'], bc.naam)
        self.assertEqual(row['display'], bc.naam)
        self.assertEqual(row['type'], 'gebieden/buurtcombinatie')
        self.assertEqual(row['uri'], 'http://update.me/api/gebieden/buurtcombinatie/{}/'.format(bc.id))

    def test_bag_gebiedsgerichtwerken(self):
        g = bag_factories.GebiedsgerichtwerkenFactory.create()
        row = self.get_row('geo_bag_gebiedsgerichtwerken')
        self.assertEqual(row['id'], g.id)
        self.assertIn("geometrie", row)
        self.assertEqual(row['code'], g.code)
        self.assertEqual(row['naam'], g.naam)
        self.assertEqual(row['display'], g.naam)
        self.assertEqual(row['type'], 'gebieden/gebiedsgerichtwerken')
        self.assertEqual(row['uri'], 'http://update.me/api/gebieden/gebiedsgerichtwerken/{}/'.format(g.id))

    def test_bag_grootstedelijkgebied(self):
        gg = bag_factories.GrootstedelijkGebiedFactory.create()
        row = self.get_row('geo_bag_grootstedelijkgebied')
        self.assertEqual(row['id'], gg.id)
        self.assertIn("geometrie", row)
        self.assertEqual(row['naam'], gg.naam)
        self.assertEqual(row['display'], gg.naam)
        self.assertEqual(row['type'], 'gebieden/grootstedelijkgebied')
        self.assertEqual(row['uri'], 'http://update.me/api/gebieden/grootstedelijkgebied/{}/'.format(gg.id))

    def test_bag_stadsdeel(self):
        s = bag_factories.StadsdeelFactory.create()
        row = self.get_row('geo_bag_stadsdeel')
        self.assertEqual(row['id'], s.id)
        self.assertIn("geometrie", row)
        self.assertEqual(row['code'], s.code)
        self.assertEqual(row['naam'], s.naam)
        self.assertEqual(row['display'], s.naam)
        self.assertEqual(row['type'], 'gebieden/stadsdeel')
        self.assertEqual(row['uri'], 'http://update.me/api/gebieden/stadsdeel/{}/'.format(s.id))

    def test_bag_unesco(self):
        u = bag_factories.UnescoFactory.create()
        row = self.get_row('geo_bag_unesco')
        self.assertEqual(row['id'], u.id)
        self.assertIn("geometrie", row)
        self.assertEqual(row['naam'], u.naam)
        self.assertEqual(row['display'], u.naam)
        self.assertEqual(row['type'], 'gebieden/unesco')
        self.assertEqual(row['uri'], 'http://update.me/api/gebieden/unesco/{}/'.format(u.id))

    def test_lki_gemeente(self):
        g = lki_factories.GemeenteFactory.create()
        row = self.get_row('geo_lki_gemeente')
        self.assertEqual(row['id'], g.id)
        self.assertIn("geometrie", row)
        self.assertEqual(row['gemeentenaam'], g.gemeentenaam)
        self.assertEqual(row['gemeentecode'], g.gemeentecode)

    def test_lki_kadastrale_gemeente(self):
        g = lki_factories.KadastraleGemeenteFactory.create()
        row = self.get_row('geo_lki_kadastralegemeente')
        self.assertEqual(row['id'], g.id)
        self.assertIn("geometrie", row)
        self.assertEqual(row["code"], g.code)

    def test_lki_sectie(self):
        s = lki_factories.SectieFactory.create()
        row = self.get_row('geo_lki_sectie')
        self.assertEqual(row["id"], s.id)
        self.assertIn("geometrie", row)
        self.assertEqual(row["code"], s.code)

    def test_lki_kadastraal_object(self):
        ko = lki_factories.KadastraalObjectFactory.create()
        row = self.get_row('geo_lki_kadastraalobject')
        self.assertEqual(row["id"], ko.id)
        self.assertIn("geometrie", row)
        self.assertEqual(row["perceelnummer"], ko.perceelnummer)
        self.assertEqual(row["volledige_code"], ko.aanduiding)
        self.assertEqual(row['display'], ko.aanduiding)
        self.assertEqual(row['type'], 'kadaster/object')
        self.assertEqual(row['uri'], 'http://update.me/api/kadaster/object/{}/'.format(ko.aanduiding))

    def test_wkpb(self):
        b = wkpb_factories.BeperkingKadastraalObjectFactory.create()
        row = self.get_row('geo_wkpb')
        self.assertEqual(row["id"], b.id)
        self.assertIn("geometrie", row)
        self.assertEqual(row["beperkingtype_id"], b.beperking.beperkingtype.pk)
