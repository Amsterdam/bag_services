import datetime

from django.contrib.gis.geos import Point
from django.test import TestCase

from bag import models, batch

BAG = 'diva/bag'
BAG_WKT = 'diva/bag_wkt'
GEBIEDEN = 'diva/gebieden'


class ImportAvrTest(TestCase):
    def test_import(self):
        task = batch.ImportAvrTask(BAG)
        task.execute()

        batch.FlushCacheTask().execute()

        imported = models.RedenAfvoer.objects.all()
        self.assertEqual(len(imported), 44)

        a = models.RedenAfvoer.objects.get(pk='20')
        self.assertEqual(a.omschrijving, 'Geconstateerd adres')


class ImportBrnTest(TestCase):
    def test_import(self):
        task = batch.ImportBrnTask(BAG)
        task.execute()

        batch.FlushCacheTask().execute()

        imported = models.Bron.objects.all()
        self.assertEqual(len(imported), 100)

        self.assertIsNotNone(models.Bron.objects.get(pk='PST'))

        b = models.Bron.objects.get(pk='13')
        self.assertEqual(b.omschrijving, 'Stadsdeel Zuideramstel (13)')


class ImportEgmTest(TestCase):
    def test_import(self):
        task = batch.ImportEgmTask(BAG)
        task.execute()

        batch.FlushCacheTask().execute()

        imported = models.Eigendomsverhouding.objects.all()
        self.assertEqual(len(imported), 2)

        a = models.Eigendomsverhouding.objects.get(pk='01')
        self.assertEqual(a.omschrijving, 'Huur')


class ImportFngTest(TestCase):
    def test_import(self):
        task = batch.ImportFngTask(BAG)
        task.execute()

        batch.FlushCacheTask().execute()

        imported = models.Financieringswijze.objects.all()
        self.assertEqual(len(imported), 19)

        a = models.Financieringswijze.objects.get(pk='200')
        self.assertEqual(a.omschrijving, 'Premiehuur Profit (200)')


class ImportLggTest(TestCase):
    def test_import(self):
        task = batch.ImportLggTask(BAG)
        task.execute()

        batch.FlushCacheTask().execute()

        imported = models.Ligging.objects.all()
        self.assertEqual(len(imported), 6)

        a = models.Ligging.objects.get(pk='03')
        self.assertEqual(a.omschrijving, 'Tussengebouw')


class ImportGbkTest(TestCase):
    def test_import(self):
        task = batch.ImportGbkTask(BAG)
        task.execute()

        batch.FlushCacheTask().execute()

        imported = models.Gebruik.objects.all()
        self.assertEqual(len(imported), 320)

        a = models.Gebruik.objects.get(pk='0006')
        self.assertEqual(a.omschrijving, 'ZZ-BEDRIJF EN WONING')


class ImportLocTest(TestCase):
    def test_import(self):
        task = batch.ImportLocTask(BAG)
        task.execute()

        batch.FlushCacheTask().execute()

        imported = models.LocatieIngang.objects.all()
        self.assertEqual(len(imported), 5)

        a = models.LocatieIngang.objects.get(pk='04')
        self.assertEqual(a.omschrijving, 'L-zijde')


class ImportTggTest(TestCase):
    def test_import(self):
        task = batch.ImportTggTask(BAG)
        task.execute()

        batch.FlushCacheTask().execute()

        imported = models.Toegang.objects.all()
        self.assertEqual(len(imported), 9)

        a = models.Toegang.objects.get(pk='08')
        self.assertEqual(a.omschrijving, 'Begane grond (08)')


class ImportStsTest(TestCase):
    def test_import(self):
        task = batch.ImportStsTask(BAG)
        task.execute()

        batch.FlushCacheTask().execute()

        imported = models.Status.objects.all()
        self.assertEqual(len(imported), 43)

        self.assertIsNotNone(models.Status.objects.get(pk='10'))

        s = models.Status.objects.get(pk='01')
        self.assertEqual(s.omschrijving, 'Buitengebruik i.v.m. renovatie')


class ImportGmeTest(TestCase):
    def test_import(self):
        task = batch.ImportGmeTask(GEBIEDEN)
        task.execute()

        batch.FlushCacheTask().execute()

        imported = models.Gemeente.objects.all()
        self.assertEqual(len(imported), 1)

        g = models.Gemeente.objects.get(pk='03630000000000')

        self.assertEquals(g.id, '03630000000000')
        self.assertEquals(g.code, '0363')
        self.assertEquals(g.naam, 'Amsterdam')
        self.assertTrue(g.verzorgingsgebied)
        self.assertFalse(g.vervallen)


class ImportSdlTest(TestCase):
    def test_import(self):
        batch.ImportGmeTask(GEBIEDEN).execute()

        task = batch.ImportSdlTask(GEBIEDEN)
        task.execute()

        batch.FlushCacheTask().execute()

        imported = models.Stadsdeel.objects.all()
        self.assertEqual(len(imported), 8)

        s = models.Stadsdeel.objects.get(pk='03630011872037')

        self.assertEquals(s.id, '03630011872037')
        self.assertEquals(s.code, 'F')
        self.assertEquals(s.naam, 'Nieuw-West')
        self.assertEquals(s.vervallen, False)
        self.assertEquals(s.gemeente.id, '03630000000000')


class ImportBrtTest(TestCase):
    def test_import(self):
        batch.ImportGmeTask(GEBIEDEN).execute()
        batch.ImportSdlTask(GEBIEDEN).execute()

        task = batch.ImportBrtTask(GEBIEDEN)
        task.execute()

        batch.FlushCacheTask().execute()

        imported = models.Buurt.objects.all()
        self.assertEqual(len(imported), 481)

        b = models.Buurt.objects.get(pk='03630000000796')

        self.assertEquals(b.id, '03630000000796')
        self.assertEquals(b.code, '44b')
        self.assertEquals(b.naam, 'Westlandgrachtbuurt')
        self.assertEquals(b.vervallen, False)
        self.assertEquals(b.stadsdeel.id, '03630011872038')


class ImportLigTest(TestCase):
    def test_import(self):
        batch.ImportBrnTask(BAG).execute()
        batch.ImportStsTask(BAG).execute()

        batch.ImportGmeTask(GEBIEDEN).execute()
        batch.ImportSdlTask(GEBIEDEN).execute()
        batch.ImportBrtTask(GEBIEDEN).execute()

        task = batch.ImportLigTask(BAG)
        task.execute()

        batch.FlushCacheTask().execute()

        imported = models.Ligplaats.objects.all()
        self.assertEqual(len(imported), 60)

        l = models.Ligplaats.objects.get(pk='03630001024868')
        self.assertEquals(l.identificatie, '03630001024868')
        self.assertEquals(l.vervallen, False)
        self.assertIsNone(l.bron)
        self.assertEquals(l.status.code, '33')
        self.assertEquals(l.buurt.id, '03630000000100')
        self.assertEquals(l.document_mutatie, datetime.date(2010, 9, 9))
        self.assertEquals(l.document_nummer, 'GV00000407')


class ImportLigGeoTest(TestCase):
    def test_import(self):
        batch.ImportStsTask(BAG).execute()
        batch.ImportLigTask(BAG).execute()

        task = batch.ImportLigGeoTask(BAG_WKT)
        task.execute()

        batch.FlushCacheTask().execute()

        imported = models.Ligplaats.objects.exclude(geometrie__isnull=True)
        self.assertEqual(len(imported), 60)

        l = models.Ligplaats.objects.get(pk='03630001024868')
        self.assertIsNotNone(l.geometrie)


class ImportWplTest(TestCase):
    def test_import(self):
        batch.ImportGmeTask(GEBIEDEN).execute()

        task = batch.ImportWplTask(BAG)
        task.execute()

        batch.FlushCacheTask().execute()

        imported = models.Woonplaats.objects.all()
        self.assertEqual(len(imported), 1)

        w = models.Woonplaats.objects.get(pk='03630022796658')
        self.assertEquals(w.id, '03630022796658')
        self.assertEquals(w.code, '3594')
        self.assertEquals(w.naam, 'Amsterdam')
        self.assertEquals(w.document_mutatie, datetime.date(2014, 1, 10))
        self.assertEquals(w.document_nummer, 'GV00001729_AC00AC')
        self.assertEquals(w.naam_ptt, 'AMSTERDAM')
        self.assertEquals(w.vervallen, False)
        self.assertEquals(w.gemeente.id, '03630000000000')


class ImportOprTest(TestCase):
    def test_import(self):
        batch.ImportBrnTask(BAG).execute()
        batch.ImportStsTask(BAG).execute()
        batch.ImportGmeTask(GEBIEDEN).execute()
        batch.ImportWplTask(BAG).execute()

        task = batch.ImportOprTask(BAG)
        task.execute()

        batch.FlushCacheTask().execute()

        imported = models.OpenbareRuimte.objects.all()
        self.assertEqual(len(imported), 97)

        o = models.OpenbareRuimte.objects.get(pk='03630000002701')
        self.assertEquals(o.id, '03630000002701')
        self.assertEquals(o.type, models.OpenbareRuimte.TYPE_WEG)
        self.assertEquals(o.naam, 'Amstel')
        self.assertEquals(o.code, '02186')
        self.assertEquals(o.document_mutatie, datetime.date(2014, 1, 10))
        self.assertEquals(o.document_nummer, 'GV00001729_AC00AC')
        self.assertEquals(o.straat_nummer, '')
        self.assertEquals(o.naam_nen, 'Amstel')
        self.assertEquals(o.naam_ptt, 'AMSTEL')
        self.assertEquals(o.vervallen, False)
        self.assertIsNone(o.bron)
        self.assertEquals(o.status.code, '35')
        self.assertEquals(o.woonplaats.id, '03630022796658')


class ImportNumTest(TestCase):
    def test_import(self):
        batch.ImportStsTask(BAG).execute()
        batch.ImportGmeTask(GEBIEDEN).execute()
        batch.ImportWplTask(BAG).execute()
        batch.ImportOprTask(BAG).execute()

        task = batch.ImportNumTask(BAG)
        task.execute()

        batch.FlushCacheTask().execute()

        imported = models.Nummeraanduiding.objects.all()
        self.assertEqual(len(imported), 207)

        n = models.Nummeraanduiding.objects.get(pk='03630000512845')
        self.assertEquals(n.id, '03630000512845')
        self.assertEquals(n.huisnummer, '26')
        self.assertEquals(n.huisletter, 'G')
        self.assertEquals(n.huisnummer_toevoeging, '')
        self.assertEquals(n.postcode, '1018DS')
        self.assertEquals(n.document_mutatie, datetime.date(2005, 5, 25))
        self.assertEquals(n.document_nummer, 'GV00000403')
        self.assertEquals(n.type, models.Nummeraanduiding.OBJECT_TYPE_LIGPLAATS)
        self.assertEquals(n.vervallen, False)
        self.assertIsNone(n.bron)
        self.assertEquals(n.status.code, '16')
        self.assertEquals(n.openbare_ruimte.id, '03630000003910')


class ImportNumLigHfdTest(TestCase):
    def test_import(self):
        batch.ImportStsTask(BAG).execute()
        batch.ImportGmeTask(GEBIEDEN).execute()
        batch.ImportWplTask(BAG).execute()
        batch.ImportOprTask(BAG).execute()
        batch.ImportNumTask(BAG).execute()
        batch.ImportLigTask(BAG).execute()

        task = batch.ImportNumLigHfdTask(BAG)
        task.execute()

        batch.FlushCacheTask().execute()

        n = models.Nummeraanduiding.objects.get(pk='03630000520671')
        l = models.Ligplaats.objects.get(pk='03630001035885')

        self.assertEquals(n.ligplaats.id, l.id)
        self.assertEquals(l.hoofdadres.id, n.id)
        self.assertIn(n.id, [a.id for a in l.adressen.all()])


class ImportStaTest(TestCase):
    def test_import(self):
        batch.ImportStsTask(BAG).execute()

        task = batch.ImportStaTask(BAG)
        task.execute()

        batch.FlushCacheTask().execute()

        imported = models.Standplaats.objects.all()
        self.assertEqual(len(imported), 51)

        l = models.Standplaats.objects.get(pk='03630001002936')
        self.assertEquals(l.identificatie, '03630001002936')
        self.assertEquals(l.vervallen, False)
        self.assertIsNone(l.bron)
        self.assertEquals(l.status.code, '37')
        self.assertIsNone(l.buurt)
        self.assertEquals(l.document_mutatie, datetime.date(2010, 9, 9))
        self.assertEquals(l.document_nummer, 'GV00000407')


class ImportStaGeoTest(TestCase):
    def test_import(self):
        batch.ImportStsTask(BAG).execute()
        batch.ImportStaTask(BAG).execute()

        task = batch.ImportStaGeoTask(BAG_WKT)
        task.execute()

        batch.FlushCacheTask().execute()

        imported = models.Standplaats.objects.exclude(geometrie__isnull=True)
        self.assertEqual(len(imported), 51)

        l = models.Standplaats.objects.get(pk='03630001002936')
        self.assertIsNotNone(l.geometrie)


class ImportNumStaHfdTest(TestCase):
    def test_import(self):
        batch.ImportStsTask(BAG).execute()
        batch.ImportGmeTask(GEBIEDEN).execute()
        batch.ImportWplTask(BAG).execute()
        batch.ImportOprTask(BAG).execute()
        batch.ImportNumTask(BAG).execute()
        batch.ImportStaTask(BAG).execute()

        task = batch.ImportNumStaHfdTask(BAG)
        task.execute()

        batch.FlushCacheTask().execute()

        n = models.Nummeraanduiding.objects.get(pk='03630000398621')
        s = models.Standplaats.objects.get(pk='03630000717733')

        self.assertEquals(n.standplaats.id, s.id)
        self.assertEquals(s.hoofdadres.id, n.id)
        self.assertIn(n.id, [a.id for a in s.adressen.all()])


class ImportVboTest(TestCase):
    def test_import(self):
        batch.ImportEgmTask(BAG).execute()
        batch.ImportFngTask(BAG).execute()
        batch.ImportGbkTask(BAG).execute()
        batch.ImportLocTask(BAG).execute()
        batch.ImportStsTask(BAG).execute()
        batch.ImportLggTask(BAG).execute()
        batch.ImportTggTask(BAG).execute()

        task = batch.ImportVboTask(BAG)
        task.execute()

        batch.FlushCacheTask().execute()

        imported = models.Verblijfsobject.objects.all()
        self.assertEqual(len(imported), 96)

        v = models.Verblijfsobject.objects.get(pk='03630000648915')
        self.assertEqual(v.geometrie, Point(121466, 493032))
        self.assertEqual(v.gebruiksdoel_code, '1010')
        self.assertEqual(v.gebruiksdoel_omschrijving, 'BEST-woning')
        self.assertEqual(v.oppervlakte, 95)
        self.assertEqual(v.document_mutatie, datetime.date(2010, 9, 9))
        self.assertEqual(v.document_nummer, 'GV00000406')
        self.assertEqual(v.bouwlaag_toegang, 0)
        self.assertEqual(v.status_coordinaat_code, 'DEF')
        self.assertEqual(v.status_coordinaat_omschrijving, 'Definitief punt')
        self.assertEqual(v.bouwlagen, 3)
        self.assertEqual(v.type_woonobject_code, 'E')
        self.assertEqual(v.type_woonobject_omschrijving, 'Eengezinswoning')
        self.assertEqual(v.woningvoorraad, True)
        self.assertEqual(v.aantal_kamers, 4)
        self.assertEqual(v.vervallen, False)
        self.assertIsNone(v.reden_afvoer)
        self.assertIsNone(v.bron)
        self.assertEqual(v.eigendomsverhouding.code, '02')
        self.assertEqual(v.financieringswijze.code, '274')
        self.assertEqual(v.gebruik.code, '1800')
        self.assertIsNone(v.locatie_ingang)
        self.assertEqual(v.ligging.code, '03')
        # todo: monument
        # todo: toegang
        # todo: opvoer
        self.assertEqual(v.status.code, '21')
        self.assertIsNone(v.buurt)


class ImportNumVboHfdTest(TestCase):
    def test_import(self):
        batch.ImportStsTask(BAG).execute()
        batch.ImportGmeTask(GEBIEDEN).execute()
        batch.ImportWplTask(BAG).execute()
        batch.ImportOprTask(BAG).execute()
        batch.ImportNumTask(BAG).execute()
        batch.ImportVboTask(BAG).execute()

        task = batch.ImportNumVboHfdTask(BAG)
        task.execute()

        batch.FlushCacheTask().execute()

        n = models.Nummeraanduiding.objects.get(pk='03630000181936')
        v = models.Verblijfsobject.objects.get(pk='03630000721053')

        self.assertEquals(n.verblijfsobject.id, v.id)
        self.assertEquals(v.hoofdadres.id, n.id)
        self.assertIn(n.id, [n.id for n in v.adressen.all()])


class ImportNumVboNvnTest(TestCase):
    def test_import(self):
        batch.ImportStsTask(BAG).execute()
        batch.ImportGmeTask(GEBIEDEN).execute()
        batch.ImportWplTask(BAG).execute()
        batch.ImportOprTask(BAG).execute()
        batch.ImportNumTask(BAG).execute()
        batch.ImportVboTask(BAG).execute()

        task = batch.ImportNumVboNvnTask(BAG)
        task.execute()

        batch.FlushCacheTask().execute()

        v = models.Verblijfsobject.objects.get(pk='03630000643306')
        n1 = models.Nummeraanduiding.objects.get(pk='03630000087815')
        n2 = models.Nummeraanduiding.objects.get(pk='03630000105581')

        self.assertIn(n1.id, [n.id for n in v.adressen.all()])
        self.assertIn(n2.id, [n.id for n in v.adressen.all()])
        self.assertEquals(n1.verblijfsobject.id, v.id)
        self.assertEquals(n2.verblijfsobject.id, v.id)


class ImportPndTest(TestCase):
    def test_import(self):
        batch.ImportStsTask(BAG).execute()

        task = batch.ImportPndTask(BAG)
        task.execute()

        batch.FlushCacheTask().execute()

        imported = models.Pand.objects.all()
        self.assertEquals(len(imported), 79)

        p = models.Pand.objects.get(pk='03630013002931')
        self.assertEqual(p.identificatie, '03630013002931')
        self.assertEqual(p.document_mutatie, datetime.date(2010, 9, 9))
        self.assertEqual(p.document_nummer, 'GV00000406')
        self.assertEqual(p.bouwjaar, 1993)
        self.assertIsNone(p.laagste_bouwlaag)
        self.assertIsNone(p.hoogste_bouwlaag)
        self.assertEqual(p.pandnummer, '')
        self.assertEqual(p.vervallen, False)
        self.assertEqual(p.status.code, '31')


class ImportPndWktTest(TestCase):
    def test_import(self):
        batch.ImportStsTask(BAG).execute()
        batch.ImportPndTask(BAG).execute()

        task = batch.ImportPndGeoTask(BAG_WKT)
        task.execute()

        batch.FlushCacheTask().execute()

        imported = models.Pand.objects.exclude(geometrie__isnull=True)
        self.assertEquals(len(imported), 79)


class ImportVboPndTask(TestCase):
    def test_import(self):
        batch.ImportStsTask(BAG).execute()
        batch.ImportVboTask(BAG).execute()
        batch.ImportPndTask(BAG).execute()

        task = batch.ImportPndVboTask(BAG)
        task.execute()

        batch.FlushCacheTask().execute()

        imported = models.VerblijfsobjectPandRelatie.objects.all()
        self.assertEquals(len(imported), 96)

        p = models.Pand.objects.get(pk='03630013113460')
        v1 = models.Verblijfsobject.objects.get(pk='03630000716108')
        v2 = models.Verblijfsobject.objects.get(pk='03630000716112')
        v3 = models.Verblijfsobject.objects.get(pk='03630000716086')

        self.assertCountEqual([v.id for v in p.verblijfsobjecten.all()], [v1.id, v2.id, v3.id])
        self.assertEqual([p.id for p in v1.panden.all()], [p.id])
