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

        kot = models.KadastraalObject.objects.get(pk='274434')

        self.assertIsNotNone(kot)
        self.assertEqual(kot.gemeentecode_domein, "ASD25")
        self.assertEqual(kot.sectie, "AD")
        self.assertEqual(kot.perceelnummer, 412)
        self.assertEqual(kot.objectindex_letter, "G")
        self.assertEqual(kot.objectindex_nummer, 0)
        self.assertEqual(kot.grootte, 11350)
        self.assertEqual(kot.grootte_geschat, False)
        self.assertEqual(kot.cultuur_tekst, '')
        self.assertEqual(kot.soort_cultuur_onbebouwd_domein.code, 57)
        self.assertEqual(kot.soort_cultuur_onbebouwd_domein.omschrijving, "ERF EN TUIN")
        self.assertEqual(kot.meer_culturen_onbebouwd, True)
        self.assertEqual(kot.bebouwingscode_domein.code, 2)
        self.assertEqual(kot.bebouwingscode_domein.omschrijving, "ONBEBOUWD MET BEBOUWD")
        self.assertEqual(kot.kaartblad, 30)
        self.assertEqual(kot.ruitletter, "D")
        self.assertEqual(kot.ruitnummer, 5)
        self.assertEqual(kot.omschrijving_deelperceel, '')



