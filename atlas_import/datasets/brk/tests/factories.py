import factory
from django.contrib.gis.geos import MultiPolygon, Polygon
from factory import fuzzy
import faker

from .. import models
from datasets.generic import kadaster


f = faker.Factory.create(locale='nl_NL')


def random_poly():
    return MultiPolygon(Polygon(((0.0, 0.0), (0.0, 50.0), (50.0, 50.0), (50.0, 0.0), (0.0, 0.0))))


class GemeenteFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.Gemeente

    gemeente = factory.LazyAttribute(lambda o: f.city())
    geometrie = random_poly()


class KadastraleGemeenteFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.KadastraleGemeente

    pk = fuzzy.FuzzyText(length=5)
    gemeente = factory.SubFactory(GemeenteFactory)
    geometrie = random_poly()

