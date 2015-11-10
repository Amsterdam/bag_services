from datetime import date
import string

from django.contrib.gis import geos

import factory
from factory import fuzzy
import faker

from datasets.generic import kadaster

f = faker.Factory.create(locale='nl_NL')

from .. import models


class GemeenteFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.Gemeente

    id = fuzzy.FuzzyInteger(low=1, high=99999)
    gemeentecode = fuzzy.FuzzyInteger(low=1, high=9999)
    gemeentenaam = factory.LazyAttribute(lambda g: f.city()[:9])


class KadastraleGemeenteFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.KadastraleGemeente

    id = fuzzy.FuzzyInteger(low=1, high=99999)
    code = fuzzy.FuzzyText(length=5)
    ingang_cyclus = fuzzy.FuzzyDate(start_date=date.today())


class SectieFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.Sectie

    id = fuzzy.FuzzyInteger(low=1, high=99999)
    kadastrale_gemeente_code = fuzzy.FuzzyChoice(choices=['ASD02', 'STN02'])
    code = fuzzy.FuzzyText(length=2)
    ingang_cyclus = fuzzy.FuzzyDate(start_date=date.today())


class KadastraalObjectFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.KadastraalObject

    id = fuzzy.FuzzyInteger(low=1, high=99999)
    kadastrale_gemeente_code = fuzzy.FuzzyChoice(choices=['ASD02', 'STN02'])
    sectie_code = fuzzy.FuzzyText(length=1, chars=string.ascii_uppercase)
    perceelnummer = fuzzy.FuzzyInteger(low=0, high=99999)
    indexletter = fuzzy.FuzzyChoice(choices=['A', 'G'])
    indexnummer = fuzzy.FuzzyInteger(low=0, high=9999)
    oppervlakte = fuzzy.FuzzyInteger(low=1, high=999)
    ingang_cyclus = fuzzy.FuzzyDate(start_date=date.today())
    aanduiding = factory.LazyAttribute(
        lambda kot: kadaster.get_aanduiding(kot.kadastrale_gemeente_code, kot.sectie_code, kot.perceelnummer,
                                            kot.indexletter, kot.indexnummer))
    geometrie = factory.LazyAttribute(
        lambda kot: geos.MultiPolygon(geos.Polygon(((0.0, 0.0), (0.0, 50.0), (50.0, 50.0), (50.0, 0.0), (0.0, 0.0)))))
