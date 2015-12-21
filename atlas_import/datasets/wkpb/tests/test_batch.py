import datetime

from batch.test import TaskTestCase
from .. import models, batch

BEPERKINGEN = 'diva/beperkingen'
KAD_LKI = 'diva/kadaster/lki'
KAD_AKR = 'diva/kadaster/akr'


class ImportBeperkingcode(TaskTestCase):
    def task(self):
        return batch.ImportBeperkingcodeTask(BEPERKINGEN)

    def test_import(self):
        self.run_task()

        imported = models.Beperkingcode.objects.all()
        self.assertEqual(len(imported), 20)

        a = models.Beperkingcode.objects.get(pk='VI')
        self.assertEqual(a.omschrijving, 'Aanwijzing van gronden, Wet Voorkeursrecht gemeenten')


class ImportWkpbBroncode(TaskTestCase):
    def task(self):
        return batch.ImportWkpbBroncodeTask(BEPERKINGEN)

    def test_import(self):
        self.run_task()

        imported = models.Broncode.objects.all()
        self.assertEqual(len(imported), 6)

        a = models.Broncode.objects.get(pk='5')
        self.assertEqual(a.omschrijving, 'Dagelijks Bestuur')


class ImportWkpbBrondocument(TaskTestCase):
    def requires(self):
        return [
            batch.ImportWkpbBroncodeTask(BEPERKINGEN),
            batch.ImportBeperkingcodeTask(BEPERKINGEN),
            batch.ImportBeperkingTask(BEPERKINGEN),
        ]

    def task(self):
        return batch.ImportWkpbBrondocumentTask(BEPERKINGEN)

    def test_import(self):
        self.run_task()

        imported = models.Brondocument.objects.all()
        self.assertEqual(len(imported), 48)

        a = models.Brondocument.objects.get(pk=6641)
        self.assertEqual(a.inschrijfnummer, 6641)
        self.assertEqual(a.documentnaam, 'BD00000149_WK00WK.pdf')
        self.assertEqual(a.bron.omschrijving, 'Burgemeester')
        self.assertEqual(a.persoonsgegevens_afschermen, False)
        self.assertEqual(a.beperking.id, 1006943)


class ImportBeperking(TaskTestCase):
    def requires(self):
        return [
            batch.ImportBeperkingcodeTask(BEPERKINGEN),
        ]

    def task(self):
        return batch.ImportBeperkingTask(BEPERKINGEN)

    def test_import(self):
        self.run_task()

        imported = models.Beperking.objects.all()
        self.assertEqual(len(imported), 50)

        b = models.Beperking.objects.get(pk=1001730)
        self.assertEqual(b.inschrijfnummer, 1156)
        self.assertEqual(b.beperkingtype.omschrijving, 'Melding, bevel, beschikking of vordering Wet bodembescherming')
        self.assertEqual(b.datum_in_werking, datetime.date(2008, 12, 17))
        self.assertEqual(b.datum_einde, None)


