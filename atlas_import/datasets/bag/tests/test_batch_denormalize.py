from django.test import TransactionTestCase

from datasets.bag import batch, models
from datasets.bag.tests import factories


class DenormalizeDataTaskTest(TransactionTestCase):
    def setUp(self):
        super().setUp()

        self.opr_1 = factories.OpenbareRuimteFactory.create()
        self.opr_2 = factories.OpenbareRuimteFactory.create()

        self.vbo_1 = factories.VerblijfsobjectFactory.create()
        self.vbo_2 = factories.VerblijfsobjectFactory.create()

        self.num_vbo_1_nvn = factories.NummeraanduidingFactory.create(openbare_ruimte=self.opr_1, hoofdadres=False,
                                                                      verblijfsobject=self.vbo_1, )
        self.num_vbo_1_hfd = factories.NummeraanduidingFactory.create(openbare_ruimte=self.opr_1, hoofdadres=True,
                                                                      verblijfsobject=self.vbo_1, )
        self.num_vbo_2_hfd = factories.NummeraanduidingFactory.create(openbare_ruimte=self.opr_2, hoofdadres=True,
                                                                      verblijfsobject=self.vbo_2, )

        self.lig_1 = factories.LigplaatsFactory.create()
        self.lig_2 = factories.LigplaatsFactory.create()

        self.num_lig_1_nvn = factories.NummeraanduidingFactory.create(openbare_ruimte=self.opr_1, hoofdadres=False,
                                                                      ligplaats=self.lig_1, )
        self.num_lig_1_hfd = factories.NummeraanduidingFactory.create(openbare_ruimte=self.opr_1, hoofdadres=True,
                                                                      ligplaats=self.lig_1, )
        self.num_lig_2 = factories.NummeraanduidingFactory.create(openbare_ruimte=self.opr_2, hoofdadres=True,
                                                                  ligplaats=self.lig_2, )

        self.sta_1 = factories.StandplaatsFactory.create()
        self.sta_2 = factories.StandplaatsFactory.create()

        self.num_sta_1_nvn = factories.NummeraanduidingFactory.create(openbare_ruimte=self.opr_1, hoofdadres=False,
                                                                      standplaats=self.sta_1, )
        self.num_sta_1_hfd = factories.NummeraanduidingFactory.create(openbare_ruimte=self.opr_1, hoofdadres=True,
                                                                      standplaats=self.sta_1, )
        self.num_sta_2 = factories.NummeraanduidingFactory.create(openbare_ruimte=self.opr_2, hoofdadres=True,
                                                                  standplaats=self.sta_2, )

    def test_normalize_vbo(self):
        batch.DenormalizeDataTask().execute()

        vbo_1 = models.Verblijfsobject.objects.get(pk=self.vbo_1.pk)
        vbo_2 = models.Verblijfsobject.objects.get(pk=self.vbo_2.pk)

        self.assertEqual(vbo_1._openbare_ruimte_naam, self.opr_1.naam)
        self.assertEqual(vbo_2._openbare_ruimte_naam, self.opr_2.naam)

        self.assertEqual(vbo_1._huisnummer, self.num_vbo_1_hfd.huisnummer)
        self.assertEqual(vbo_1._huisletter, self.num_vbo_1_hfd.huisletter)
        self.assertEqual(vbo_1._huisnummer_toevoeging, self.num_vbo_1_hfd.huisnummer_toevoeging)

        self.assertEqual(vbo_2._huisnummer, self.num_vbo_2_hfd.huisnummer)

    def test_normalize_lig(self):
        batch.DenormalizeDataTask().execute()

        lig_1 = models.Ligplaats.objects.get(pk=self.lig_1.pk)
        lig_2 = models.Ligplaats.objects.get(pk=self.lig_2.pk)

        self.assertEqual(lig_1._openbare_ruimte_naam, self.opr_1.naam)
        self.assertEqual(lig_2._openbare_ruimte_naam, self.opr_2.naam)

        self.assertEqual(lig_1._huisnummer, self.num_lig_1_hfd.huisnummer)
        self.assertEqual(lig_1._huisletter, self.num_lig_1_hfd.huisletter)
        self.assertEqual(lig_1._huisnummer_toevoeging, self.num_lig_1_hfd.huisnummer_toevoeging)

        self.assertEqual(lig_2._huisnummer, self.num_lig_2.huisnummer)

    def test_normalize_sta(self):
        batch.DenormalizeDataTask().execute()

        sta_1 = models.Standplaats.objects.get(pk=self.sta_1.pk)
        sta_2 = models.Standplaats.objects.get(pk=self.sta_2.pk)

        self.assertEqual(sta_1._openbare_ruimte_naam, self.opr_1.naam)
        self.assertEqual(sta_2._openbare_ruimte_naam, self.opr_2.naam)

        self.assertEqual(sta_1._huisnummer, self.num_sta_1_hfd.huisnummer)
        self.assertEqual(sta_1._huisletter, self.num_sta_1_hfd.huisletter)
        self.assertEqual(sta_1._huisnummer_toevoeging, self.num_sta_1_hfd.huisnummer_toevoeging)

        self.assertEqual(sta_2._huisnummer, self.num_sta_2.huisnummer)
