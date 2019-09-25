import datetime
import logging
from unittest import skip

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


@skip
class ImportBuurtTest(TaskTestCase):
    def setUp(self):
        factories.StadsdeelFactory.create(pk='03630000000016')
        factories.BuurtcombinatieFactory.create(code='92')

    def task(self):
        return batch.ImportBuurtTask(GEBIEDEN)

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


@skip
class ImportBouwblokTest(TaskTestCase):

    def requires(self):
        return [
            batch.ImportWijkTask(GEBIEDEN_SHP),
            batch.ImportBuurtTask(GEBIEDEN),
        ]

    def task(self):
        return batch.ImportBouwblokTask(GEBIEDEN)

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
@skip
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


@skip
class ImportGebiedsgerichtwerkenTest(TaskTestCase):
    def task(self):
        return batch.ImportGebiedsgerichtwerkenTask(GEBIEDEN_SHP)

    def test_import(self):
        self.run_task()

        imported = models.Gebiedsgerichtwerken.objects.all()
        self.assertEqual(len(imported), 23)

        b = models.Gebiedsgerichtwerken.objects.get(code='DX06')

        self.assertEqual(b.stadsdeel.id, '03630011872037')


@skip
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


@skip
class ImportGrootstedelijkgebiedTest(TaskTestCase):
    def task(self):
        return batch.ImportGrootstedelijkgebiedTask(GEBIEDEN_SHP)

    def test_import(self):
        self.run_task()

        imported = models.Grootstedelijkgebied.objects.all()
        self.assertEqual(len(imported), 46)

        b = models.Grootstedelijkgebied.objects.get(naam='Overamstel')

        self.assertIsInstance(b, models.Grootstedelijkgebied)


@skip
class ImportUnescoTest(TaskTestCase):
    def task(self):
        return batch.ImportUnescoTask(GEBIEDEN_SHP)

    def test_import(self):
        self.run_task()

        imported = models.Unesco.objects.all()
        self.assertEqual(len(imported), 2)

        b = models.Unesco.objects.get(naam='Kernzone')

        self.assertIsInstance(b, models.Unesco)


@skip
class ImportOprTest(TaskTestCase):
    def setUp(self):
        factories.StatusFactory.create(code='35')
        factories.WoonplaatsFactory.create(id='03630022796658')

    def task(self):
        return batch.ImportOpenbareRuimteTask(BAG)

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


@skip
class ImportStandplaatsenTest(TaskTestCase):
    def task(self):
        return batch.ImportStandplaatsenTask(BAG)

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


@skip
class ImportPandTest(TaskTestCase):

    def setUp(self):
        factories.StatusFactory.create(pk='31')
        factories.BouwblokFactory.create(pk='03630012102404')

    def task(self):
        return batch.ImportPandTask(BAG)

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


@skip
class UpdateGGWGebiedenTaskTest(TaskTestCase):

    def requires(self):
        return [
            batch.ImportWijkTask(GEBIEDEN_SHP),
            batch.ImportBuurtTask(GEBIEDEN),
            batch.ImportStandplaatsenTask(BAG),
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
