from datetime import date

import factory
from factory import fuzzy
import faker

f = faker.Factory.create(locale='nl_NL')

from .. import models
from datasets.lki.tests import factories as lki_factories
from datasets.akr.tests import factories as akr_factories


class BeperkingCodeFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.Beperkingcode


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
    kadastraal_object = factory.SubFactory(lki_factories.KadastraalObjectFactory)
    kadastraal_object_akr = factory.SubFactory(akr_factories.KadastraalObjectFactory)