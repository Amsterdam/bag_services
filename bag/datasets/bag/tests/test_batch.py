import datetime
import logging

from django.contrib.gis.geos import Point

from datasets.bag.tests import factories
from .. import models, batch

from batch.test import TaskTestCase

BAG = 'diva/bag'
BAG_WKT = 'diva/bag_wkt'
OPR_BESCHRIJVING = 'diva/bag_openbareruimte_beschrijving'
GEBIEDEN = 'diva/gebieden'
GEBIEDEN_SHP = 'diva/gebieden_shp'


log = logging.getLogger(__name__)


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


class ImportBronTest(TaskTestCase):
    def task(self):
        return batch.ImportBronTask(BAG)

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
        return batch.ImportStatusTask(BAG)

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

        self.assertEqual(g.id, '03630000000000')
        self.assertEqual(g.code, '0363')
        self.assertEqual(g.naam, 'Amsterdam')
        self.assertTrue(g.verzorgingsgebied)
        self.assertFalse(g.vervallen)
        self.assertEqual(g.begin_geldigheid, datetime.date(1900, 1, 1))
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

        self.assertEqual(s.id, '03630011872037')
        self.assertEqual(s.code, 'F')
        self.assertEqual(s.naam, 'Nieuw-West')
        self.assertEqual(s.vervallen, False)
        self.assertEqual(s.gemeente.id, '03630000000000')
        self.assertEqual(s.begin_geldigheid, datetime.date(2015, 1, 1))
        self.assertIsNone(s.einde_geldigheid)

    def test_import_geo(self):
        self.run_task()

        s = models.Stadsdeel.objects.get(pk='03630011872037')
        self.assertIsNotNone(s.geometrie)


class ImportBuurtTest(TaskTestCase):
    def setUp(self):
        factories.StadsdeelFactory.create(pk='03630000000016')
        factories.BuurtcombinatieFactory.create(code='92')

    def task(self):
        return batch.ImportBuurtTask(GEBIEDEN, GEBIEDEN_SHP)

    def test_import(self):
        self.run_task()

        b = models.Buurt.objects.get(pk='03630000000487')

        self.assertEqual(b.id, '03630000000487')
        self.assertEqual(b.code, '92c')
        self.assertEqual(b.vollcode, 'T92c')
        self.assertEqual(b.naam, 'Amstel III deel C/D Noord')
        self.assertEqual(b.vervallen, False)
        self.assertEqual(b.stadsdeel.id, '03630000000016')
        self.assertIsNotNone(b.geometrie)
        self.assertEqual(b.begin_geldigheid, datetime.date(2015, 10, 1))
        self.assertIsNone(b.einde_geldigheid)
        self.assertEqual(b.buurtcombinatie.code, '92')


class ImportBouwblokTest(TaskTestCase):

    def requires(self):
        return [
            batch.ImportGmeTask(GEBIEDEN),
            batch.ImportSdlTask(GEBIEDEN, GEBIEDEN_SHP),
            batch.ImportWijkTask(GEBIEDEN_SHP),
            batch.ImportBuurtTask(GEBIEDEN, GEBIEDEN_SHP),
        ]

    def task(self):
        return batch.ImportBouwblokTask(GEBIEDEN, GEBIEDEN_SHP)

    def test_import(self):
        self.run_task()

        imported = models.Bouwblok.objects.all()
        self.assertEqual(len(imported), 99)

        b = models.Bouwblok.objects.get(pk='03630012100449')

        self.assertEqual(b.id, '03630012100449')
        self.assertEqual(b.code, 'DE66')
        self.assertEqual(b.buurt.id, '03630000000537')
        self.assertIsNotNone(b.geometrie)
        self.assertEqual(b.begin_geldigheid, datetime.date(2006, 6, 12))
        self.assertIsNone(b.einde_geldigheid)

        b9 = models.Bouwblok.objects.get(pk='03630012101999')
        b8 = models.Bouwblok.objects.get(pk='03630012101888')
        b7 = models.Bouwblok.objects.get(pk='03630012101777')

        # test the auto fixing of buurten
        self.assertEqual(b9.buurt.code, '92a')
        self.assertEqual(b8.buurt.code, '92c')
        self.assertEqual(b7.buurt.code, '93f')


# gebieden shp
class ImportBuurtcombinatieTest(TaskTestCase):
    def setUp(self):
        factories.StadsdeelFactory.create(code='E')

    def task(self):
        return batch.ImportWijkTask(GEBIEDEN_SHP)

    def test_import(self):
        self.run_task()

        imported = models.Buurtcombinatie.objects.all()
        self.assertEqual(len(imported), 99)

        b = models.Buurtcombinatie.objects.get(code='14')

        self.assertEqual(b.id, '3630012052018')
        self.assertEqual(b.vollcode, 'E14')
        self.assertEqual(b.stadsdeel.code, 'E')
        self.assertEqual(b.begin_geldigheid, datetime.date(2010, 5, 1))
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

        self.assertEqual(b.stadsdeel.id, '03630011872037')


class ImportGebiedsgerichtwerkenPraktijkgebiedenTest(TaskTestCase):
    def requires(self):
        return []

    def task(self):
        return batch.ImportGebiedsgerichtwerkenPraktijkgebiedenTask(GEBIEDEN_SHP)

    def test_import(self):
        self.run_task()

        imported = models.GebiedsgerichtwerkenPraktijkgebieden.objects.all()
        self.assertEqual(len(imported), 25)

        b = models.GebiedsgerichtwerkenPraktijkgebieden.objects.get(naam='Centrum-Oost')

        self.assertIsInstance(b, models.GebiedsgerichtwerkenPraktijkgebieden)


class ImportGrootstedelijkgebiedTest(TaskTestCase):
    def task(self):
        return batch.ImportGrootstedelijkgebiedTask(GEBIEDEN_SHP)

    def test_import(self):
        self.run_task()

        imported = models.Grootstedelijkgebied.objects.all()
        self.assertEqual(len(imported), 46)

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
        self.assertEqual(len(imported), 58)

        l = models.Ligplaats.objects.get(pk='03630001028467')
        self.assertEqual(l.landelijk_id, '0363020001028467')
        self.assertEqual(l.vervallen, False)
        self.assertIsNone(l.bron)
        self.assertEqual(l.status.code, '33')
        self.assertEqual(l.buurt.id, '03630000000491')
        self.assertEqual(l.document_mutatie, datetime.date(2010, 9, 9))
        self.assertEqual(l.document_nummer, 'GV00000407')
        self.assertEqual(l.begin_geldigheid, datetime.date(2010, 9, 9))
        self.assertIsNone(l.einde_geldigheid)
        self.assertEqual(l.mutatie_gebruiker, 'DBI')

    def test_import_geo(self):
        self.run_task()

        imported = models.Ligplaats.objects.exclude(geometrie__isnull=True)
        self.assertEqual(len(imported), 58)

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
        self.assertEqual(w.id, '03630022796658')
        self.assertEqual(w.landelijk_id, '3594')
        self.assertEqual(w.naam, 'Amsterdam')
        self.assertEqual(w.document_mutatie, datetime.date(2014, 1, 10))
        self.assertEqual(w.document_nummer, 'GV00001729_AC00AC')
        self.assertEqual(w.naam_ptt, 'AMSTERDAM')
        self.assertEqual(w.vervallen, False)
        self.assertEqual(w.gemeente.id, '03630000000000')
        self.assertEqual(w.begin_geldigheid, datetime.date(2014, 1, 10))
        self.assertIsNone(w.einde_geldigheid)
        self.assertEqual(w.mutatie_gebruiker, 'DBI')


class ImportOprTest(TaskTestCase):
    def setUp(self):
        factories.StatusFactory.create(code='35')
        factories.WoonplaatsFactory.create(id='03630022796658')

    def task(self):
        return batch.ImportOpenbareRuimteTask(BAG, BAG_WKT, OPR_BESCHRIJVING)

    def test_import(self):
        self.run_task()

        o = models.OpenbareRuimte.objects.get(pk='03630000002701')
        self.assertEqual(o.id, '03630000002701')
        self.assertEqual(o.landelijk_id, '0363300000000879')
        self.assertEqual(
            o.omschrijving, 'Dark Code Lords Preeker en Bert.')
        self.assertEqual(o.type, models.OpenbareRuimte.TYPE_WEG)
        self.assertEqual(o.naam, 'Amstel')
        self.assertEqual(o.code, '02186')
        self.assertEqual(o.document_mutatie, datetime.date(2014, 1, 10))
        self.assertEqual(o.document_nummer, 'GV00001729_AC00AC')
        self.assertEqual(o.straat_nummer, '')
        self.assertEqual(o.naam_nen, 'Amstel')
        self.assertEqual(o.naam_ptt, 'AMSTEL')
        self.assertEqual(o.vervallen, False)
        self.assertIsNone(o.bron)
        self.assertEqual(o.status.code, '35')
        self.assertEqual(o.woonplaats.id, '03630022796658')
        self.assertEqual(o.begin_geldigheid, datetime.date(2014, 1, 10))
        self.assertEqual(o.einde_geldigheid, None)
        self.assertEqual(o.mutatie_gebruiker, 'DBI')
        self.assertIsNotNone(o.geometrie)


class ImportStandplaatsenTest(TaskTestCase):
    def requires(self):
        return [
            batch.ImportStatusTask(BAG),
        ]

    def task(self):
        return batch.ImportStandplaatsenTask(BAG, BAG_WKT)

    def test_import(self):
        self.run_task()

        imported = models.Standplaats.objects.all()
        self.assertEqual(len(imported), 49)

        lp = models.Standplaats.objects.get(pk='03630001002936')
        self.assertEqual(lp.landelijk_id, '0363030001002936')
        self.assertEqual(lp.vervallen, False)
        self.assertIsNone(lp.bron)
        self.assertEqual(lp.status.code, '37')
        self.assertIsNone(lp.buurt)
        self.assertEqual(lp.document_mutatie, datetime.date(2010, 9, 9))
        self.assertEqual(lp.document_nummer, 'GV00000407')
        self.assertEqual(lp.begin_geldigheid, datetime.date(2010, 9, 9))
        self.assertIsNone(lp.einde_geldigheid)
        self.assertEqual(lp.mutatie_gebruiker, 'DBI')

    def test_import_geo(self):
        self.run_task()

        imported = models.Standplaats.objects.exclude(geometrie__isnull=True)
        self.assertEqual(len(imported), 49)

        lp = models.Standplaats.objects.get(pk='03630001002936')
        self.assertIsNotNone(lp.geometrie)


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
        self.assertEqual(
            v.geometrie, Point(121466, 493032, srid=28992),
            "%s != 121466, 493032" % v.geometrie)
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
        self.assertEqual(n.id, '03630000512845')
        self.assertEqual(n.landelijk_id, '0363200000512845')
        self.assertEqual(n.huisnummer, 26)
        self.assertEqual(n.huisletter, 'G')
        self.assertEqual(n.huisnummer_toevoeging, '')
        self.assertEqual(n.postcode, '1018DS')
        self.assertEqual(n.document_mutatie, datetime.date(2005, 5, 25))
        self.assertEqual(n.document_nummer, 'GV00000403')
        self.assertEqual(
            n.type, models.Nummeraanduiding.OBJECT_TYPE_LIGPLAATS)
        self.assertEqual(n.vervallen, False)
        self.assertIsNone(n.bron)
        self.assertEqual(n.status.code, '16')
        self.assertEqual(n.openbare_ruimte.id, '03630000003910')
        self.assertEqual(n.begin_geldigheid, datetime.date(2005, 5, 25))
        self.assertIsNone(n.einde_geldigheid)
        self.assertEqual(n.mutatie_gebruiker, 'DBI')


class SetHoofdAdressenTest(TaskTestCase):

    def loadNums(self):
        batch.ImportNumTask(BAG).execute()

    def task(self):
        return batch.SetHoofdAdres(BAG)

    def test_num_lig_hfd_import(self):
        factories.OpenbareRuimteFactory.create(pk='03630000003404')
        factories.OpenbareRuimteFactory.create(pk='03630000001094')
        factories.LigplaatsFactory.create(pk='03630001035885')

        self.loadNums()
        self.run_task()

        n = models.Nummeraanduiding.objects.get(pk='03630000520671')
        lp = models.Ligplaats.objects.get(pk='03630001035885')

        self.assertEqual(n.ligplaats.id, lp.id)
        self.assertEqual(lp.hoofdadres.id, n.id)
        self.assertIn(n.id, [a.id for a in lp.adressen.all()])

    def test_num_sta_hfd_import(self):
        factories.OpenbareRuimteFactory.create(pk='03630000001094')
        factories.StandplaatsFactory.create(pk='03630000717733')

        self.loadNums()
        self.run_task()

        n = models.Nummeraanduiding.objects.get(pk='03630000398621')
        s = models.Standplaats.objects.get(pk='03630000717733')

        self.assertEqual(n.standplaats.id, s.id)
        self.assertEqual(s.hoofdadres.id, n.id)
        self.assertIn(n.id, [a.id for a in s.adressen.all()])

    def test_num_vbo_hfd_import(self):
        factories.OpenbareRuimteFactory.create(pk='03630000004150')
        factories.VerblijfsobjectFactory.create(pk='03630000721053')

        self.loadNums()
        self.run_task()

        n = models.Nummeraanduiding.objects.get(pk='03630000181936')
        v = models.Verblijfsobject.objects.get(pk='03630000721053')

        self.assertEqual(n.verblijfsobject.id, v.id)
        self.assertEqual(v.hoofdadres.id, n.id)
        self.assertIn(n.id, [vn.id for vn in v.adressen.all()])

    def test_num_vbo_nvn_import(self):
        factories.OpenbareRuimteFactory.create(pk='03630000003699')
        factories.OpenbareRuimteFactory.create(pk='03630000003293')
        factories.VerblijfsobjectFactory.create(pk='03630000643306')

        self.loadNums()
        self.run_task()

        v = models.Verblijfsobject.objects.get(pk='03630000643306')
        n1 = models.Nummeraanduiding.objects.get(pk='03630000087815')
        n2 = models.Nummeraanduiding.objects.get(pk='03630000105581')

        self.assertIn(n1.id, [n.id for n in v.adressen.all()])
        self.assertIn(n2.id, [n.id for n in v.adressen.all()])
        self.assertEqual(n1.verblijfsobject.id, v.id)
        self.assertEqual(n2.verblijfsobject.id, v.id)


class ImportPandTest(TaskTestCase):

    def setUp(self):
        factories.StatusFactory.create(pk='31')
        factories.BouwblokFactory.create(pk='03630012102404')

    def task(self):
        return batch.ImportPandTask(BAG, BAG_WKT)

    def test_import(self):
        self.run_task()

        imported = models.Pand.objects.all()
        self.assertEqual(len(imported), 79)

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
        self.assertEqual(p.bouwblok.id, '03630012102404')

    def test_import_geo(self):
        self.run_task()

        imported = models.Pand.objects.exclude(geometrie__isnull=True)
        self.assertEqual(len(imported), 79)


class ImportPandNaamTest(TaskTestCase):

    def requires(self):
        return [
            batch.ImportStatusTask(BAG),
            batch.ImportVboTask(BAG),
            batch.ImportPandTask(BAG, BAG_WKT),
        ]

    def task(self):
        return batch.ImportPandNaamTask(BAG)

    def test_import(self):
        self.run_task()
        # all panden should have names now
        # in reality there are only 200..
        naam_count = models.Pand.objects.filter(pandnaam__isnull=False).count()
        self.assertTrue(naam_count > 0)


class ImportIndicatieAOTTaskTest(TaskTestCase):

    def requires(self):
        return [
            batch.ImportStatusTask(BAG),
            batch.ImportStandplaatsenTask(BAG, BAG_WKT),
            batch.ImportLigTask(BAG, BAG_WKT),
            batch.ImportVboTask(BAG),
            batch.ImportIndicatieAOTTask(BAG),
        ]

    def task(self):
        return batch.DenormalizeIndicatieTask()

    def test_indicaties(self):
        self.run_task()

        # check ligplaats, standplaatsen, vbo have indicaties.
        lp_count = models.Ligplaats.objects.filter(indicatie_geconstateerd__isnull=False).count()
        st_count = models.Standplaats.objects.filter(indicatie_geconstateerd__isnull=False).count()
        vbo = models.Verblijfsobject.objects.filter(indicatie_geconstateerd__isnull=False).count()

        vb_count_i_f = models.Verblijfsobject.objects.filter(indicatie_in_onderzoek=False).count()
        vb_count_i_t = models.Verblijfsobject.objects.filter(indicatie_in_onderzoek=True).count()

        vb_count_g_f = models.Verblijfsobject.objects.filter(indicatie_geconstateerd=False).count()
        vb_count_g_t = models.Verblijfsobject.objects.filter(indicatie_geconstateerd=True).count()

        self.assertTrue(lp_count > 0)
        self.assertTrue(st_count > 0)
        self.assertTrue(vbo > 0)

        self.assertTrue(vb_count_i_f > 0)
        self.assertTrue(vb_count_i_t > 0)

        self.assertTrue(vb_count_g_f > 0)
        self.assertTrue(vb_count_g_t > 0)


class ImportVboPandTaskTest(TaskTestCase):
    def requires(self):
        return [
            batch.ImportStatusTask(BAG),
            batch.ImportVboTask(BAG),
            batch.ImportPandTask(BAG, BAG_WKT),
        ]

    def task(self):
        return batch.ImportPandVboTask(BAG)

    def test_import(self):
        self.run_task()

        imported = models.VerblijfsobjectPandRelatie.objects.all()
        self.assertEqual(len(imported), 96)

        p = models.Pand.objects.get(pk='03630013113460')
        v1 = models.Verblijfsobject.objects.get(pk='03630000716108')
        v2 = models.Verblijfsobject.objects.get(pk='03630000716112')
        v3 = models.Verblijfsobject.objects.get(pk='03630000716086')

        self.assertCountEqual(
            [v.id for v in p.verblijfsobjecten.all()],
            [v1.id, v2.id, v3.id])
        self.assertEqual([_p.id for _p in v1.panden.all()], [p.id])


class UpdateGGWGebiedenTaskTest(TaskTestCase):

    def requires(self):
        return [
            batch.ImportGmeTask(GEBIEDEN),
            batch.ImportSdlTask(GEBIEDEN, GEBIEDEN_SHP),
            batch.ImportWijkTask(GEBIEDEN_SHP),
            batch.ImportBuurtTask(GEBIEDEN, GEBIEDEN_SHP),
            batch.ImportStatusTask(BAG),
            batch.ImportVboTask(BAG),
            batch.ImportStandplaatsenTask(BAG, BAG_WKT),
            batch.ImportLigTask(BAG, BAG_WKT),
            batch.ImportGebiedsgerichtwerkenTask(GEBIEDEN_SHP),
            batch.ImportGebiedsgerichtwerkenPraktijkgebiedenTask(GEBIEDEN_SHP)
        ]

    def task(self):
        assert models.Verblijfsobject.objects.count() > 0
        assert models.Standplaats.objects.count() > 0
        assert models.Gebiedsgerichtwerken.objects.count() > 0
        return batch.UpdateGebiedenAttributenTask()

    def test_import(self):
        self.run_task()

        # Gebiedsgerichtwerken coveren de hele stad
        # dus kan er geen vbo, standplaats, lig_n
        # zonder dit veld ingevuld.

        # NOTE buurten coveren niet alleen de stad.
        # alleen bijlmer area.

        # check that everything has a GGW code

        vb_n = models.Verblijfsobject.objects.filter(
            _gebiedsgerichtwerken__isnull=True)

        self.assertTrue(vb_n.count() == 0)

        std_n = models.Standplaats.objects.filter(
            _gebiedsgerichtwerken__isnull=True)

        self.assertTrue(std_n.count() == 0)

        lig_n = models.Ligplaats.objects.filter(
            _gebiedsgerichtwerken__isnull=True)

        self.assertTrue(lig_n.count() == 0)

        # test GGW. DX20, DX21, DX22

        # buurten coveren maar klein deel van de stad.
        ggd_ids = ['DX20', 'DX21', 'DX22']

        for ggw in (
            models.Gebiedsgerichtwerken.objects
                .filter(geometrie__isnull=False)
                .filter(code__in=ggd_ids)):

            self.assertTrue(ggw.buurten.count() > 0, ggw.naam)


class UpdateGSGebiedenTaskTest(TaskTestCase):

    def requires(self):

        factories.VerblijfsobjectFactory.create(
            geometrie=Point(115909, 491336, srid=28992))

        return [

            batch.ImportGrootstedelijkgebiedTask(GEBIEDEN_SHP)
        ]

    def task(self):
        assert models.Verblijfsobject.objects.count() > 0
        assert models.Grootstedelijkgebied.objects.count() > 0
        return batch.UpdateGrootstedelijkAttributenTask()

    def test_import(self):
        self.run_task()

        # There is at least one vbo in a grootstedelijkgebied
        vb_n = models.Verblijfsobject.objects.filter(
            _grootstedelijkgebied__isnull=False)

        # check that a vbo has a GSG code
        self.assertTrue(vb_n.count() > 0)


class ImportGebruiksdoelenTaskTest(TaskTestCase):
    def requires(self):
        return [batch.ImportVboTask(BAG)]

    def task(self):
        return batch.ImportGebruiksdoelenTask(BAG)

    def test_import(self):
        self.run_task()

        # check that several Gebruiksdoelen were imported:
        g = list(models.Gebruiksdoel.objects.all())
        self.assertTrue(g)
        g_special = models.Gebruiksdoel.objects.filter(verblijfsobject_id='03630000716895')[0]
        self.assertEqual(g_special.code, '1100')
        self.assertEqual(g_special.code_plus, '')
        self.assertEqual(g_special.omschrijving_plus, '')
        g_special_plus = models.Gebruiksdoel.objects.filter(verblijfsobject_id='03630000712887')[0]
        self.assertEqual(g_special_plus.code, '1000')
        self.assertEqual(g_special_plus.code_plus, '1010')
        self.assertEqual(g_special_plus.omschrijving_plus, 'BEST-woning')

