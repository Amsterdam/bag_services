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

    def test_import_twice(self):
        source = 'atlas_jobs/fixtures/examplebag/BRN_20071001_J_20000101_20050101.UVA2'
        task = jobs.ImportBrnTask(source)
        task.execute()
        task.execute()

        imported = models.Bron.objects.all()
        self.assertEqual(len(imported), 96)


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
        jobs.ImportGmeTask('atlas_jobs/fixtures/examplebag/GME_20071001_J_20000101_20050101.UVA2').execute()

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
        self.assertEquals(s.gemeente.id, '3630000000000')


class ImportBrtTest(TestCase):
    def test_import(self):
        jobs.ImportGmeTask('atlas_jobs/fixtures/examplebag/GME_20071001_J_20000101_20050101.UVA2').execute()
        jobs.ImportSdlTask('atlas_jobs/fixtures/examplebag/SDL_20071001_J_20000101_20050101.UVA2').execute()

        source = 'atlas_jobs/fixtures/examplebag/BRT_20071001_J_20000101_20050101.UVA2'
        task = jobs.ImportBrtTask(source)
        task.execute()

        imported = models.Buurt.objects.all()
        self.assertEqual(len(imported), 64)

        b = models.Buurt.objects.get(pk='3630001910451')

        self.assertEquals(b.id, '3630001910451')
        self.assertEquals(b.code, '870')
        self.assertEquals(b.naam, 'Westlandgracht (870)')
        self.assertEquals(b.vervallen, True)
        self.assertEquals(b.stadsdeel.id, '3630001910418')


class ImportLigTest(TestCase):
    def test_import(self):
        jobs.ImportBrnTask('atlas_jobs/fixtures/examplebag/BRN_20071001_J_20000101_20050101.UVA2').execute()
        jobs.ImportStsTask('atlas_jobs/fixtures/examplebag/STS_20071001_J_20000101_20050101.UVA2').execute()

        jobs.ImportGmeTask('atlas_jobs/fixtures/examplebag/GME_20071001_J_20000101_20050101.UVA2').execute()
        jobs.ImportSdlTask('atlas_jobs/fixtures/examplebag/SDL_20071001_J_20000101_20050101.UVA2').execute()
        jobs.ImportBrtTask('atlas_jobs/fixtures/examplebag/BRT_20071001_J_20000101_20050101.UVA2').execute()

        source = 'atlas_jobs/fixtures/examplebag/LIG_20071001_J_20000101_20050101.UVA2'
        task = jobs.ImportLigTask(source)
        task.execute()

        imported = models.Ligplaats.objects.all()
        self.assertEqual(len(imported), 62)

        l = models.Ligplaats.objects.get(pk='3630000956442')
        self.assertEquals(l.identificatie, 3630000956442)
        self.assertEquals(l.ligplaats_nummer, 462020)
        self.assertEquals(l.vervallen, False)
        self.assertEquals(l.bron.code, '4')
        self.assertEquals(l.status, None)
        # self.assertEquals(l.buurt.id, '3630001910926')
