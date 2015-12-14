import factory
import faker
from django.contrib.gis.geos import MultiPolygon, Polygon
from factory import fuzzy

from .. import models

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


class KadastraleSectieFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.KadastraleSectie

    pk = fuzzy.FuzzyText(length=60)
    sectie = fuzzy.FuzzyText(length=2)
    kadastrale_gemeente = factory.SubFactory(KadastraleGemeenteFactory)
    geometrie = random_poly()


class NatuurlijkPersoonFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.KadastraalSubject

    pk = fuzzy.FuzzyText(length=60)
    type = models.KadastraalSubject.SUBJECT_TYPE_NATUURLIJK
    bron = fuzzy.FuzzyChoice(choices=(models.KadastraalSubject.BRON_KADASTER,
                                      models.KadastraalSubject.BRON_REGISTRATIE))
