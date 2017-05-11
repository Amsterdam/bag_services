from datetime import date

import factory
from factory import fuzzy

import faker

from datasets.brk.tests import factories as brk_factories
from datasets.bag.tests import factories as bag_factories

from .. import models

f = faker.Factory.create(locale='nl_NL')


class BeperkingCodeFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.Beperkingcode

    code = fuzzy.FuzzyText(length=4)
    omschrijving = fuzzy.FuzzyText(length=20)


class BeperkingFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.Beperking

    id = fuzzy.FuzzyInteger(low=1, high=99999)
    inschrijfnummer = fuzzy.FuzzyInteger(low=1, high=99999)
    beperkingtype = factory.SubFactory(BeperkingCodeFactory)
    datum_in_werking = fuzzy.FuzzyDate(date.today())


class BeperkingKadastraalObjectFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.BeperkingKadastraalObject

    id = fuzzy.FuzzyText(length=33)
    beperking = factory.SubFactory(BeperkingFactory)
    kadastraal_object = factory.SubFactory(
        brk_factories.KadastraalObjectFactory)


class BeperkingVerblijfsobjectFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.BeperkingVerblijfsobject

    beperking = factory.SubFactory(BeperkingFactory)
    verblijfsobject = factory.SubFactory(bag_factories.VerblijfsobjectFactory)


class BroncodeFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.Broncode

    code = fuzzy.FuzzyText(length=4)
    omschrijving = fuzzy.FuzzyText(length=150)


class BrondocumentFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.Brondocument

    id = fuzzy.FuzzyInteger(low=1, high=99999)
    bron = factory.SubFactory(BroncodeFactory)
    inschrijfnummer = fuzzy.FuzzyInteger(low=1, high=99999)
    documentnaam = fuzzy.FuzzyText(length=21)
    persoonsgegevens_afschermen = fuzzy.FuzzyChoice([True, False])
    beperking = factory.SubFactory(BeperkingFactory)
