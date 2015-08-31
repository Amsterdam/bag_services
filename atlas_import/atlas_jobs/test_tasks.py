import datetime
from django.contrib.gis.geos import Point

from django.test import TestCase

from atlas_jobs import jobs
from atlas import models
import atlas_jobs.batch.bag

BAG = 'atlas_jobs/fixtures/testset/bag'
BAG_WKT = 'atlas_jobs/fixtures/testset/bag_wkt'
GEBIEDEN = 'atlas_jobs/fixtures/testset/gebieden'
BEPERKINGEN = 'atlas_jobs/fixtures/testset/beperkingen'
KAD_LKI = 'atlas_jobs/fixtures/testset/kadaster/lki'
KAD_AKR = 'atlas_jobs/fixtures/testset/kadaster/akr'

class ImportBrnTest(TestCase):
    def test_import(self):
        task = atlas_jobs.batch.bag.ImportBrnTask(BAG)
        task.execute()

        imported = models.Bron.objects.all()
        self.assertEqual(len(imported), 100)

        self.assertIsNotNone(models.Bron.objects.get(pk='PST'))

        b = models.Bron.objects.get(pk='13')
        self.assertEqual(b.omschrijving, 'Stadsdeel Zuideramstel (13)')

    def test_import_twice(self):
        task = atlas_jobs.batch.bag.ImportBrnTask(BAG)
        task.execute()
        task.execute()

        imported = models.Bron.objects.all()
        self.assertEqual(len(imported), 100)


class ImportAvrTest(TestCase):
    def test_import(self):
        task = atlas_jobs.batch.bag.ImportAvrTask(BAG)
        task.execute()

        imported = models.RedenAfvoer.objects.all()
        self.assertEqual(len(imported), 44)

        a = models.RedenAfvoer.objects.get(pk='20')
        self.assertEqual(a.omschrijving, 'Geconstateerd adres')


class ImportEgmTest(TestCase):
    def test_import(self):
        task = atlas_jobs.batch.bag.ImportEgmTask(BAG)
        task.execute()

        imported = models.Eigendomsverhouding.objects.all()
        self.assertEqual(len(imported), 2)

        a = models.Eigendomsverhouding.objects.get(pk='01')
        self.assertEqual(a.omschrijving, 'Huur')


class ImportFngTest(TestCase):
    def test_import(self):
        task = atlas_jobs.batch.bag.ImportFngTask(BAG)
        task.execute()

        imported = models.Financieringswijze.objects.all()
        self.assertEqual(len(imported), 19)

        a = models.Financieringswijze.objects.get(pk='200')
        self.assertEqual(a.omschrijving, 'Premiehuur Profit (200)')


class ImportLggTest(TestCase):
    def test_import(self):
        task = atlas_jobs.batch.bag.ImportLggTask(BAG)
        task.execute()

        imported = models.Ligging.objects.all()
        self.assertEqual(len(imported), 6)

        a = models.Ligging.objects.get(pk='03')
        self.assertEqual(a.omschrijving, 'Tussengebouw')


class ImportGbkTest(TestCase):
    def test_import(self):
        task = atlas_jobs.batch.bag.ImportGbkTask(BAG)
        task.execute()

        imported = models.Gebruik.objects.all()
        self.assertEqual(len(imported), 320)

        a = models.Gebruik.objects.get(pk='0006')
        self.assertEqual(a.omschrijving, 'ZZ-BEDRIJF EN WONING')


class ImportLocTest(TestCase):
    def test_import(self):
        task = atlas_jobs.batch.bag.ImportLocTask(BAG)
        task.execute()

        imported = models.LocatieIngang.objects.all()
        self.assertEqual(len(imported), 5)

        a = models.LocatieIngang.objects.get(pk='04')
        self.assertEqual(a.omschrijving, 'L-zijde')


class ImportTggTest(TestCase):
    def test_import(self):
        task = atlas_jobs.batch.bag.ImportTggTask(BAG)
        task.execute()

        imported = models.Toegang.objects.all()
        self.assertEqual(len(imported), 9)

        a = models.Toegang.objects.get(pk='08')
        self.assertEqual(a.omschrijving, 'Begane grond (08)')


class ImportStsTest(TestCase):
    def test_import(self):
        task = atlas_jobs.batch.bag.ImportStsTask(BAG)
        task.execute()

        imported = models.Status.objects.all()
        self.assertEqual(len(imported), 43)

        self.assertIsNotNone(models.Status.objects.get(pk='10'))

        s = models.Status.objects.get(pk='01')
        self.assertEqual(s.omschrijving, 'Buitengebruik i.v.m. renovatie')


class ImportGmeTest(TestCase):
    def test_import(self):
        task = atlas_jobs.batch.bag.ImportGmeTask(GEBIEDEN)
        task.execute()

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
        atlas_jobs.batch.bag.ImportGmeTask(GEBIEDEN).execute()

        task = atlas_jobs.batch.bag.ImportSdlTask(GEBIEDEN)
        task.execute()

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
        atlas_jobs.batch.bag.ImportGmeTask(GEBIEDEN).execute()
        atlas_jobs.batch.bag.ImportSdlTask(GEBIEDEN).execute()

        task = atlas_jobs.batch.bag.ImportBrtTask(GEBIEDEN)
        task.execute()

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
        atlas_jobs.batch.bag.ImportBrnTask(BAG).execute()
        atlas_jobs.batch.bag.ImportStsTask(BAG).execute()

        atlas_jobs.batch.bag.ImportGmeTask(GEBIEDEN).execute()
        atlas_jobs.batch.bag.ImportSdlTask(GEBIEDEN).execute()
        atlas_jobs.batch.bag.ImportBrtTask(GEBIEDEN).execute()

        task = atlas_jobs.batch.bag.ImportLigTask(BAG)
        task.execute()

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
        atlas_jobs.batch.bag.ImportStsTask(BAG).execute()
        atlas_jobs.batch.bag.ImportLigTask(BAG).execute()

        task = atlas_jobs.batch.bag.ImportLigGeoTask(BAG_WKT)
        task.execute()

        imported = models.Ligplaats.objects.exclude(geometrie__isnull=True)
        self.assertEqual(len(imported), 60)

        l = models.Ligplaats.objects.get(pk='03630001024868')
        self.assertIsNotNone(l.geometrie)


class ImportWplTest(TestCase):
    def test_import(self):
        atlas_jobs.batch.bag.ImportGmeTask(GEBIEDEN).execute()

        task = atlas_jobs.batch.bag.ImportWplTask(BAG)
        task.execute()

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
        atlas_jobs.batch.bag.ImportBrnTask(BAG).execute()
        atlas_jobs.batch.bag.ImportStsTask(BAG).execute()
        atlas_jobs.batch.bag.ImportGmeTask(GEBIEDEN).execute()
        atlas_jobs.batch.bag.ImportWplTask(BAG).execute()

        task = atlas_jobs.batch.bag.ImportOprTask(BAG)
        task.execute()

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
        atlas_jobs.batch.bag.ImportStsTask(BAG).execute()
        atlas_jobs.batch.bag.ImportGmeTask(GEBIEDEN).execute()
        atlas_jobs.batch.bag.ImportWplTask(BAG).execute()
        atlas_jobs.batch.bag.ImportOprTask(BAG).execute()

        task = atlas_jobs.batch.bag.ImportNumTask(BAG)
        task.execute()

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
        atlas_jobs.batch.bag.ImportStsTask(BAG).execute()
        atlas_jobs.batch.bag.ImportGmeTask(GEBIEDEN).execute()
        atlas_jobs.batch.bag.ImportWplTask(BAG).execute()
        atlas_jobs.batch.bag.ImportOprTask(BAG).execute()
        atlas_jobs.batch.bag.ImportNumTask(BAG).execute()
        atlas_jobs.batch.bag.ImportLigTask(BAG).execute()

        task = atlas_jobs.batch.bag.ImportNumLigHfdTask(BAG)
        task.execute()

        n = models.Nummeraanduiding.objects.get(pk='03630000520671')
        l = models.Ligplaats.objects.get(pk='03630001035885')

        self.assertEquals([l.id for l in n.ligplaatsen.all()], [l.id])
        self.assertEquals(l.hoofdadres.id, n.id)


class ImportStaTest(TestCase):
    def test_import(self):
        atlas_jobs.batch.bag.ImportStsTask(BAG).execute()

        task = atlas_jobs.batch.bag.ImportStaTask(BAG)
        task.execute()

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
        atlas_jobs.batch.bag.ImportStsTask(BAG).execute()
        atlas_jobs.batch.bag.ImportStaTask(BAG).execute()

        task = atlas_jobs.batch.bag.ImportStaGeoTask(BAG_WKT)
        task.execute()

        imported = models.Standplaats.objects.exclude(geometrie__isnull=True)
        self.assertEqual(len(imported), 51)

        l = models.Standplaats.objects.get(pk='03630001002936')
        self.assertIsNotNone(l.geometrie)


class ImportNumStaHfdTest(TestCase):
    def test_import(self):
        atlas_jobs.batch.bag.ImportStsTask(BAG).execute()
        atlas_jobs.batch.bag.ImportGmeTask(GEBIEDEN).execute()
        atlas_jobs.batch.bag.ImportWplTask(BAG).execute()
        atlas_jobs.batch.bag.ImportOprTask(BAG).execute()
        atlas_jobs.batch.bag.ImportNumTask(BAG).execute()
        atlas_jobs.batch.bag.ImportStaTask(BAG).execute()

        task = atlas_jobs.batch.bag.ImportNumStaHfdTask(BAG)
        task.execute()

        n = models.Nummeraanduiding.objects.get(pk='03630000398621')
        s = models.Standplaats.objects.get(pk='03630000717733')

        self.assertEquals([l.id for l in n.standplaatsen.all()], [s.id])
        self.assertEquals(s.hoofdadres.id, n.id)


class ImportVboTest(TestCase):
    def test_import(self):
        atlas_jobs.batch.bag.ImportEgmTask(BAG).execute()
        atlas_jobs.batch.bag.ImportFngTask(BAG).execute()
        atlas_jobs.batch.bag.ImportGbkTask(BAG).execute()
        atlas_jobs.batch.bag.ImportLocTask(BAG).execute()
        atlas_jobs.batch.bag.ImportStsTask(BAG).execute()
        atlas_jobs.batch.bag.ImportLggTask(BAG).execute()
        atlas_jobs.batch.bag.ImportTggTask(BAG).execute()

        task = atlas_jobs.batch.bag.ImportVboTask(BAG)
        task.execute()

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
        atlas_jobs.batch.bag.ImportStsTask(BAG).execute()
        atlas_jobs.batch.bag.ImportGmeTask(GEBIEDEN).execute()
        atlas_jobs.batch.bag.ImportWplTask(BAG).execute()
        atlas_jobs.batch.bag.ImportOprTask(BAG).execute()
        atlas_jobs.batch.bag.ImportNumTask(BAG).execute()
        atlas_jobs.batch.bag.ImportVboTask(BAG).execute()

        task = atlas_jobs.batch.bag.ImportNumVboHfdTask(BAG)
        task.execute()

        n = models.Nummeraanduiding.objects.get(pk='03630000181936')
        v = models.Verblijfsobject.objects.get(pk='03630000721053')

        self.assertEquals([v.id for v in n.verblijfsobjecten.all()], [v.id])
        self.assertEquals(v.hoofdadres.id, n.id)


class ImportPndTest(TestCase):

    def test_import(self):
        atlas_jobs.batch.bag.ImportStsTask(BAG).execute()

        task = atlas_jobs.batch.bag.ImportPndTask(BAG)
        task.execute()

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
        atlas_jobs.batch.bag.ImportStsTask(BAG).execute()
        atlas_jobs.batch.bag.ImportPndTask(BAG).execute()

        task = atlas_jobs.batch.bag.ImportPndGeoTask(BAG_WKT)
        task.execute()

        imported = models.Pand.objects.exclude(geometrie__isnull=True)
        self.assertEquals(len(imported), 79)

class ImportVboPndTask(TestCase):

    def test_import(self):
        atlas_jobs.batch.bag.ImportStsTask(BAG).execute()
        atlas_jobs.batch.bag.ImportVboTask(BAG).execute()
        atlas_jobs.batch.bag.ImportPndTask(BAG).execute()

        task = atlas_jobs.batch.bag.ImportPndVboTask(BAG)
        task.execute()

        p = models.Pand.objects.get(pk='03630013113460')
        v1 = models.Verblijfsobject.objects.get(pk='03630000716108')
        v2 = models.Verblijfsobject.objects.get(pk='03630000716112')
        v3 = models.Verblijfsobject.objects.get(pk='03630000716086')

        self.assertCountEqual([v.id for v in p.verblijfsobjecten.all()], [v1.id, v2.id, v3.id])
        self.assertEqual([p.id for p in v1.panden.all()], [p.id])

class ImportBeperkingcode(TestCase):

    def test_import(self):
        task = jobs.ImportBeperkingcodeTask(BEPERKINGEN)
        task.execute()

        imported = models.Beperkingcode.objects.all()
        self.assertEqual(len(imported), 20)

        a = models.Beperkingcode.objects.get(pk='VI')
        self.assertEqual(a.omschrijving, 'Aanwijzing van gronden, Wet Voorkeursrecht gemeenten')

class ImportWkpbBroncode(TestCase):

    def test_import(self):
        task = jobs.ImportWkpbBroncodeTask(BEPERKINGEN)
        task.execute()

        imported = models.WkpbBroncode.objects.all()
        self.assertEqual(len(imported), 6)

        a = models.WkpbBroncode.objects.get(pk='5')
        self.assertEqual(a.omschrijving, 'Dagelijks Bestuur')

class ImportWkpbBrondocument(TestCase):

    def test_import(self):

        jobs.ImportWkpbBroncodeTask(BEPERKINGEN).execute()

        task = jobs.ImportWkpbBrondocumentTask(BEPERKINGEN)
        task.execute()

        imported = models.WkpbBrondocument.objects.all()
        self.assertEqual(len(imported), 48)

        a = models.WkpbBrondocument.objects.get(pk=6641)
        self.assertEqual(a.documentnummer, 6641)
        self.assertEqual(a.documentnaam, 'BD00000149_WK00WK.pdf')
        self.assertEqual(a.bron.omschrijving, 'Burgemeester')
        self.assertEqual(a.persoonsgegeven_afschermen, False)


class ImportBeperking(TestCase):

    def test_import(self):

        jobs.ImportWkpbBroncodeTask(BEPERKINGEN).execute()
        jobs.ImportWkpbBrondocumentTask(BEPERKINGEN).execute()
        jobs.ImportBeperkingcodeTask(BEPERKINGEN).execute()

        task = jobs.ImportBeperkingTask(BEPERKINGEN)
        task.execute()

        imported = models.Beperking.objects.all()
        self.assertEqual(len(imported), 50)

        b = models.Beperking.objects.get(pk=1001730)
        self.assertEqual(b.inschrijfnummer, 1156)
        self.assertEqual(b.beperkingtype.omschrijving, 'Melding, bevel, beschikking of vordering Wet bodembescherming')
        self.assertEqual(b.datum_in_werking, datetime.date(2008, 12, 17))
        self.assertEqual(b.datum_einde, None)


class ImportWkpbBepKad(TestCase):

    def test_import(self):

        jobs.ImportWkpbBroncodeTask(BEPERKINGEN).execute()
        jobs.ImportWkpbBrondocumentTask(BEPERKINGEN).execute()
        jobs.ImportBeperkingcodeTask(BEPERKINGEN).execute()
        jobs.ImportBeperkingTask(BEPERKINGEN).execute()
        jobs.ImportLkiKadastraalObjectTask(KAD_LKI).execute()

        task = jobs.ImportWkpbBepKadTask(BEPERKINGEN)
        task.execute()

        bk = models.BeperkingKadastraalObject.objects.get(pk='1001730_ASD12P03580A0061')
        self.assertEqual(bk.beperking.id, 1001730)
        self.assertEqual(bk.kadastraal_object.aanduiding, 'ASD12P03580A0061')


# Kadaster

class ImportLkiGemeente(TestCase):

    def test_import(self):

        task = jobs.ImportLkiGemeenteTask(KAD_LKI)
        task.execute()

        g = models.LkiGemeente.objects.get(pk=3630010602635)
        self.assertEqual(g.gemeentenaam, 'AMSTERDAM')
        self.assertEqual(g.gemeentecode, 363)
        self.assertEqual(g.geometrie.area, 219491741.99025947)

        
class ImportLkiKadastraleGemeente(TestCase):

    def test_import(self):

        task = jobs.ImportLkiKadastraleGemeenteTask(KAD_LKI)
        task.execute()

        g = models.LkiKadastraleGemeente.objects.get(pk=3630010602590)
        self.assertEqual(g.code, 'ASD06')
        self.assertEqual(g.ingang_cyclus, datetime.date(2008, 12, 2))
        self.assertEqual(g.geometrie.area, 1278700.9685260097)


class ImportLkiSectie(TestCase):
    
    def test_import(self):
        
        task = jobs.ImportLkiSectieTask(KAD_LKI)
        task.execute()

        s = models.LkiSectie.objects.get(pk=3630010602661)
        self.assertEqual(s.kadastrale_gemeente_code, 'RDP00')
        self.assertEqual(s.code, 'C')
        self.assertEqual(s.ingang_cyclus, datetime.date(2008, 12, 2))
        self.assertEqual(s.geometrie.area, 869579.8324124987)

        
class ImportLkiKadastraalObject(TestCase):
    
    def test_import(self):
        
        task = jobs.ImportLkiKadastraalObjectTask(KAD_LKI)
        task.execute()

        o = models.LkiKadastraalObject.objects.get(pk=3630010603206)
        self.assertEqual(o.kadastrale_gemeente_code, 'STN02')
        self.assertEqual(o.sectie_code, 'G')
        self.assertEqual(o.perceelnummer, 1478)
        self.assertEqual(o.indexletter, 'G')
        self.assertEqual(o.indexnummer, 0)
        self.assertEqual(o.oppervlakte, 76)
        self.assertEqual(o.ingang_cyclus, datetime.date(2015, 2, 10))
        self.assertEqual(o.aanduiding, 'STN02G01478G0000')
        self.assertEqual(o.geometrie.area, 78.42037450020632)


