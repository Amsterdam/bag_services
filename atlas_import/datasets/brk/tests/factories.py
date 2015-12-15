import factory
import faker
from django.contrib.gis.geos import MultiPolygon, Polygon
from factory import fuzzy

from datasets.generic import kadaster
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
    sectie = fuzzy.FuzzyText(length=1)
    kadastrale_gemeente = factory.SubFactory(KadastraleGemeenteFactory)
    geometrie = random_poly()


class NatuurlijkPersoonFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.KadastraalSubject

    pk = fuzzy.FuzzyText(length=60)
    type = models.KadastraalSubject.SUBJECT_TYPE_NATUURLIJK
    bron = fuzzy.FuzzyChoice(choices=(models.KadastraalSubject.BRON_KADASTER,
                                      models.KadastraalSubject.BRON_REGISTRATIE))


class KadastraalSubjectFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.KadastraalSubject

    pk = fuzzy.FuzzyText(length=60)
    type = fuzzy.FuzzyChoice(choices=(models.KadastraalSubject.SUBJECT_TYPE_NATUURLIJK,
                                      models.KadastraalSubject.SUBJECT_TYPE_NIET_NATUURLIJK))
    bron = fuzzy.FuzzyChoice(choices=(models.KadastraalSubject.BRON_KADASTER,
                                      models.KadastraalSubject.BRON_REGISTRATIE))


class KadastraalObjectFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.KadastraalObject

    pk = fuzzy.FuzzyText(length=60)
    aanduiding = factory.LazyAttribute(lambda obj: kadaster.get_aanduiding(obj.sectie.kadastrale_gemeente.pk,
                                                                           obj.sectie.sectie,
                                                                           obj.perceelnummer,
                                                                           obj.index_letter,
                                                                           obj.index_nummer))
    kadastrale_gemeente = factory.SubFactory(KadastraleGemeenteFactory)
    sectie = factory.SubFactory(KadastraleSectieFactory)
    perceelnummer = fuzzy.FuzzyInteger(low=0, high=9999)
    index_letter = fuzzy.FuzzyChoice(choices=('A', 'G'))
    index_nummer = fuzzy.FuzzyInteger(low=0, high=9999)
    grootte = fuzzy.FuzzyInteger(low=10, high=1000)
    register9_tekst = fuzzy.FuzzyText(length=50)
    geometrie = random_poly()
