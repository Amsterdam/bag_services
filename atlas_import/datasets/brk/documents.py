import elasticsearch_dsl as es

from datasets.generic import analyzers
from django.conf import settings


class KadastraalObject(es.DocType):
    aanduiding = es.String(
        analyzer=analyzers.postcode,
        fields={
            'raw': es.String(index='not_analyzed'),
            'ngram': es.String(analyzer=analyzers.kad_obj_aanduiding)})
    # The search aanduiding is the aanduiding without the "acd00 " prefix
    order = es.Integer()
    centroid = es.GeoPoint()

    subtype = es.String(analyzer=analyzers.subtype)
    _display = es.String(index='not_analyzed')

    class Meta:
        index = settings.ELASTIC_INDICES['BRK']
        all = es.MetaField(enabled=False)


class KadastraalSubject(es.DocType):
    naam = es.String(
        analyzer=analyzers.naam,
        fields={
            'raw': es.String(index='not_analyzed'),
            'ngram': es.String(
                analyzer=analyzers.kad_obj_aanduiding,
                search_analyzer=analyzers.kad_obj_aanduiding_search)})
    natuurlijk_persoon = es.Boolean()
    geslachtsnaam = es.String(analyzer=analyzers.naam)
    order = es.Integer()

    subtype = es.String(analyzer=analyzers.subtype)
    _display = es.String(index='not_analyzed')

    class Meta:
        index = settings.ELASTIC_INDICES['BRK']
        all = es.MetaField(enabled=False)


def from_kadastraal_subject(ks):
    d = KadastraalSubject(_id=ks.pk)

    if ks.is_natuurlijk_persoon():
        d.natuurlijk_persoon = True

        d.geslachtsnaam = ks.naam
    else:
        d.natuurlijk_persoon = False

    d.naam = ks.volledige_naam()
    d.order = analyzers.orderings['kadastraal_subject']
    d.subtype = 'kadastraal_subject'
    d._display = d.naam

    return d


def from_kadastraal_object(ko):
    d = KadastraalObject(_id=ko.pk)

    d.aanduiding = ko.get_aanduiding_spaties()
    d.search_aanduiding = d.aanduiding[6:]
    d.order = analyzers.orderings['kadastraal_object']

    d.subtype = 'kadastraal_object'
    # Finding the centeroid
    geometrie = ko.point_geom or ko.poly_geom
    if geometrie:
        centroid = geometrie.centroid
        centroid.transform('wgs84')

        d.centroid = centroid.coords
    d._display = d.aanduiding

    return d
