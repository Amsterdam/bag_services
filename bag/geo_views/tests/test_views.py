from django.db import connection

from django.test import TestCase
from datasets.bag.tests import factories as bag_factories

from datasets.brk.tests import factories as brk_factories
from datasets.wkpb.tests import factories as wkpb_factories

from django.conf import settings

URL = settings.DATAPUNT_API_URL


class ViewsTest(TestCase):

    def get_row(self, view_name):
        with connection.cursor() as cursor:
            cursor.execute(
                'SELECT * FROM {} LIMIT 1'.format(
                    connection.ops.quote_name(view_name)
                )
            )
            result = cursor.fetchone()
            self.assertIsNotNone(result)

        return dict(zip([col[0] for col in cursor.description], result))

    def test_bag_ligplaats(self):
        l = bag_factories.LigplaatsFactory.create()
        bag_factories.NummeraanduidingFactory.create(
            ligplaats=l,
            type_adres="Hoofdadres",
        )
        row = self.get_row('geo_bag_ligplaats')
        self.assertEqual(row['id'], l.landelijk_id)
        self.assertIn("geometrie", row)
        self.assertEqual(
            row['display'].split()[0], l.hoofdadres.adres().split()[0])
        self.assertEqual(row['type'], 'bag/ligplaats')
        self.assertEqual(
            row['uri'],
            '{}bag/v1.1/ligplaats/{}/'.format(URL, l.landelijk_id))

    def test_bag_openbareruimte(self):

        ob = bag_factories.OpenbareRuimteFactory.create(
            naam='prinsengracht',
            type='02'
        )

        row = self.get_row('geo_bag_openbareruimte')
        self.assertIn("geometrie", row)
        self.assertEqual(row['display'], 'prinsengracht')
        self.assertEqual(row['type'], 'bag/openbareruimte')
        self.assertEqual(row['opr_type'], 'Water')
        self.assertEqual(
            row['uri'], '{}bag/v1.1/openbareruimte/{}/'.format(URL, ob.landelijk_id))

    def test_bag_standplaats(self):
        s = bag_factories.StandplaatsFactory.create()
        bag_factories.NummeraanduidingFactory.create(
            standplaats=s,
            type_adres="Hoofdadres",
        )
        row = self.get_row('geo_bag_standplaats')
        self.assertEqual(row['id'], s.landelijk_id)
        self.assertIn("geometrie", row)
        self.assertEqual(
            row["display"].split()[0], s.hoofdadres.adres().split()[0])
        self.assertEqual(row["type"], 'bag/standplaats')
        self.assertIn(
            row["uri"], '{}bag/v1.1/standplaats/{}/'.format(URL, s.landelijk_id))

    def test_bag_verblijfsobject(self):
        v = bag_factories.VerblijfsobjectFactory.create()
        bag_factories.NummeraanduidingFactory.create(
            verblijfsobject=v,
            type_adres="Hoofdadres",
        )
        row = self.get_row('geo_bag_verblijfsobject')
        self.assertEqual(row["id"], v.landelijk_id)
        self.assertIn("geometrie", row)
        self.assertEqual(
            row["display"].split()[0], v.hoofdadres.adres().split()[0])
        self.assertEqual(row['type'], 'bag/verblijfsobject')
        self.assertEqual(
            row['uri'], f'{URL}bag/v1.1/verblijfsobject/{v.landelijk_id}/')

    def test_bag_pand(self):
        p = bag_factories.PandFactory.create()
        row = self.get_row('geo_bag_pand')
        self.assertEqual(row['id'], p.landelijk_id)
        self.assertIn("geometrie", row)
        self.assertEqual(row['display'], p.landelijk_id)
        self.assertEqual(row['type'], 'bag/pand')
        self.assertIn(
            row['uri'], '{}bag/v1.1/pand/{}/'.format(URL, p.landelijk_id))

    def test_bag_bouwblok(self):
        bb = bag_factories.BouwblokFactory.create()
        row = self.get_row('geo_bag_bouwblok')
        self.assertEqual(row['id'], bb.id)
        self.assertIn("geometrie", row)
        self.assertEqual(row['code'], bb.code)
        self.assertEqual(row['display'], bb.code)
        self.assertEqual(row['type'], 'gebieden/bouwblok')
        self.assertEqual(
            row['uri'], '{}gebieden/bouwblok/{}/'.format(URL, bb.id))

    def test_bag_buurt(self):
        b = bag_factories.BuurtFactory.create()
        row = self.get_row('geo_bag_buurt')
        self.assertEqual(row['id'], b.id)
        self.assertIn("geometrie", row)
        self.assertEqual(row['code'], b.code)
        self.assertEqual(row['naam'], b.naam)
        self.assertEqual(row['display'], b.naam)
        self.assertEqual(row['type'], 'gebieden/buurt')
        self.assertEqual(
            row['uri'], '{}gebieden/buurt/{}/'.format(URL, b.id))

    def test_bag_buurtcombinatie(self):
        bc = bag_factories.BuurtcombinatieFactory.create()
        row = self.get_row('geo_bag_buurtcombinatie')
        self.assertEqual(row['id'], bc.id)
        self.assertIn("geometrie", row)
        self.assertEqual(row['vollcode'], bc.vollcode)
        self.assertEqual(row['naam'], bc.naam)
        self.assertEqual(row['display'], bc.naam)
        self.assertEqual(row['type'], 'gebieden/buurtcombinatie')
        self.assertEqual(
            row['uri'],
            '{}gebieden/buurtcombinatie/{}/'.format(URL, bc.id))

    def test_bag_gebiedsgerichtwerken(self):
        g = bag_factories.GebiedsgerichtwerkenFactory.create()
        row = self.get_row('geo_bag_gebiedsgerichtwerken')
        self.assertEqual(row['id'], g.id)
        self.assertIn("geometrie", row)
        self.assertEqual(row['code'], g.code)
        self.assertEqual(row['naam'], g.naam)
        self.assertEqual(row['display'], g.naam)
        self.assertEqual(row['type'], 'gebieden/gebiedsgerichtwerken')
        self.assertEqual(
            row['uri'],
            '{}gebieden/gebiedsgerichtwerken/{}/'.format(URL, g.id))

    def test_bag_gebiedsgerichtwerken_praktijkgebieden(self):
        g = bag_factories.GebiedsgerichtwerkenPraktijkgebiedenFactory.create()
        row = self.get_row('geo_bag_gebiedsgerichtwerkenpraktijkgebieden')
        self.assertEqual(row['id'], g.id)
        self.assertIn("geometrie", row)
        self.assertEqual(row['naam'], g.naam)
        self.assertEqual(row['display'], g.naam)
        self.assertEqual(row['type'], 'gebieden/gebiedsgerichtwerkenpraktijkgebieden')
        self.assertEqual(
            row['uri'],
            '{}gebieden/gebiedsgerichtwerkenpraktijkgebieden/{}/'.format(URL, g.id))

    def test_bag_grootstedelijkgebied(self):
        gg = bag_factories.GrootstedelijkGebiedFactory.create()
        row = self.get_row('geo_bag_grootstedelijkgebied')
        self.assertEqual(row['id'], gg.id)
        self.assertIn("geometrie", row)
        self.assertEqual(row['naam'], gg.naam)
        self.assertEqual(row['display'], gg.naam)
        self.assertEqual(row['type'], 'gebieden/grootstedelijkgebied')
        self.assertEqual(
            row['uri'],
            '{}gebieden/grootstedelijkgebied/{}/'.format(URL, gg.id))

    def test_bag_stadsdeel(self):
        s = bag_factories.StadsdeelFactory.create()
        row = self.get_row('geo_bag_stadsdeel')
        self.assertEqual(row['id'], s.id)
        self.assertIn("geometrie", row)
        self.assertEqual(row['code'], s.code)
        self.assertEqual(row['naam'], s.naam)
        self.assertEqual(row['display'], s.naam)
        self.assertEqual(row['type'], 'gebieden/stadsdeel')
        self.assertEqual(
            row['uri'], '{}gebieden/stadsdeel/{}/'.format(URL, s.id))

    def test_bag_unesco(self):
        u = bag_factories.UnescoFactory.create()
        row = self.get_row('geo_bag_unesco')
        self.assertEqual(row['id'], u.id)
        self.assertIn("geometrie", row)
        self.assertEqual(row['naam'], u.naam)
        self.assertEqual(row['display'], u.naam)
        self.assertEqual(row['type'], 'gebieden/unesco')
        self.assertEqual(
            row['uri'], '{}gebieden/unesco/{}/'.format(URL, u.id))

    def test_lki_gemeente(self):
        g = brk_factories.GemeenteFactory.create()
        row = self.get_row('geo_lki_gemeente')
        self.assertEqual(row['id'], g.gemeente)
        self.assertIn("geometrie", row)
        self.assertEqual(row['gemeentenaam'], g.gemeente)
        self.assertEqual(row['gemeentecode'], g.gemeente)

    def test_lki_kadastrale_gemeente(self):
        g = brk_factories.KadastraleGemeenteFactory.create()
        row = self.get_row('geo_lki_kadastralegemeente')
        self.assertEqual(row['id'], g.id)
        self.assertIn("geometrie", row)
        self.assertIn("geometrie_lines", row)
        self.assertEqual(row["code"], g.id)

    def test_lki_sectie(self):
        s = brk_factories.KadastraleSectieFactory.create()
        row = self.get_row('geo_lki_sectie')
        self.assertEqual(row["id"], s.id)
        self.assertEqual(row["volledige_code"], "{} {}".format(
                                                    s.kadastrale_gemeente_id,
                                                    s.sectie))
        self.assertIn("geometrie", row)
        self.assertIn("geometrie_lines", row)
        self.assertEqual(row["code"], s.sectie)

    def test_lki_kadastraal_object(self):
        ko = brk_factories.KadastraalObjectFactory.create()
        row = self.get_row('geo_lki_kadastraalobject')
        self.assertEqual(row["id"], ko.id)
        self.assertIn("geometrie", row)
        self.assertEqual(row["perceelnummer"], ko.perceelnummer)
        self.assertEqual(row["volledige_code"], ko.aanduiding)
        self.assertEqual(row['display'], ko.get_aanduiding_spaties())
        self.assertEqual(row['type'], 'kadaster/kadastraal_object')
        self.assertEqual(
            row['uri'], '{}brk/object/{}/'.format(URL, ko.id))

    def test_wkpb(self):
        b = wkpb_factories.BeperkingKadastraalObjectFactory.create()
        row = self.get_row('geo_wkpb')
        self.assertEqual(row["id"], b.id)
        self.assertIn("geometrie", row)
        self.assertEqual(row["beperkingtype_id"], b.beperking.beperkingtype.pk)
