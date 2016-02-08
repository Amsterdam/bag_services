import elasticsearch_dsl as es

from datasets.generic import analyzers
from django.conf import settings


class KadastraalObject(es.DocType):
    aanduiding = es.String(analyzer=analyzers.kadastrale_aanduiding)
    order = es.Integer()
    centroid = es.GeoPoint()

    subtype = es.String(analyzer=analyzers.subtype)

    class Meta:
        index = settings.ELASTIC_INDICES['BRK']


class KadastraalSubject(es.DocType):
    naam = es.String(analyzer=analyzers.naam)
    natuurlijk_persoon = es.Boolean()
    geslachtsnaam = es.String(analyzer=analyzers.naam)
    geboortedatum = es.Date()
    order = es.Integer()

    subtype = es.String(analyzer=analyzers.subtype)

    class Meta:
        index = settings.ELASTIC_INDICES['BRK']


def from_kadastraal_subject(ks):
    d = KadastraalSubject(_id=ks.pk)

    if ks.is_natuurlijk_persoon():
        d.natuurlijk_persoon = True

        d.geslachtsnaam = ks.naam
        d.geboortedatum = ks.geboortedatum
    else:
        d.natuurlijk_persoon = False

    d.naam = ks.volledige_naam()
    d.order = analyzers.orderings['kadastraal_subject']
    d.subtype = 'kadestraal_subject'

    return d


def from_kadastraal_object(ko):
    d = KadastraalObject(_id=ko.pk)

    d.aanduiding = ko.aanduiding
    d.order = analyzers.orderings['kadastraal_object']

    d.subtype = 'kadestraal_object'

    if ko.geometrie:
        centroid = ko.geometrie.centroid
        centroid.transform('wgs84')

        d.centroid = centroid.coords

    return d
