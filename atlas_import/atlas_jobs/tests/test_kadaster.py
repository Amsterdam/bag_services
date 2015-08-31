import datetime

from django.test import TestCase

from atlas import models
from atlas_jobs.batch import kadaster

KAD_LKI = 'atlas_jobs/fixtures/testset/kadaster/lki'
KAD_AKR = 'atlas_jobs/fixtures/testset/kadaster/akr'


# Kadaster

class ImportLkiGemeente(TestCase):
    def test_import(self):
        task = kadaster.ImportLkiGemeenteTask(KAD_LKI)
        task.execute()

        g = models.LkiGemeente.objects.get(pk=3630010602635)
        self.assertEqual(g.gemeentenaam, 'AMSTERDAM')
        self.assertEqual(g.gemeentecode, 363)
        self.assertEqual(g.geometrie.area, 219491741.99025947)


class ImportLkiKadastraleGemeente(TestCase):
    def test_import(self):
        task = kadaster.ImportLkiKadastraleGemeenteTask(KAD_LKI)
        task.execute()

        g = models.LkiKadastraleGemeente.objects.get(pk=3630010602590)
        self.assertEqual(g.code, 'ASD06')
        self.assertEqual(g.ingang_cyclus, datetime.date(2008, 12, 2))
        self.assertEqual(g.geometrie.area, 1278700.9685260097)


class ImportLkiSectie(TestCase):
    def test_import(self):
        task = kadaster.ImportLkiSectieTask(KAD_LKI)
        task.execute()

        s = models.LkiSectie.objects.get(pk=3630010602661)
        self.assertEqual(s.kadastrale_gemeente_code, 'RDP00')
        self.assertEqual(s.code, 'C')
        self.assertEqual(s.ingang_cyclus, datetime.date(2008, 12, 2))
        self.assertEqual(s.geometrie.area, 869579.8324124987)


class ImportLkiKadastraalObject(TestCase):
    def test_import(self):
        task = kadaster.ImportLkiKadastraalObjectTask(KAD_LKI)
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
