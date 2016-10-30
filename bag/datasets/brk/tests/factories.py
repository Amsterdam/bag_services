import factory
import faker
from django.contrib.gis.geos import MultiPolygon, Polygon
from factory import fuzzy

from datasets.generic import kadaster
from .. import models

f = faker.Factory.create(locale='nl_NL')


def random_poly():
    return MultiPolygon(
        Polygon(
            ((0.0, 0.0), (0.0, 50.0), (50.0, 50.0), (50.0, 0.0), (0.0, 0.0))))


class GemeenteFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.Gemeente
        django_get_or_create = ('gemeente',)

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


class AdresFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.Adres

    pk = fuzzy.FuzzyText(length=32)
    openbareruimte_naam = fuzzy.FuzzyText(length=80)


class NatuurlijkPersoonFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.KadastraalSubject

    pk = fuzzy.FuzzyText(length=60)
    type = models.KadastraalSubject.SUBJECT_TYPE_NATUURLIJK
    bron = fuzzy.FuzzyChoice(
        choices=(models.KadastraalSubject.BRON_KADASTER,
                 models.KadastraalSubject.BRON_REGISTRATIE))
    woonadres = factory.SubFactory(AdresFactory)
    postadres = factory.SubFactory(AdresFactory)


class NietNatuurlijkPersoonFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.KadastraalSubject

    pk = fuzzy.FuzzyText(length=60)
    type = models.KadastraalSubject.SUBJECT_TYPE_NIET_NATUURLIJK
    bron = fuzzy.FuzzyChoice(choices=(
        models.KadastraalSubject.BRON_KADASTER,
        models.KadastraalSubject.BRON_REGISTRATIE))
    woonadres = factory.SubFactory(AdresFactory)
    postadres = factory.SubFactory(AdresFactory)


class KadastraalSubjectFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.KadastraalSubject

    pk = fuzzy.FuzzyText(length=60)
    type = fuzzy.FuzzyChoice(
        choices=(models.KadastraalSubject.SUBJECT_TYPE_NATUURLIJK,
                 models.KadastraalSubject.SUBJECT_TYPE_NIET_NATUURLIJK))
    bron = fuzzy.FuzzyChoice(
        choices=(models.KadastraalSubject.BRON_KADASTER,
                 models.KadastraalSubject.BRON_REGISTRATIE))
    woonadres = factory.SubFactory(AdresFactory)
    postadres = factory.SubFactory(AdresFactory)


class KadastraalObjectFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.KadastraalObject

    pk = fuzzy.FuzzyText(length=60)
    aanduiding = factory.LazyAttribute(
        lambda obj: kadaster.get_aanduiding(
            obj.kadastrale_gemeente.id,
            obj.sectie.sectie,
            obj.perceelnummer,
            obj.indexletter,
            obj.indexnummer))

    kadastrale_gemeente = factory.SubFactory(KadastraleGemeenteFactory)
    sectie = factory.SubFactory(KadastraleSectieFactory)
    perceelnummer = fuzzy.FuzzyInteger(low=0, high=9999)
    indexletter = fuzzy.FuzzyChoice(choices=('A', 'G'))
    indexnummer = fuzzy.FuzzyInteger(low=0, high=9999)
    grootte = fuzzy.FuzzyInteger(low=10, high=1000)
    register9_tekst = fuzzy.FuzzyText(length=50)
    poly_geom = random_poly()


class ZakelijkRechtFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.ZakelijkRecht

    pk = fuzzy.FuzzyText(length=60)
    kadastraal_object = factory.SubFactory(KadastraalObjectFactory)
    kadastraal_subject = factory.SubFactory(KadastraalSubjectFactory)

    _kadastraal_subject_naam = fuzzy.FuzzyText(length=50)
    kadastraal_object_status = fuzzy.FuzzyText(length=50)


class AardAantekeningFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.AardAantekening


class AantekeningFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.Aantekening

    pk = fuzzy.FuzzyText(length=60)
    aard_aantekening = factory.SubFactory(AardAantekeningFactory)

    kadastraal_object = factory.SubFactory(KadastraalObjectFactory)
    opgelegd_door = factory.SubFactory(KadastraalSubjectFactory)
