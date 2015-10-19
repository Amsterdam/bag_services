import string

import factory
from factory import fuzzy
import faker

f = faker.Factory.create(locale='nl_NL')

from .. import models


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