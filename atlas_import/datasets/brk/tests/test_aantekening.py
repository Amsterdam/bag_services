from batch.test import TaskTestCase
from datasets.brk.tests import factories
from datasets.brk import models, batch


class ImportAantekeningTaskTest(TaskTestCase):

    def setUp(self):
        super().setUp()
        factories.KadastraalObjectFactory.create(
            pk='NL.KAD.OnroerendeZaak.14070185210026'
        )
        factories.KadastraalObjectFactory.create(
            pk='NL.KAD.OnroerendeZaak.25420017370000'
        )
        factories.KadastraalSubjectFactory.create(
            pk='NL.KAD.Persoon.146152266'
        )
        factories.ZakelijkRechtFactory.create(
            pk='NL.KAD.Tenaamstelling.AKR1.5913592'
        )

    def task(self):
        return batch.ImportAantekeningTask("diva/brk")

    def test_import(self):
        self.run_task()

        atk = models.Aantekening.objects.get(pk='NL.KAD.Aantekening.AKR1.100000007082195')
        self.assertEqual(atk.aard_aantekening.code, '71')
        self.assertEqual(atk.aard_aantekening.omschrijving, 'Locatiegegevens ontleend aan Basisregistraties Adressen en Gebouwen')
        self.assertEqual(atk.omschrijving, '')

        # self.assertEqual(atk.kadastraal_object.id, 'NL.KAD.OnroerendeZaak.14070185210026')
        # self.assertIsNone(atk.zekerheidsrecht)
        # self.assertIsNone(atk.kadastraal_subject)
        #
        # atk = models.Aantekening.objects.get(pk='NL.KAD.Aantekening.AKR2.4624349')
        #
        # self.assertEqual(atk.aard_aantekening.code, '39')
        # self.assertEqual(atk.aard_aantekening.omschrijving, 'Raadpleeg brondocument')
        # self.assertEqual(atk.omschrijving, 'VERKREGEN TEN BEHOEVE VAN MAATSCHAP                           '
        #                                    'OORSPRONKELIJK GEVESTIGD BIJ: 4       0   0')
        #
        # self.assertEqual(atk.kadastraal_object.id, 'NL.KAD.OnroerendeZaak.25420017370000')
        # self.assertIsNone(atk.zekerheidsrecht.id, 'NL.KAD.Tenaamstelling.AKR1.5913592')
        # self.assertIsNone(atk.kadastraal_subject.id, 'NL.KAD.Persoon.146152266')

