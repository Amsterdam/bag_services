
# Packages
from elasticsearch import Elasticsearch

# Project
from batch import batch
from django.conf import settings

import datasets.bag.batch
from datasets.bag.tests import factories as bag_factories
import datasets.brk.batch
from datasets.brk.tests import factories as brk_factories


def load_docs(cls):

    bag_factories.StadsdeelFactory(
        id='test_query',
        naam='Centrum')

    cls.prinsengracht = bag_factories.OpenbareRuimteFactory.create(
        naam="Prinsengracht", type='02', landelijk_id='0363300000004580')

    # Create brug objects
    bag_factories.OpenbareRuimteFactory.create(
        naam="Korte Brug", type='05')

    bag_factories.OpenbareRuimteFactory.create(
        naam="Brugover", type='05')

    bag_factories.OpenbareRuimteFactory.create(
        naam="Brughuis", type='05')

    # Special chars
    bag_factories.OpenbareRuimteFactory.create(
        naam="Laing's Nekstraat", type='01', landelijk_id='0363300000004117')

    anjeliersstraat = bag_factories.OpenbareRuimteFactory.create(
        naam="Anjeliersstraat", type='01')

    cls.na = bag_factories.NummeraanduidingFactory.create(
        openbare_ruimte=anjeliersstraat, huisnummer=11, huisletter='A',
        type='01',
        landelijk_id='5432109876543210',
        postcode=1001)

    bag_factories.NummeraanduidingFactory.create(
        openbare_ruimte=anjeliersstraat, huisnummer=11,
        huisletter='B', type='01',
        postcode=1001)

    bag_factories.NummeraanduidingFactory.create(
        openbare_ruimte=anjeliersstraat, huisnummer=11, huisletter='C',
        type='01',
        postcode=1001)

    bag_factories.NummeraanduidingFactory.create(
        postcode=1001,
        type='01',
        openbare_ruimte=anjeliersstraat, huisnummer=12)

    # Maak een woonboot
    kade_ruimte = bag_factories.OpenbareRuimteFactory.create(
        type='01',
        naam="Ligplaatsenstraat")

    bag_factories.NummeraanduidingFactory.create(
        type='05',
        postcode='9999ZZ',
        openbare_ruimte=kade_ruimte, huisnummer=33, type_adres='Hoofdadres')

    # marnixkade
    marnix_kade = bag_factories.OpenbareRuimteFactory.create(
        naam="Marnixkade")

    bag_factories.NummeraanduidingFactory.create(
        openbare_ruimte=marnix_kade, huisnummer=36, huisletter='F',
        type_adres='Hoofdadres', postcode='1015XR')

    rozenstraat = bag_factories.OpenbareRuimteFactory.create(
        naam="Rozenstraat", landelijk_id="0363300000004425")

    bag_factories.NummeraanduidingFactory.create(
        openbare_ruimte=rozenstraat, huisnummer=228, huisletter='a',
        type_adres='Hoofdadres', postcode='1016SZ', huisnummer_toevoeging='1')

    bag_factories.NummeraanduidingFactory.create(
        openbare_ruimte=rozenstraat, huisnummer=228, huisletter='b',
        type_adres='Hoofdadres', postcode='1016SZ', huisnummer_toevoeging='1', landelijk_id="0363200000425129")

    bag_factories.NummeraanduidingFactory.create(
        openbare_ruimte=rozenstraat, huisnummer=229,
        type_adres='Hoofdadres', postcode='1016SZ', huisnummer_toevoeging='1', landelijk_id="0363200000425130")

    bag_factories.NummeraanduidingFactory.create(
        openbare_ruimte=rozenstraat, huisnummer=229,
        type_adres='Hoofdadres', postcode='1016SZ', huisnummer_toevoeging='2', landelijk_id="0363200000425131")

    bag_factories.NummeraanduidingFactory.create(
        openbare_ruimte=rozenstraat, huisnummer=229,
        type_adres='Hoofdadres', postcode='1016SZ', huisnummer_toevoeging='3', landelijk_id="0363200000425132")

    bag_factories.NummeraanduidingFactory.create(
        openbare_ruimte=rozenstraat, huisnummer=229,
        type_adres='Hoofdadres', postcode='1016SZ', huisnummer_toevoeging='4', landelijk_id="0363200000425133")

    bag_factories.BouwblokFactory.create(code='RN35')
    bag_factories.BouwblokFactory.create(code='AB01')

    adres = brk_factories.AdresFactory(
        huisnummer=340,
        huisletter='A',
        postcode='1234AB',
        woonplaats='FabeltjesLand',
        openbareruimte_naam='Sesamstraat')

    brk_factories.NatuurlijkPersoonFactory(
        naam='Kikker',
        voorvoegsels='de',
        voornamen='Kermet',
        woonadres=adres
    )

    cls.pand1 = bag_factories.PandFactory.create(landelijk_id="0363100012062184")

    batch.execute(datasets.bag.batch.DeleteIndexBagJob())
    batch.execute(datasets.bag.batch.DeleteIndexGebiedJob())
    batch.execute(datasets.bag.batch.DeleteIndexPandJob())
    batch.execute(datasets.brk.batch.DeleteIndexKadasterJob())

    batch.execute(datasets.bag.batch.IndexBagJob())
    batch.execute(datasets.bag.batch.IndexGebiedenJob())
    batch.execute(datasets.bag.batch.IndexPandJob())
    batch.execute(datasets.brk.batch.IndexKadasterJob())

    es = Elasticsearch(hosts=settings.ELASTIC_SEARCH_HOSTS)
    es.indices.refresh(index="_all")


