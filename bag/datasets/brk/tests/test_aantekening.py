from batch.test import TaskTestCase
from datasets.brk.tests import factories
from datasets.brk import models, batch


class ImportAantekeningTaskTest(TaskTestCase):

    def setUp(self):
        super().setUp()

        [factories.KadastraalObjectFactory.create(pk=kot) for kot in [
            'NL.KAD.OnroerendeZaak.14070185210026',
            'NL.KAD.OnroerendeZaak.25420017370000',
            'NL.KAD.OnroerendeZaak.14601211270000',
        ]]

        [factories.KadastraalSubjectFactory.create(pk=kst) for kst in [
            'NL.KAD.Persoon.146152266',
            'NL.KAD.Persoon.172174522',
        ]]

        factories.ZakelijkRechtFactory.create(
            pk='NL.KAD.Tenaamstelling.AKR1.5913592'
        )

    def task(self):
        return batch.ImportAantekeningTask("gob/brk")

    def test_import(self):
        self.run_task()

        atk = models.Aantekening.objects.get(aantekening_id='NL.KAD.Aantekening.AKR1.100000007082195')
        self.assertEqual(atk.aard_aantekening.code, '71')
        self.assertEqual(
            atk.aard_aantekening.omschrijving, 'Locatiegegevens ontleend aan Basisregistraties Adressen en Gebouwen')
        self.assertEqual(atk.omschrijving, '')

        self.assertEqual(atk.kadastraal_object.id, 'NL.KAD.OnroerendeZaak.14070185210026')
        self.assertIsNone(atk.opgelegd_door)

        try:
            atk = models.Aantekening.objects.get(aantekening_id='NL.KAD.Aantekening.AKR2.4624349')
            self.fail("Aantekening should not exist: " + atk.id)
        except models.Aantekening.DoesNotExist:
            pass

        atk = models.Aantekening.objects.get(aantekening_id='NL.KAD.Aantekening.AKR1.413201')
        self.assertEqual(atk.opgelegd_door_id, 'NL.KAD.Persoon.172174522')
