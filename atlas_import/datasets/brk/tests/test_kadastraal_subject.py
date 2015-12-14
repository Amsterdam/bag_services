import datetime

from batch.test import TaskTestCase
from datasets.brk import batch, models


class ImportKadastraalSubjectTaskTest(TaskTestCase):

    def setUp(self):
        super().setUp()

    def task(self):
        return batch.ImportKadastraalSubjectTask("diva/brk")

    def test_import(self):
        self.run_task()

        np = models.KadastraalSubject.objects.get(pk='NL.KAD.Persoon.171335763')
        self.assertEqual(np.type, models.KadastraalSubject.SUBJECT_TYPE_NATUURLIJK)
        self.assertIsNone(np.beschikkingsbevoegdheid)
        self.assertIsNone(np.bsn)
        self.assertEqual(np.voornamen, "Jan")
        self.assertEqual(np.voorvoegsels, "")
        self.assertEqual(np.naam, "Sterenborg")
        self.assertEqual(np.geslacht.code, "M")
        self.assertEqual(np.geslacht.omschrijving, "Man")
        self.assertEqual(np.aanduiding_naam.code, "E")
        self.assertEqual(np.aanduiding_naam.omschrijving, "Eigen geslachtsnaam")
        self.assertEqual(np.geboortedatum, "1940-11-05")
        self.assertEqual(np.geboorteplaats, "AMSTERDAM")
        self.assertIsNone(np.geboorteland)
        self.assertEqual(np.overlijdensdatum, "")
        self.assertEqual(np.partner_voornamen, "")
        self.assertEqual(np.partner_voorvoegsels, "")
        self.assertEqual(np.partner_naam, "")
        self.assertIsNone(np.land_waarnaar_vertrokken)
        self.assertIsNone(np.rsin)
        self.assertIsNone(np.kvknummer)
        self.assertIsNone(np.rechtsvorm)
        self.assertIsNone(np.statutaire_naam)
        self.assertIsNone(np.statutaire_zetel)
        self.assertEqual(np.bron, models.KadastraalSubject.BRON_REGISTRATIE)
        self.assertIsNotNone(np.woonadres)
        self.assertEquals(np.woonadres.openbareruimte_naam, "Zandpad-Driemond")
        self.assertEquals(np.woonadres.huisnummer, 82)
        self.assertEquals(np.woonadres.postcode, "1109AH")
        self.assertEquals(np.woonadres.woonplaats, "AMSTERDAM")
        self.assertIsNone(np.postadres)

        nnp = models.KadastraalSubject.objects.get(pk='NL.KAD.Persoon.398719470')
        self.assertEqual(nnp.type, models.KadastraalSubject.SUBJECT_TYPE_NIET_NATUURLIJK)
        self.assertIsNone(nnp.beschikkingsbevoegdheid)
        self.assertIsNone(nnp.bsn)
        self.assertIsNone(nnp.voornamen)
        self.assertIsNone(nnp.voorvoegsels)
        self.assertIsNone(nnp.naam)
        self.assertIsNone(nnp.geslacht)
        self.assertIsNone(nnp.aanduiding_naam)
        self.assertIsNone(nnp.geboortedatum)
        self.assertIsNone(nnp.geboorteplaats)
        self.assertIsNone(nnp.geboorteland)
        self.assertIsNone(nnp.overlijdensdatum)
        self.assertIsNone(nnp.partner_voornamen)
        self.assertIsNone(nnp.partner_voorvoegsels)
        self.assertIsNone(nnp.partner_naam)
        self.assertIsNone(nnp.land_waarnaar_vertrokken)
        self.assertEqual(nnp.rsin, "807944440")
        self.assertEqual(nnp.kvknummer, "32074966")
        self.assertEqual(nnp.rechtsvorm.code, "2")
        self.assertEqual(nnp.rechtsvorm.omschrijving, "Besloten vennootschap")
        self.assertEqual(nnp.statutaire_naam, "FTB PARTICIPATIES B.V.")
        self.assertEqual(nnp.statutaire_zetel, "MUIDEN")
        self.assertEqual(nnp.bron, models.KadastraalSubject.BRON_REGISTRATIE)
        self.assertEquals(nnp.woonadres.openbareruimte_naam, "Leeuwenveldseweg")
        self.assertEquals(nnp.woonadres.huisnummer, 16)
        self.assertEquals(nnp.woonadres.toevoeging, "A")
        self.assertEquals(nnp.woonadres.postcode, "1382LX")
        self.assertEqual(nnp.woonadres.woonplaats, "WEESP")

