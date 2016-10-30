from batch.test import TaskTestCase
from datasets.brk import batch
from datasets.brk.tests import factories


class ImportKadastraalObjectRelatiesTaskTest(TaskTestCase):
    def setUp(self):
        self.a1 = factories.KadastraalObjectFactory.create(indexletter='A')
        self.g1 = factories.KadastraalObjectFactory.create(indexletter='G')
        s1 = factories.KadastraalSubjectFactory.create()

        self.a2 = factories.KadastraalObjectFactory.create(indexletter='A')
        self.a3 = factories.KadastraalObjectFactory.create(indexletter='A')
        self.g2 = factories.KadastraalObjectFactory.create(indexletter='G')
        s2 = factories.KadastraalSubjectFactory.create()

        factories.ZakelijkRechtFactory.create(
                kadastraal_object=self.g1,
                betrokken_bij=s1,
        )
        factories.ZakelijkRechtFactory.create(
                kadastraal_object=self.a1,
                ontstaan_uit=s1,
        )
        factories.ZakelijkRechtFactory.create(
                kadastraal_object=self.g2,
                betrokken_bij=s2,
        )
        factories.ZakelijkRechtFactory.create(
                kadastraal_object=self.a2,
                ontstaan_uit=s2,
        )
        factories.ZakelijkRechtFactory.create(
                kadastraal_object=self.a3,
                ontstaan_uit=s2,
        )

    def task(self):
        return batch.ImportKadastraalObjectRelatiesTask()

    def test_import(self):
        self.run_task()

        self.a1.refresh_from_db()
        self.a2.refresh_from_db()
        self.a3.refresh_from_db()
        self.g1.refresh_from_db()
        self.g2.refresh_from_db()

        def get_aanduiding(obj):
            return obj.aanduiding

        self.assertQuerysetEqual(
            self.a1.g_percelen.all(), [self.g1.aanduiding], get_aanduiding)
        self.assertQuerysetEqual(
            self.a2.g_percelen.all(), [self.g2.aanduiding], get_aanduiding)

        g2_a = set([obj.aanduiding for obj in self.g2.a_percelen.all()])

        self.assertEqual(g2_a, {self.a2.aanduiding, self.a3.aanduiding})
