import datetime

from django.contrib.gis.geos import Point
from django.test import TransactionTestCase

from datasets.bag.tests import factories
from .. import models, batch
from batch.test import TaskTestCase

BAG = 'diva/bag'
BAG_WKT = 'diva/bag_wkt'
GEBIEDEN = 'diva/gebieden'
GEBIEDEN_SHP = 'diva/gebieden_shp'


class ImportAvrTest(TaskTestCase):
    def task(self):
        return batch.ImportAvrTask(BAG)

    def test_import(self):
        self.run_task()

        imported = models.RedenAfvoer.objects.all()
        self.assertEqual(len(imported), 44)

        a = models.RedenAfvoer.objects.get(pk='20')
        self.assertEqual(a.omschrijving, 'Geconstateerd adres')


class ImportOvrTest(TaskTestCase):
    def task(self):
        return batch.ImportOvrTask(BAG)

    def test_import(self):
        self.run_task()

        imported = models.RedenOpvoer.objects.all()
        self.assertEqual(len(imported), 44)

        o = models.RedenOpvoer.objects.get(pk='10')
        self.assertEqual(o.omschrijving, 'Verbouw door wijziging gebruiksdoel')


class ImportBrnTest(TaskTestCase):
    def task(self):
        return batch.ImportBrnTask(BAG)

    def test_import(self):
        self.run_task()

        imported = models.Bron.objects.all()
        self.assertEqual(len(imported), 100)

        self.assertIsNotNone(models.Bron.objects.get(pk='PST'))

        b = models.Bron.objects.get(pk='13')
        self.assertEqual(b.omschrijving, 'Stadsdeel Zuideramstel (13)')


class ImportEgmTest(TaskTestCase):
    def task(self):
        return batch.ImportEgmTask(BAG)

    def test_import(self):
        self.run_task()

        imported = models.Eigendomsverhouding.objects.all()
        self.assertEqual(len(imported), 2)

        a = models.Eigendomsverhouding.objects.get(pk='01')
        self.assertEqual(a.omschrijving, 'Huur')


class ImportFngTest(TaskTestCase):
    def task(self):
        return batch.ImportFngTask(BAG)

    def test_import(self):
        self.run_task()

        imported = models.Financieringswijze.objects.all()
        self.assertEqual(len(imported), 19)

        a = models.Financieringswijze.objects.get(pk='200')
        self.assertEqual(a.omschrijving, 'Premiehuur Profit (200)')


class ImportLggTest(TaskTestCase):
    def task(self):
        return batch.ImportLggTask(BAG)

    def test_import(self):
        self.run_task()

        imported = models.Ligging.objects.all()
        self.assertEqual(len(imported), 6)

        a = models.Ligging.objects.get(pk='03')
        self.assertEqual(a.omschrijving, 'Tussengebouw')


class ImportGbkTest(TaskTestCase):
    def task(self):
        return batch.ImportGbkTask(BAG)

    def test_import(self):
        self.run_task()

        imported = models.Gebruik.objects.all()
        self.assertEqual(len(imported), 320)

        a = models.Gebruik.objects.get(pk='0006')
        self.assertEqual(a.omschrijving, 'ZZ-BEDRIJF EN WONING')


class ImportLocTest(TaskTestCase):
    def task(self):
        return batch.ImportLocTask(BAG)

    def test_import(self):
        self.run_task()

        imported = models.LocatieIngang.objects.all()
        self.assertEqual(len(imported), 5)

        a = models.LocatieIngang.objects.get(pk='04')
        self.assertEqual(a.omschrijving, 'L-zijde')


class ImportTggTest(TaskTestCase):
    def task(self):
        return batch.ImportTggTask(BAG)

    def test_import(self):
        self.run_task()

        imported = models.Toegang.objects.all()
        self.assertEqual(len(imported), 9)

        a = models.Toegang.objects.get(pk='08')
        self.assertEqual(a.omschrijving, 'Begane grond (08)')


class ImportStsTest(TaskTestCase):
    def task(self):
        return batch.ImportStsTask(BAG)

    def test_import(self):
        self.run_task()

        imported = models.Status.objects.all()
        self.assertEqual(len(imported), 43)

        self.assertIsNotNone(models.Status.objects.get(pk='10'))

        s = models.Status.objects.get(pk='01')
        self.assertEqual(s.omschrijving, 'Buitengebruik i.v.m. renovatie')


# gebieden
class ImportGmeTest(TaskTestCase):
    def task(self):
        return batch.ImportGmeTask(GEBIEDEN)

    def test_import(self):
        self.run_task()

        imported = models.Gemeente.objects.all()
        self.assertEqual(len(imported), 1)

        g = models.Gemeente.objects.get(pk='03630000000000')

        self.assertEquals(g.id, '03630000000000')
        self.assertEquals(g.code, '0363')
        self.assertEquals(g.naam, 'Amsterdam')
        self.assertTrue(g.verzorgingsgebied)
        self.assertFalse(g.vervallen)
        self.assertEquals(g.begin_geldigheid, datetime.date(1900, 1, 1))
        self.assertIsNone(g.einde_geldigheid)


class ImportSdlTest(TaskTestCase):
    def setUp(self):
        factories.GemeenteFactory.create(pk='03630000000000')

    def task(self):
        return batch.ImportSdlTask(GEBIEDEN, GEBIEDEN_SHP)

    def test_import(self):
        self.run_task()

        imported = models.Stadsdeel.objects.all()
        self.assertEqual(len(imported), 8)

        s = models.Stadsdeel.objects.get(pk='03630011872037')

        self.assertEquals(s.id, '03630011872037')
        self.assertEquals(s.code, 'F')
        self.assertEquals(s.naam, 'Nieuw-West')
        self.assertEquals(s.vervallen, False)
        self.assertEquals(s.gemeente.id, '03630000000000')
        self.assertEquals(s.begin_geldigheid, datetime.date(2015, 1, 1))
        self.assertIsNone(s.einde_geldigheid)

    def test_import_geo(self):
        self.run_task()

        s = models.Stadsdeel.objects.get(pk='03630011872037')
        self.assertIsNotNone(s.geometrie)


class ImportBrtTest(TaskTestCase):
    def setUp(self):
        factories.StadsdeelFactory.create(pk='03630000000016')
        factories.BuurtcombinatieFactory.create(code='92')

    def task(self):
        return batch.ImportBrtTask(GEBIEDEN, GEBIEDEN_SHP)

    def test_import(self):
        self.run_task()

        b = models.Buurt.objects.get(pk='03630000000487')

        self.assertEquals(b.id, '03630000000487')
        self.assertEquals(b.code, '92c')
        self.assertEquals(b.vollcode, 'T92c')
        self.assertEquals(b.naam, 'Amstel III deel C/D Noord')
        self.assertEquals(b.vervallen, False)
        self.assertEquals(b.stadsdeel.id, '03630000000016')
        self.assertIsNotNone(b.geometrie)
        self.assertEquals(b.begin_geldigheid, datetime.date(2006, 6, 12))
        self.assertIsNone(b.einde_geldigheid)
        self.assertEquals(b.buurtcombinatie.code, '92')


class ImportBbkTest(TaskTestCase):
    def setUp(self):
        factories.BuurtFactory.create(pk='03630000000537')

    def task(self):
        return batch.ImportBbkTask(GEBIEDEN, GEBIEDEN_SHP)

    def test_import(self):
        self.run_task()

        imported = models.Bouwblok.objects.all()
        self.assertEqual(len(imported), 96)

        b = models.Bouwblok.objects.get(pk='03630012100449')

        self.assertEquals(b.id, '03630012100449')
        self.assertEquals(b.code, 'DE66')
        self.assertEquals(b.buurt.id, '03630000000537')
        self.assertIsNotNone(b.geometrie)
        self.assertEquals(b.begin_geldigheid, datetime.date(2006, 6, 12))
        self.assertIsNone(b.einde_geldigheid)


# gebieden shp
class ImportBuurtcombinatieTest(TaskTestCase):
    def setUp(self):
        factories.StadsdeelFactory.create(code='E')

    def task(self):
        return batch.ImportBuurtcombinatieTask(GEBIEDEN_SHP)

    def test_import(self):
        self.run_task()

        imported = models.Buurtcombinatie.objects.all()
        self.assertEqual(len(imported), 99)

        b = models.Buurtcombinatie.objects.get(code='14')

        self.assertEquals(b.id, '3630012052018')
        self.assertEquals(b.vollcode, 'E14')
        self.assertEquals(b.stadsdeel.code, 'E')
        self.assertEquals(b.begin_geldigheid, datetime.date(2010, 5, 1))
        self.assertIsNone(b.einde_geldigheid)


class ImportGebiedsgerichtwerkenTest(TaskTestCase):
    def requires(self):
        return [
            batch.ImportGmeTask(GEBIEDEN),
            batch.ImportSdlTask(GEBIEDEN, GEBIEDEN_SHP),
        ]

    def task(self):
        return batch.ImportGebiedsgerichtwerkenTask(GEBIEDEN_SHP)

    def test_import(self):
        self.run_task()

        imported = models.Gebiedsgerichtwerken.objects.all()
        self.assertEqual(len(imported), 23)

        b = models.Gebiedsgerichtwerken.objects.get(code='DX06')

        self.assertEquals(b.stadsdeel.id, '03630011872037')


class ImportGrootstedelijkgebiedTest(TaskTestCase):
    def task(self):
        return batch.ImportGrootstedelijkgebiedTask(GEBIEDEN_SHP)

    def test_import(self):
        self.run_task()

        imported = models.Grootstedelijkgebied.objects.all()
        self.assertEqual(len(imported), 15)

        b = models.Grootstedelijkgebied.objects.get(naam='Overamstel')

        self.assertIsInstance(b, models.Grootstedelijkgebied)


class ImportUnescoTest(TaskTestCase):
    def task(self):
        return batch.ImportUnescoTask(GEBIEDEN_SHP)

    def test_import(self):
        self.run_task()

        imported = models.Unesco.objects.all()
        self.assertEqual(len(imported), 2)

        b = models.Unesco.objects.get(naam='Kernzone')

        self.assertIsInstance(b, models.Unesco)


# bag
class ImportLigTest(TaskTestCase):

    def setUp(self):
        factories.StatusFactory.create(code='33')
        factories.BuurtFactory.create(pk='03630000000491')

    def task(self):
        return batch.ImportLigTask(BAG, BAG_WKT)

    def test_import(self):
        self.run_task()

        imported = models.Ligplaats.objects.all()
        self.assertEqual(len(imported), 60)

        l = models.Ligplaats.objects.get(pk='03630001028467')
        self.assertEquals(l.landelijk_id, '0363020001028467')
        self.assertEquals(l.vervallen, False)
        self.assertIsNone(l.bron)
        self.assertEquals(l.status.code, '33')
        self.assertEquals(l.buurt.id, '03630000000491')
        self.assertEquals(l.document_mutatie, datetime.date(2010, 9, 9))
        self.assertEquals(l.document_nummer, 'GV00000407')
        self.assertEquals(l.begin_geldigheid, datetime.date(2010, 9, 9))
        self.assertIsNone(l.einde_geldigheid)
        self.assertEquals(l.mutatie_gebruiker, 'DBI')

    def test_import_geo(self):
        self.run_task()

        imported = models.Ligplaats.objects.exclude(geometrie__isnull=True)
        self.assertEqual(len(imported), 60)

        l = models.Ligplaats.objects.get(pk='03630001024868')
        self.assertIsNotNone(l.geometrie)


class ImportWplTest(TaskTestCase):
    def requires(self):
        return [
            batch.ImportGmeTask(GEBIEDEN),
        ]

    def task(self):
        return batch.ImportWplTask(BAG)

    def test_import(self):
        self.run_task()

        imported = models.Woonplaats.objects.all()
        self.assertEqual(len(imported), 1)

        w = models.Woonplaats.objects.get(pk='03630022796658')
        self.assertEquals(w.id, '03630022796658')
        self.assertEquals(w.landelijk_id, '3594')
        self.assertEquals(w.naam, 'Amsterdam')
        self.assertEquals(w.document_mutatie, datetime.date(2014, 1, 10))
        self.assertEquals(w.document_nummer, 'GV00001729_AC00AC')
        self.assertEquals(w.naam_ptt, 'AMSTERDAM')
        self.assertEquals(w.vervallen, False)
        self.assertEquals(w.gemeente.id, '03630000000000')
        self.assertEquals(w.begin_geldigheid, datetime.date(2014, 1, 10))
        self.assertIsNone(w.einde_geldigheid)
        self.assertEquals(w.mutatie_gebruiker, 'DBI')


class ImportOprTest(TaskTestCase):
    def setUp(self):
        factories.StatusFactory.create(code='35')
        factories.WoonplaatsFactory.create(id='03630022796658')

    def task(self):
        return batch.ImportOprTask(BAG, BAG_WKT)

    def test_import(self):
        self.run_task()

        o = models.OpenbareRuimte.objects.get(pk='03630000002701')
        self.assertEquals(o.id, '03630000002701')
        self.assertEquals(o.landelijk_id, '0363300000002701')
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
        self.assertEquals(o.begin_geldigheid, datetime.date(2014, 1, 10))
        self.assertEquals(o.einde_geldigheid, None)
        self.assertEquals(o.mutatie_gebruiker, 'DBI')
        self.assertIsNotNone(o.geometrie)


class ImportStaTest(TaskTestCase):
    def requires(self):
        return [
            batch.ImportStsTask(BAG),
        ]

    def task(self):
        return batch.ImportStaTask(BAG, BAG_WKT)

    def test_import(self):
        self.run_task()

        imported = models.Standplaats.objects.all()
        self.assertEqual(len(imported), 50)

        l = models.Standplaats.objects.get(pk='03630001002936')
        self.assertEquals(l.landelijk_id, '0363030001002936')
        self.assertEquals(l.vervallen, False)
        self.assertIsNone(l.bron)
        self.assertEquals(l.status.code, '37')
        self.assertIsNone(l.buurt)
        self.assertEquals(l.document_mutatie, datetime.date(2010, 9, 9))
        self.assertEquals(l.document_nummer, 'GV00000407')
        self.assertEquals(l.begin_geldigheid, datetime.date(2010, 9, 9))
        self.assertIsNone(l.einde_geldigheid)
        self.assertEquals(l.mutatie_gebruiker, 'DBI')

    def test_import_geo(self):
        self.run_task()

        imported = models.Standplaats.objects.exclude(geometrie__isnull=True)
        self.assertEqual(len(imported), 50)

        l = models.Standplaats.objects.get(pk='03630001002936')
        self.assertIsNotNone(l.geometrie)


class ImportVboTest(TaskTestCase):
    def setUp(self):
        factories.EigendomsverhoudingFactory.create(code='02')
        factories.FinancieringswijzeFactory.create(code='274')
        factories.GebruikFactory.create(code='1800')
        factories.LiggingFactory.create(code='03')
        factories.StatusFactory.create(code='21')

    def task(self):
        return batch.ImportVboTask(BAG)

    def test_import(self):
        self.run_task()

        v = models.Verblijfsobject.objects.get(pk='03630000648915')
        self.assertEqual(v.landelijk_id, '0363010000648915')
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
        self.assertIsNone(v.reden_opvoer)
        self.assertIsNone(v.bron)
        self.assertEqual(v.eigendomsverhouding.code, '02')
        self.assertEqual(v.financieringswijze.code, '274')
        self.assertEqual(v.gebruik.code, '1800')
        self.assertIsNone(v.locatie_ingang)
        self.assertEqual(v.ligging.code, '03')
        self.assertEqual(v.status.code, '21')
        self.assertIsNone(v.buurt)
        self.assertEqual(v.begin_geldigheid, datetime.date(2010, 9, 9))
        self.assertIsNone(v.einde_geldigheid)
        self.assertEqual(v.verhuurbare_eenheden, None)
        self.assertEqual(v.mutatie_gebruiker, 'DBI')


class ImportNumTest(TaskTestCase):
    def setUp(self):
        factories.OpenbareRuimteFactory.create(pk='03630000003910')
        factories.LigplaatsFactory.create(pk='03630001025513')
        factories.StatusFactory.create(code='16')

    def task(self):
        return batch.ImportNumTask(BAG)

    def test_import(self):
        self.run_task()

        n = models.Nummeraanduiding.objects.get(pk='03630000512845')
        self.assertEquals(n.id, '03630000512845')
        self.assertEquals(n.landelijk_id, '0363200000512845')
        self.assertEquals(n.huisnummer, 26)
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
        self.assertEquals(n.begin_geldigheid, datetime.date(2005, 5, 25))
        self.assertIsNone(n.einde_geldigheid)
        self.assertEquals(n.mutatie_gebruiker, 'DBI')

    def test_num_lig_hfd_import(self):
        factories.OpenbareRuimteFactory.create(pk='03630000003404')
        factories.LigplaatsFactory.create(pk='03630001035885')

        self.run_task()

        n = models.Nummeraanduiding.objects.get(pk='03630000520671')
        l = models.Ligplaats.objects.get(pk='03630001035885')

        self.assertEquals(n.ligplaats.id, l.id)
        self.assertEquals(l.hoofdadres.id, n.id)
        self.assertIn(n.id, [a.id for a in l.adressen.all()])

    def test_num_sta_hfd_import(self):
        factories.OpenbareRuimteFactory.create(pk='03630000001094')
        factories.StandplaatsFactory.create(pk='03630000717733')

        self.run_task()

        n = models.Nummeraanduiding.objects.get(pk='03630000398621')
        s = models.Standplaats.objects.get(pk='03630000717733')

        self.assertEquals(n.standplaats.id, s.id)
        self.assertEquals(s.hoofdadres.id, n.id)
        self.assertIn(n.id, [a.id for a in s.adressen.all()])

    def test_num_vbo_hfd_import(self):
        factories.OpenbareRuimteFactory.create(pk='03630000004150')
        factories.VerblijfsobjectFactory.create(pk='03630000721053')

        self.run_task()

        n = models.Nummeraanduiding.objects.get(pk='03630000181936')
        v = models.Verblijfsobject.objects.get(pk='03630000721053')

        self.assertEquals(n.verblijfsobject.id, v.id)
        self.assertEquals(v.hoofdadres.id, n.id)
        self.assertIn(n.id, [n.id for n in v.adressen.all()])

    def test_num_vbo_nvn_import(self):
        factories.OpenbareRuimteFactory.create(pk='03630000003699')
        factories.OpenbareRuimteFactory.create(pk='03630000003293')
        factories.VerblijfsobjectFactory.create(pk='03630000643306')

        self.run_task()

        v = models.Verblijfsobject.objects.get(pk='03630000643306')
        n1 = models.Nummeraanduiding.objects.get(pk='03630000087815')
        n2 = models.Nummeraanduiding.objects.get(pk='03630000105581')

        self.assertIn(n1.id, [n.id for n in v.adressen.all()])
        self.assertIn(n2.id, [n.id for n in v.adressen.all()])
        self.assertEquals(n1.verblijfsobject.id, v.id)
        self.assertEquals(n2.verblijfsobject.id, v.id)


class ImportPndTest(TaskTestCase):

    def setUp(self):
        factories.StatusFactory.create(pk='31')
        factories.BouwblokFactory.create(pk='03630012102404')

    def task(self):
        return batch.ImportPndTask(BAG, BAG_WKT)

    def test_import(self):
        self.run_task()

        imported = models.Pand.objects.all()
        self.assertEquals(len(imported), 79)

        p = models.Pand.objects.get(pk='03630013002931')
        self.assertEqual(p.landelijk_id, '0363100012073178')
        self.assertEqual(p.document_mutatie, datetime.date(2010, 9, 9))
        self.assertEqual(p.document_nummer, 'GV00000406')
        self.assertEqual(p.bouwjaar, 1993)
        self.assertIsNone(p.laagste_bouwlaag)
        self.assertIsNone(p.hoogste_bouwlaag)
        self.assertEqual(p.pandnummer, '')
        self.assertEqual(p.vervallen, False)
        self.assertEqual(p.status.code, '31')
        self.assertEqual(p.begin_geldigheid, datetime.date(2010, 9, 9))
        self.assertIsNone(p.einde_geldigheid)
        self.assertEqual(p.mutatie_gebruiker, 'DBI')
        self.assertIsNone(p.bouwblok)

        p = models.Pand.objects.get(pk='03630012977654')
        self.assertEquals(p.bouwblok.id, '03630012102404')

    def test_import_geo(self):
        self.run_task()

        imported = models.Pand.objects.exclude(geometrie__isnull=True)
        self.assertEquals(len(imported), 79)


class ImportVboPndTask(TaskTestCase):
    def requires(self):
        return [
            batch.ImportStsTask(BAG),
            batch.ImportVboTask(BAG),
            batch.ImportPndTask(BAG, BAG_WKT),
        ]

    def task(self):
        return batch.ImportPndVboTask(BAG)
    
    def test_import(self):
        self.run_task()

        imported = models.VerblijfsobjectPandRelatie.objects.all()
        self.assertEquals(len(imported), 96)

        p = models.Pand.objects.get(pk='03630013113460')
        v1 = models.Verblijfsobject.objects.get(pk='03630000716108')
        v2 = models.Verblijfsobject.objects.get(pk='03630000716112')
        v3 = models.Verblijfsobject.objects.get(pk='03630000716086')

        self.assertCountEqual([v.id for v in p.verblijfsobjecten.all()], [v1.id, v2.id, v3.id])
        self.assertEqual([p.id for p in v1.panden.all()], [p.id])


