import datetime

from django.test import TestCase

from .. import models, batch
from datasets.lki import batch as lki

BEPERKINGEN = 'diva/beperkingen'
KAD_LKI = 'diva/kadaster/lki'


class ImportBeperkingcode(TestCase):
    def test_import(self):
        task = batch.ImportBeperkingcodeTask(BEPERKINGEN)
        task.execute()

        imported = models.Beperkingcode.objects.all()
        self.assertEqual(len(imported), 20)

        a = models.Beperkingcode.objects.get(pk='VI')
        self.assertEqual(a.omschrijving, 'Aanwijzing van gronden, Wet Voorkeursrecht gemeenten')


class ImportWkpbBroncode(TestCase):
    def test_import(self):
        task = batch.ImportWkpbBroncodeTask(BEPERKINGEN)
        task.execute()

        imported = models.Broncode.objects.all()
        self.assertEqual(len(imported), 6)

        a = models.Broncode.objects.get(pk='5')
        self.assertEqual(a.omschrijving, 'Dagelijks Bestuur')


class ImportWkpbBrondocument(TestCase):
    def test_import(self):
        batch.ImportWkpbBroncodeTask(BEPERKINGEN).execute()

        task = batch.ImportWkpbBrondocumentTask(BEPERKINGEN)
        task.execute()

        imported = models.Brondocument.objects.all()
        self.assertEqual(len(imported), 48)

        a = models.Brondocument.objects.get(pk=6641)
        self.assertEqual(a.documentnummer, 6641)
        self.assertEqual(a.documentnaam, 'BD00000149_WK00WK.pdf')
        self.assertEqual(a.bron.omschrijving, 'Burgemeester')
        self.assertEqual(a.persoonsgegeven_afschermen, False)


class ImportBeperking(TestCase):
    def test_import(self):
        batch.ImportWkpbBroncodeTask(BEPERKINGEN).execute()
        batch.ImportWkpbBrondocumentTask(BEPERKINGEN).execute()
        batch.ImportBeperkingcodeTask(BEPERKINGEN).execute()

        task = batch.ImportBeperkingTask(BEPERKINGEN)
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
        batch.ImportWkpbBroncodeTask(BEPERKINGEN).execute()
        batch.ImportWkpbBrondocumentTask(BEPERKINGEN).execute()
        batch.ImportBeperkingcodeTask(BEPERKINGEN).execute()
        batch.ImportBeperkingTask(BEPERKINGEN).execute()
        lki.ImportKadastraalObjectTask(KAD_LKI).execute()

        task = batch.ImportWkpbBepKadTask(BEPERKINGEN)
        task.execute()

        bk = models.BeperkingKadastraalObject.objects.get(pk='1001730_ASD12P03580A0061')
        self.assertEqual(bk.beperking.id, 1001730)
        self.assertEqual(bk.kadastraal_object.aanduiding, 'ASD12P03580A0061')
