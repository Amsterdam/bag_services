import datetime

from django.test import TestCase

from .. import models, batch
from batch.test import TaskTestCase

KAD_LKI = 'diva/kadaster/lki'
KAD_AKR = 'diva/kadaster/akr'


# Kadaster

class ImportGemeente(TaskTestCase):
    def test_import(self):
        self.run_task()

        g = models.Gemeente.objects.get(pk=3630010602635)
        self.assertEqual(g.gemeentenaam, 'AMSTERDAM')
        self.assertEqual(g.gemeentecode, 363)
        self.assertEqual(g.geometrie.area, 219491741.99025947)

    def task(self):
        return batch.ImportGemeenteTask(KAD_LKI)


class ImportKadastraleGemeente(TaskTestCase):
    def task(self):
        return batch.ImportKadastraleGemeenteTask(KAD_LKI)

    def test_import(self):
        self.run_task()

        g = models.KadastraleGemeente.objects.get(pk=3630010602590)
        self.assertEqual(g.code, 'ASD06')
        self.assertEqual(g.ingang_cyclus, datetime.date(2008, 12, 2))
        self.assertEqual(g.geometrie.area, 1278700.9685260097)


class ImportSectie(TaskTestCase):
    def task(self):
        return batch.ImportSectieTask(KAD_LKI)

    def test_import(self):
        self.run_task()

        s = models.Sectie.objects.get(pk=3630010602661)
        self.assertEqual(s.kadastrale_gemeente_code, 'RDP00')
        self.assertEqual(s.code, 'C')
        self.assertEqual(s.ingang_cyclus, datetime.date(2008, 12, 2))
        self.assertEqual(s.geometrie.area, 869579.8324124987)


class ImportKadastraalObject(TaskTestCase):
    def task(self):
        return batch.ImportKadastraalObjectTask(KAD_LKI)

    def test_import(self):
        self.run_task()

        o = models.KadastraalObject.objects.get(pk=3630010603206)
        self.assertEqual(o.kadastrale_gemeente_code, 'STN02')
        self.assertEqual(o.sectie_code, 'G')
        self.assertEqual(o.perceelnummer, 1478)
        self.assertEqual(o.indexletter, 'G')
        self.assertEqual(o.indexnummer, 0)
        self.assertEqual(o.oppervlakte, 76)
        self.assertEqual(o.ingang_cyclus, datetime.date(2015, 2, 10))
        self.assertEqual(o.aanduiding, 'STN02G01478G0000')
        self.assertEqual(o.geometrie.area, 78.42037450020632)
