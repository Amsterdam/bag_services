# Python
from random import randint
import string
# Packages
from django.contrib.gis.geos import Point
import factory

from faker import Faker

from factory import fuzzy

# from datasets.brk.tests import factories as brkfactory

# Project

from .. import models

f = Faker(locale='nl_NL')


class GebruikFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.Gebruik

    code = fuzzy.FuzzyText(length=4)
    omschrijving = fuzzy.FuzzyText(length=50)


class GemeenteFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.Gemeente
        django_get_or_create = ('code',)

    naam = 'Amsterdam'
    id = fuzzy.FuzzyText(length=14, chars=string.digits)
    code = fuzzy.FuzzyText(length=4, chars=string.digits)


class BuurtcombinatieFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.Buurtcombinatie
        django_get_or_create = ('code',)

    id = fuzzy.FuzzyText(length=14, chars=string.digits)
    naam = fuzzy.FuzzyText(length=50)
    code = fuzzy.FuzzyText(length=2)
    vollcode = fuzzy.FuzzyText(length=3)


class StadsdeelFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.Stadsdeel
        django_get_or_create = ('code',)

    id = fuzzy.FuzzyText(length=14, chars=string.digits)
    naam = fuzzy.FuzzyText(length=4)
    code = fuzzy.FuzzyText(length=3, chars=string.digits)
    gemeente = factory.SubFactory(GemeenteFactory)


class BuurtFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.Buurt
        django_get_or_create = ('code',)

    id = fuzzy.FuzzyText(length=14, chars=string.digits)
    code = fuzzy.FuzzyText(length=3, chars=string.digits)
    vollcode = fuzzy.FuzzyText(length=4)
    stadsdeel = factory.SubFactory(StadsdeelFactory)
    buurtcombinatie = factory.SubFactory(BuurtcombinatieFactory)


class BouwblokFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.Bouwblok
        django_get_or_create = ('code',)

    id = fuzzy.FuzzyText(length=14, chars=string.digits)

    code = '%s%s' % (
        fuzzy.FuzzyText(length=2, chars=string.ascii_letters).fuzz(),
        fuzzy.FuzzyText(length=2, chars=string.digits).fuzz(),
    )
    buurt = factory.SubFactory(BuurtFactory)


class LigplaatsFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.Ligplaats

    id = fuzzy.FuzzyText(length=14, chars=string.digits)
    landelijk_id = fuzzy.FuzzyText(length=16, chars=string.digits)
    buurt = factory.SubFactory(BuurtFactory)


class StandplaatsFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.Standplaats

    id = fuzzy.FuzzyText(length=14, chars=string.digits)
    landelijk_id = fuzzy.FuzzyText(length=16, chars=string.digits)
    buurt = factory.SubFactory(BuurtFactory)


class PandFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.Pand

    id = fuzzy.FuzzyText(length=14, chars=string.digits)
    landelijk_id = fuzzy.FuzzyText(length=16, chars=string.digits)
    pandnaam = fuzzy.FuzzyText(length=20)
    bouwblok = factory.SubFactory(BouwblokFactory)


class VerblijfsobjectFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.Verblijfsobject

    id = fuzzy.FuzzyText(length=14, chars=string.digits)
    landelijk_id = fuzzy.FuzzyText(length=16, chars=string.digits)
    reden_afvoer = fuzzy.FuzzyText(length=100)
    reden_opvoer = fuzzy.FuzzyText(length=100)
    buurt = factory.SubFactory(BuurtFactory)
    status = fuzzy.FuzzyText(length=100)
    geometrie = Point(
        # Defaulting to 1000, 1000
        randint(1, 100), randint(1, 100), srid=28992)
    indicatie_in_onderzoek = False
    indicatie_geconstateerd = None


class VerblijfsobjectPandRelatie(factory.DjangoModelFactory):
    class Meta:
        model = models.VerblijfsobjectPandRelatie

    id = fuzzy.FuzzyText(length=14, chars=string.digits)
    pand = factory.SubFactory(PandFactory)
    verblijfsobject = factory.SubFactory(VerblijfsobjectFactory)


class WoonplaatsFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.Woonplaats
        django_get_or_create = ('landelijk_id',)

    id = fuzzy.FuzzyText(length=14, chars=string.digits)
    landelijk_id = fuzzy.FuzzyText(length=4, chars=string.digits)
    gemeente = factory.SubFactory(GemeenteFactory)


class OpenbareRuimteFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.OpenbareRuimte

    id = fuzzy.FuzzyText(length=14, chars=string.digits)
    landelijk_id = fuzzy.FuzzyText(length=16, chars=string.digits)
    woonplaats = factory.SubFactory(WoonplaatsFactory)
    naam = factory.LazyAttribute(lambda o: f.street_name())
    type = '01'  # weg


class NummeraanduidingFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.Nummeraanduiding

    id = fuzzy.FuzzyText(length=14, chars=string.digits)
    landelijk_id = fuzzy.FuzzyText(length=16, chars=string.digits)
    huisnummer = factory.LazyAttribute(lambda o: int(f.building_number()))
    openbare_ruimte = factory.SubFactory(OpenbareRuimteFactory)
    verblijfsobject = factory.SubFactory(VerblijfsobjectFactory)
    type = '01'  # default verblijfsobject
    postcode = '1000AN'  # default postcode..
    status = fuzzy.FuzzyText(length=100)

    _openbare_ruimte_naam = factory.LazyAttribute(
        lambda o: o.openbare_ruimte.naam)


class GrootstedelijkGebiedFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.Grootstedelijkgebied

    id = fuzzy.FuzzyText(length=14, chars=string.digits)
    naam = fuzzy.FuzzyText(length=50)
    gsg_type = fuzzy.FuzzyText(length=5)


class UnescoFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.Unesco

    naam = fuzzy.FuzzyText(length=50)


class GebiedsgerichtwerkenFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.Gebiedsgerichtwerken
        django_get_or_create = ('code',)

    id = fuzzy.FuzzyText(length=4, chars=string.digits)
    naam = fuzzy.FuzzyText(length=50)
    code = fuzzy.FuzzyText(length=4)
    stadsdeel = factory.SubFactory(StadsdeelFactory)


class GebiedsgerichtwerkenPraktijkgebiedenFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.GebiedsgerichtwerkenPraktijkgebieden
        django_get_or_create = ('naam',)

    naam = fuzzy.FuzzyText(length=100)
