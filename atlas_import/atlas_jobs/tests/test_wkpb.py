import datetime

from django.test import TestCase

from atlas import models
from atlas_jobs.batch import wkpb, kadaster

BEPERKINGEN = 'diva/beperkingen'
KAD_LKI = 'diva/kadaster/lki'


class ImportBeperkingcode(TestCase):
    def test_import(self):
        task = wkpb.ImportBeperkingcodeTask(BEPERKINGEN)
        task.execute()

        imported = models.Beperkingcode.objects.all()
        self.assertEqual(len(imported), 20)

        a = models.Beperkingcode.objects.get(pk='VI')
        self.assertEqual(a.omschrijving, 'Aanwijzing van gronden, Wet Voorkeursrecht gemeenten')


class ImportWkpbBroncode(TestCase):
    def test_import(self):
        task = wkpb.ImportWkpbBroncodeTask(BEPERKINGEN)
        task.execute()

        imported = models.WkpbBroncode.objects.all()
        self.assertEqual(len(imported), 6)

        a = models.WkpbBroncode.objects.get(pk='5')
        self.assertEqual(a.omschrijving, 'Dagelijks Bestuur')


class ImportWkpbBrondocument(TestCase):
    def test_import(self):
        wkpb.ImportWkpbBroncodeTask(BEPERKINGEN).execute()

        task = wkpb.ImportWkpbBrondocumentTask(BEPERKINGEN)
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
        wkpb.ImportWkpbBroncodeTask(BEPERKINGEN).execute()
        wkpb.ImportWkpbBrondocumentTask(BEPERKINGEN).execute()
        wkpb.ImportBeperkingcodeTask(BEPERKINGEN).execute()

        task = wkpb.ImportBeperkingTask(BEPERKINGEN)
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
        wkpb.ImportWkpbBroncodeTask(BEPERKINGEN).execute()
        wkpb.ImportWkpbBrondocumentTask(BEPERKINGEN).execute()
        wkpb.ImportBeperkingcodeTask(BEPERKINGEN).execute()
        wkpb.ImportBeperkingTask(BEPERKINGEN).execute()
        kadaster.ImportLkiKadastraalObjectTask(KAD_LKI).execute()

        task = wkpb.ImportWkpbBepKadTask(BEPERKINGEN)
        task.execute()

        bk = models.BeperkingKadastraalObject.objects.get(pk='1001730_ASD12P03580A0061')
        self.assertEqual(bk.beperking.id, 1001730)
        self.assertEqual(bk.kadastraal_object.aanduiding, 'ASD12P03580A0061')
