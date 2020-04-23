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
        factories.KadastraleSectieFactory.create(
            sectie='X',
            kadastrale_gemeente=factories.KadastraleGemeenteFactory.create(
                pk="HLM02",
            ),
        )

        factories.NatuurlijkPersoonFactory.create(
            pk='NL.KAD.Persoon.170361583')
        factories.NatuurlijkPersoonFactory.create(
            pk='NL.KAD.Persoon.172014260')
        factories.NatuurlijkPersoonFactory.create(
            pk='NL.KAD.Persoon.199346638')

    def task(self):
        return batch.ImportKadastraalObjectTask("gob/brk")

    def test_import(self):
        self.run_task()

        kot = models.KadastraalObject.objects.get(
            pk='NL.KAD.OnroerendeZaak.11280310370000')

        self.assertEqual(kot.id, 'NL.KAD.OnroerendeZaak.11280310370000')
        self.assertEqual(kot.aanduiding, 'AMR03A03103G0000')
        self.assertEqual(kot.kadastrale_gemeente.id, 'AMR03')
        self.assertEqual(kot.sectie.sectie, 'A')
        self.assertEqual(kot.perceelnummer, 3103)
        self.assertEqual(kot.indexletter, 'G')
        self.assertEqual(kot.indexnummer, 0)
        self.assertEqual(kot.soort_grootte.code, '1')
        self.assertEqual(kot.soort_grootte.omschrijving, 'Vastgesteld')
        self.assertEqual(str(kot.grootte), "99.02")
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

        self.assertIsNone(kot.point_geom)
        self.assertIsNotNone(kot.poly_geom)
        self.assertEqual(
            kot.voornaamste_gerechtigde.id, 'NL.KAD.Persoon.170361583')

        kot = models.KadastraalObject.objects.get(
            pk='NL.KAD.OnroerendeZaak.12550132010037')
        self.assertIsNone(kot.poly_geom)
        self.assertIsNotNone(kot.point_geom)
