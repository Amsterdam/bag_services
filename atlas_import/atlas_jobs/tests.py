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
        self.assertTrue(g.verzorgingsgebied)
        self.assertFalse(g.vervallen)


class ImportSdlTest(TestCase):

    def test_import(self):
        g = models.Gemeente.objects.create(pk='3630000000000', naam='Amsterdam', code='0363')

        source = 'atlas_jobs/fixtures/examplebag/SDL_20071001_J_20000101_20050101.UVA2'
        task = jobs.ImportSdlTask(source)
        task.execute()

        imported = models.Stadsdeel.objects.all()
        self.assertEqual(len(imported), 15)

        s = models.Stadsdeel.objects.get(pk='3630001910428')

        self.assertEquals(s.id, '3630001910428')
        self.assertEquals(s.code, 'V')
        self.assertEquals(s.naam, 'Oud-Zuid (V)')
        self.assertEquals(s.vervallen, False)
        self.assertEquals(s.gemeente, g)