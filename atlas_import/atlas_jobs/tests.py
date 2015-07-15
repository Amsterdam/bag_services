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