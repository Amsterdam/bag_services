import string

import factory
from factory import fuzzy
import faker

from .. import models

f = faker.Factory.create(locale='nl_NL')


class LigplaatsFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.Ligplaats

    id = fuzzy.FuzzyText(length=14, chars=string.digits)
    identificatie = fuzzy.FuzzyText(length=14, chars=string.digits)


class StandplaatsFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.Standplaats

    id = fuzzy.FuzzyText(length=14, chars=string.digits)
    identificatie = fuzzy.FuzzyText(length=14, chars=string.digits)


class VerblijfsobjectFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.Verblijfsobject

    id = fuzzy.FuzzyText(length=14, chars=string.digits)
    identificatie = fuzzy.FuzzyText(length=14, chars=string.digits)


class PandFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.Pand

    id = fuzzy.FuzzyText(length=14, chars=string.digits)


class GemeenteFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.Gemeente

    id = fuzzy.FuzzyText(length=14, chars=string.digits)
    code = fuzzy.FuzzyText(length=4, chars=string.digits)


class WoonplaatsFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.Woonplaats

    id = fuzzy.FuzzyText(length=14, chars=string.digits)
    code = fuzzy.FuzzyText(length=4, chars=string.digits)
    gemeente = factory.SubFactory(GemeenteFactory)


class OpenbareRuimteFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.OpenbareRuimte

    id = fuzzy.FuzzyText(length=14, chars=string.digits)
    code = fuzzy.FuzzyText(length=5, chars=string.digits)
    woonplaats = factory.SubFactory(WoonplaatsFactory)
    naam = factory.LazyAttribute(lambda o: f.street_name())


class NummeraanduidingFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.Nummeraanduiding

    id = fuzzy.FuzzyText(length=14, chars=string.digits)
    code = fuzzy.FuzzyText(length=14, chars=string.digits)
    huisnummer = factory.LazyAttribute(lambda o: f.building_number())
    openbare_ruimte = factory.SubFactory(OpenbareRuimteFactory)
    verblijfsobject = factory.SubFactory(VerblijfsobjectFactory)


class StadsdeelFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.Stadsdeel

    id = fuzzy.FuzzyText(length=14, chars=string.digits)
    code = fuzzy.FuzzyText(length=3, chars=string.digits)
    gemeente = factory.SubFactory(GemeenteFactory)


class BuurtFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.Buurt

    id = fuzzy.FuzzyText(length=14, chars=string.digits)
    code = fuzzy.FuzzyText(length=3, chars=string.digits)
    stadsdeel = factory.SubFactory(StadsdeelFactory)


class BouwblokFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.Bouwblok

    id = fuzzy.FuzzyText(length=14, chars=string.digits)
    code = fuzzy.FuzzyText(length=4, chars=string.digits)
    buurt = factory.SubFactory(BuurtFactory)
