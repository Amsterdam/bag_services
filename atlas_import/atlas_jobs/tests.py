import datetime
from django.test import TestCase

# Create your tests here.
from atlas_jobs import jobs
from atlas import models


class ImportBrnTest(TestCase):

    def test_import(self):
        source = 'atlas_jobs/fixtures/examplebag/BRN_20071001_J_20000101_20050101.UVA2'
        task = jobs.ImportBrnTask(source)
        task.execute()

        imported = models.Bron.objects.all()
        self.assertEqual(len(imported), 96)

        self.assertIsNotNone(models.Bron.objects.get(pk='PST'))

        b = models.Bron.objects.get(pk='13')
        self.assertEqual(b.omschrijving, 'Stadsdeel Zuideramstel (13)')


class ImportStsTest(TestCase):

    def test_import(self):
        source = 'atlas_jobs/fixtures/examplebag/STS_20071001_J_20000101_20050101.UVA2'
        task = jobs.ImportStsTask(source)
        task.execute()

        imported = models.Status.objects.all()
        self.assertEqual(len(imported), 19)

        self.assertIsNotNone(models.Status.objects.get(pk='10'))

        s = models.Status.objects.get(pk='01')
        self.assertEqual(s.omschrijving, 'Buitengebruik i.v.m. renovatie')


class ImportGmtTest(TestCase):

    def test_import(self):
        source = 'atlas_jobs/fixtures/examplebag/GME_20071001_J_20000101_20050101.UVA2'
        task = jobs.ImportGmeTask(source)
        task.execute()

        imported = models.Gemeente.objects.all()
        self.assertEqual(len(imported), 1)

        g = models.Gemeente.objects.get(pk='3630000000000')

        self.assertEquals(g.id, '3630000000000')
        self.assertEquals(g.code, '0363')
        self.assertEquals(g.naam, 'Amsterdam')
        self.assertEquals(g.gemeente_waarin_overgegaan, '')
        self.assertTrue(g.indicatie_verzorgingsgebied)
        self.assertEquals(g.mutatie_gebruiker, 'GVI')
        self.assertFalse(g.indicatie_vervallen)
        self.assertEquals(g.geldigheid_begin, datetime.date(1900, 1, 1))
        self.assertIsNone(g.geldigheid_eind)