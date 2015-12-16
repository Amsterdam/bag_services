import datetime

from batch.test import TaskTestCase
from datasets.brk import batch, models
from datasets.brk.tests import factories


class ImportKadastraalObjectTaskTest(TaskTestCase):
    def setUp(self):
        factories.KadastraleSectieFactory.create(
            sectie='A',
            kadastrale_gemeente=factories.KadastraleGemeenteFactory.create(
                pk="AMR03",
            ),
        )

        factories.NatuurlijkPersoonFactory.create(
            pk='NL.KAD.Persoon.170361583'
        )

    def task(self):
        return batch.ImportKadastraalObjectTask("diva/brk")

    def test_import(self):
        self.run_task()

        kot = models.KadastraalObject.objects.get(pk='NL.KAD.OnroerendeZaak.11280310370000')

        self.assertEqual(kot.id, 'NL.KAD.OnroerendeZaak.11280310370000')
        self.assertEqual(kot.aanduiding, 'AMR03A03103G0000')
        self.assertEqual(kot.kadastrale_gemeente.id, 'AMR03')
        self.assertEqual(kot.sectie.sectie, 'A')
        self.assertEqual(kot.perceelnummer, 3103)
        self.assertEqual(kot.index_letter, 'G')
        self.assertEqual(kot.index_nummer, 0)
        self.assertEqual(kot.soort_grootte.code, '1')
        self.assertEqual(kot.soort_grootte.omschrijving, 'Vastgesteld')
        self.assertEqual(kot.grootte, 99)
        self.assertEqual(kot.g_percelen.count(), 0)
        self.assertEqual(kot.koopsom, 290419)
        self.assertEqual(kot.koopsom_valuta_code, 'EUR')
        self.assertEqual(kot.koopjaar, '1998')
        self.assertEqual(kot.meer_objecten, True)
        self.assertEqual(kot.cultuurcode_onbebouwd.code, '57')
        self.assertEqual(kot.cultuurcode_onbebouwd.omschrijving, 'Erf - Tuin')
        self.assertIsNone(kot.cultuurcode_bebouwd)

        self.assertEqual(kot.register9_tekst, '')
        self.assertEqual(kot.status_code, 'B')
        self.assertEqual(kot.toestandsdatum, datetime.date(2012, 12, 31))
        self.assertFalse(kot.voorlopige_kadastrale_grens)
        self.assertEqual(kot.in_onderzoek, '')

        self.assertIsNotNone(kot.geometrie)
        self.assertEqual(kot.voornaamste_gerechtigde.id, 'NL.KAD.Persoon.170361583')

        # kot = models.KadastraalObject.objects.get(pk='NL.KAD.OnroerendeZaak.11280351910001')
        # self.assertIsNotNone(kot.g_perceel)
        # self.assertEqual(kot.g_perceel_id, 'NL.KAD.OnroerendeZaak.11280292370000')
