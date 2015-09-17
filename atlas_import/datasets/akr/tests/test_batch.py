import datetime

from django.test import TestCase

from datasets.generic import cache
from .. import batch, models

AKR = 'diva/kadaster/akr'


class ImportKotTest(TestCase):
    def test_import(self):
        c = cache.Cache()

        task = batch.ImportKotTask(AKR, c)
        task.execute()
        c.flush()

        imported = models.KadastraalObject.objects.all()
        self.assertEqual(len(imported), 495)

        kot = models.KadastraalObject.objects.get(pk='ASD25AD00412G0000')

        self.assertIsNotNone(kot)
        self.assertEqual(kot.gemeentecode, "ASD25")
        self.assertEqual(kot.sectie, "AD")
        self.assertEqual(kot.perceelnummer, 412)
        self.assertEqual(kot.objectindex_letter, "G")
        self.assertEqual(kot.objectindex_nummer, 0)
        self.assertEqual(kot.grootte, 11350)
        self.assertEqual(kot.grootte_geschat, False)
        self.assertEqual(kot.cultuur_tekst, '')
        self.assertEqual(kot.soort_cultuur_onbebouwd.code, 57)
        self.assertEqual(kot.soort_cultuur_onbebouwd.omschrijving, "ERF EN TUIN")
        self.assertEqual(kot.meer_culturen_onbebouwd, True)
        self.assertEqual(kot.bebouwingscode.code, 2)
        self.assertEqual(kot.bebouwingscode.omschrijving, "ONBEBOUWD MET BEBOUWD")
        self.assertEqual(kot.kaartblad, 30)
        self.assertEqual(kot.ruitletter, "D")
        self.assertEqual(kot.ruitnummer, 5)
        self.assertEqual(kot.omschrijving_deelperceel, '')


class ImportKstTest(TestCase):
    def test_import(self):
        c = cache.Cache()

        task = batch.ImportKstTask(AKR, c)
        task.execute()

        c.flush()

        imported = models.KadastraalSubject.objects.all()
        self.assertEqual(len(imported), 163)

        kst = models.KadastraalSubject.objects.get(pk='44879')
        self.assertEqual(kst.subjectnummer, 1603175440)
        self.assertIsNone(kst.titel_of_predikaat)
        self.assertEqual(kst.geslachtsaanduiding, '')
        self.assertEqual(kst.geslachtsnaam, '')
        self.assertEqual(kst.diacritisch, False)
        self.assertEqual(kst.naam_niet_natuurlijke_persoon, "DELTA LLOYD VASTGOED WONINGEN B.V")
        self.assertEqual(kst.soort_subject, '')
        self.assertEqual(kst.soort_niet_natuurlijke_persoon.code, 'BV')
        self.assertEqual(kst.soort_niet_natuurlijke_persoon.omschrijving,
                         'BESLOTEN VENNOOTSCHAP MET BEPERKTE AANSPRAKELIJKHEID')
        self.assertEqual(kst.voorletters, '')
        self.assertEqual(kst.voornamen, '')
        self.assertEqual(kst.voorvoegsel, '')
        self.assertIsNone(kst.geboortedatum)
        self.assertEqual(kst.geboorteplaats, '')
        self.assertEqual(kst.overleden, False)
        self.assertIsNone(kst.overlijdensdatum)
        self.assertEqual(kst.zetel, 'AMSTERDAM')
        self.assertEqual(kst.woonadres.straatnaam, 'Spaklerwg')
        self.assertEqual(kst.woonadres.huisnummer, 4)
        self.assertEqual(kst.woonadres.huisletter, '')
        self.assertEqual(kst.woonadres.toevoeging, '')
        self.assertEqual(kst.woonadres.postcode, '1096BA')
        self.assertEqual(kst.woonadres.aanduiding, '')
        self.assertEqual(kst.woonadres.woonplaats, 'AMSTERDAM')
        self.assertEqual(kst.woonadres.adresregel_1, '')
        self.assertEqual(kst.woonadres.adresregel_2, '')
        self.assertEqual(kst.woonadres.adresregel_3, '')
        self.assertEqual(kst.woonadres.land, None)
        self.assertEqual(kst.woonadres.beschrijving, '')
        self.assertIsNone(kst.postadres)
        self.assertIsNone(kst.a_nummer)

        kst = models.KadastraalSubject.objects.get(pk='9724')
        self.assertEqual(kst.subjectnummer, 1600343431)
        self.assertEqual(kst.titel_of_predikaat.code, 'DRS')
        self.assertEqual(kst.titel_of_predikaat.omschrijving, 'Doctorandus')
        self.assertEqual(kst.geslachtsaanduiding, 'm')
        self.assertEqual(kst.geslachtsnaam, 'KLEIN')
        self.assertEqual(kst.diacritisch, False)
        self.assertEqual(kst.naam_niet_natuurlijke_persoon, '')
        self.assertEqual(kst.soort_subject, 'm')
        self.assertIsNone(kst.soort_niet_natuurlijke_persoon)
        self.assertEqual(kst.voorletters, 'S.')
        self.assertEqual(kst.voornamen, 'STAND')
        self.assertEqual(kst.voorvoegsel, 'VAN DER')
        self.assertEqual(kst.geboortedatum, datetime.date(1943, 3, 11))
        self.assertEqual(kst.geboorteplaats, 'AMSTERDAM')
        self.assertEqual(kst.overleden, False)
        self.assertIsNone(kst.overlijdensdatum)
        self.assertEqual(kst.zetel, '')
        self.assertEqual(kst.woonadres.straatnaam, 'J V GOYENKD')
        self.assertEqual(kst.woonadres.huisnummer, 170)
        self.assertEqual(kst.woonadres.huisletter, '')
        self.assertEqual(kst.woonadres.toevoeging, '')
        self.assertEqual(kst.woonadres.postcode, '1058EN')
        self.assertEqual(kst.woonadres.aanduiding, '')
        self.assertEqual(kst.woonadres.woonplaats, 'AMSTERDAM')
        self.assertEqual(kst.woonadres.adresregel_1, '')
        self.assertEqual(kst.woonadres.adresregel_2, '')
        self.assertEqual(kst.woonadres.adresregel_3, '')
        self.assertEqual(kst.woonadres.land, None)
        self.assertEqual(kst.woonadres.beschrijving, '')
        self.assertIsNone(kst.postadres)
        self.assertIsNone(kst.a_nummer)


class ImportTteTest(TestCase):
    def test_import(self):
        c = cache.Cache()

        task = batch.ImportTteTask(AKR, c)
        task.execute()
        c.flush()

        imported = models.Transactie.objects.all()
        self.assertEqual(len(imported), 801)

        tx = models.Transactie.objects.get(pk='1005480')

        self.assertEqual(tx.registercode, '1005480')
        self.assertEqual(tx.stukdeel_1, '17088')
        self.assertEqual(tx.stukdeel_2, '00033')
        self.assertEqual(tx.stukdeel_3, '')
        self.assertEqual(tx.ontvangstdatum, datetime.date(2000, 12, 20))
        self.assertEqual(tx.soort_stuk.code, '001')
        self.assertEqual(tx.soort_stuk.omschrijving, 'AKTE VAN KOOP EN VERKOOP')
        self.assertEqual(tx.verlijdensdatum, datetime.date(2000, 12, 19))
        self.assertEqual(tx.meer_kadastrale_objecten, True)
        self.assertEqual(tx.koopjaar, 2000)
        self.assertEqual(tx.koopsom, 46444405)
        self.assertEqual(tx.belastingplichtige, True)


class ImportZrtTest(TestCase):
    def test_import(self):
        c = cache.Cache()

        batch.ImportKotTask(AKR, c).execute()
        batch.ImportKstTask(AKR, c).execute()
        batch.ImportTteTask(AKR, c).execute()

        task = batch.ImportZrtTask(AKR, c)
        task.execute()
        c.flush()

        imported = models.ZakelijkRecht.objects.all()
        self.assertEqual(len(imported), 400)

        zrt = models.ZakelijkRecht.objects.get(pk='1397395')

        self.assertEqual(zrt.identificatie, '1397395')
        self.assertEqual(zrt.soort_recht.code, 'EVOS')
        self.assertEqual(zrt.soort_recht.omschrijving, 'EIGENDOM BEL. MET RECHT VAN OPSTAL')
        self.assertEqual(zrt.volgnummer, 3)
        self.assertEqual(zrt.aandeel_medegerechtigden, '')
        self.assertEqual(zrt.aandeel_subject, '1/1')
        self.assertEqual(zrt.einde_filiatie, False)
        self.assertEqual(zrt.sluimerend, False)
        self.assertEqual(zrt.kadastraal_object.id, 'ASD25AD00588G0000')
        self.assertEqual(zrt.kadastraal_subject.id, '20857')
        self.assertEqual(zrt.transactie.id, '170922')
