import string

import factory
from factory import fuzzy
import faker

from .. import models
from datasets.generic import kadaster


f = faker.Factory.create(locale='nl_NL')


class AdresFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.Adres

    id = fuzzy.FuzzyText(length=32)
    straatnaam = factory.LazyAttribute(lambda a: f.street_name())


class NatuurlijkPersoonFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.KadastraalSubject

    id = fuzzy.FuzzyText(length=10, chars=string.digits)
    geslachtsnaam = factory.LazyAttribute(lambda o: f.name())
    subjectnummer = fuzzy.FuzzyInteger(low=1, high=99999)
    woonadres = factory.SubFactory(AdresFactory)
    postadres = factory.SubFactory(AdresFactory)


class NietNatuurlijkPersoonFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.KadastraalSubject

    id = fuzzy.FuzzyText(length=10, chars=string.digits)
    naam_niet_natuurlijke_persoon = factory.LazyAttribute(lambda o: f.company())
    subjectnummer = fuzzy.FuzzyInteger(low=1, high=99999)
    woonadres = factory.SubFactory(AdresFactory)
    postadres = factory.SubFactory(AdresFactory)


class TransactieFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.Transactie

    id = factory.LazyAttribute(lambda t: t.registercode)
    registercode = fuzzy.FuzzyText(chars=string.digits)


class KadastraalObjectFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.KadastraalObject

    id = factory.LazyAttribute(lambda kot: kadaster.get_aanduiding(kot.gemeentecode, kot.sectie, kot.perceelnummer,
                                                                   kot.objectindex_letter, kot.objectindex_nummer))
    gemeentecode = fuzzy.FuzzyChoice(choices=['ASD02', 'STN02'])
    sectie = fuzzy.FuzzyText(length=1, chars=string.ascii_uppercase)
    perceelnummer = fuzzy.FuzzyInteger(low=0, high=99999)
    objectindex_letter = fuzzy.FuzzyChoice(choices=['A', 'G'])
    objectindex_nummer = fuzzy.FuzzyInteger(low=0, high=9999)


class ZakelijkRechtFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.ZakelijkRecht

    id = fuzzy.FuzzyText()
    kadastraal_subject = factory.SubFactory(NatuurlijkPersoonFactory)
    kadastraal_object = factory.SubFactory(KadastraalObjectFactory)
    transactie = factory.SubFactory(TransactieFactory)