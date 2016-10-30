from batch.test import TaskTestCase
from datasets.brk import batch, models
from datasets.brk.tests import factories


class ImportZakelijkRechtTaskTest(TaskTestCase):
    def setUp(self):
        factories.KadastraalSubjectFactory.create(
            pk='NL.KAD.Persoon.172020232'
        )
        factories.KadastraalObjectFactory.create(
            pk='NL.KAD.OnroerendeZaak.11750199770000'
        )

    def task(self):
        return batch.ImportZakelijkRechtTask("diva/brk")

    def test_import(self):
        self.run_task()

        zrt = models.ZakelijkRecht.objects.get(
            pk='NL.KAD.ZakelijkRecht.AKR1.1402794-NL.KAD.OnroerendeZaak.11750199770000-NL.KAD.Tenaamstelling.AKR1'
               '.1402794')

        self.assertEqual(zrt.zrt_id, 'NL.KAD.ZakelijkRecht.AKR1.1402794')
        self.assertEqual(zrt.aard_zakelijk_recht.code, '10')
        self.assertEqual(zrt.aard_zakelijk_recht.omschrijving,
                         'Privaatrechtelijke belemmering (als bedoeld in '
                         'artikel 5, lid 3, onder b, '
                         'Belemmeringenwet Privaatrecht)')
        self.assertEqual(zrt.aard_zakelijk_recht_akr, 'BP')

        self.assertIsNone(zrt.ontstaan_uit_id)
        self.assertIsNone(zrt.betrokken_bij_id)

        self.assertEqual(zrt.kadastraal_object_id,
                         'NL.KAD.OnroerendeZaak.11750199770000')
        self.assertEqual(zrt.kadastraal_subject_id, 'NL.KAD.Persoon.172020232')

        self.assertEqual(zrt.kadastraal_object_status, 'B')

        self.assertIsNone(zrt.app_rechtsplitstype)
        self.assertEqual(zrt.teller, 1)
        self.assertEqual(zrt.noemer, 1)
