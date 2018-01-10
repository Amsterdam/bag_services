import elasticsearch_dsl as es

from search import analyzers
from django.conf import settings


kad_text_fields = {
    'raw': es.Keyword(),
    'ngram': es.Text(analyzer=analyzers.kad_obj_aanduiding),
    'keyword': es.Keyword(normalizer=analyzers.lowercase)
}

kad_int_fields = {
    'raw': es.Keyword(),
    'int': es.Integer(),
    'ngram': es.Text(analyzer=analyzers.kad_obj_aanduiding),
    'keyword': es.Keyword(normalizer=analyzers.lowercase)
}


class KadastraalObject(es.DocType):
    aanduiding = es.Text(
        fielddata=True,
        analyzer=analyzers.postcode,
        fields=kad_text_fields)

    # The search aanduiding is the aanduiding without the "acd00 " prefix
    # remove this in future
    short_aanduiding = es.Text(
        analyzer=analyzers.kad_obj_aanduiding,
        search_analyzer='standard',
        fields=kad_text_fields)

    sectie = es.Text(
        fields=kad_text_fields,
    )

    objectnummer = es.Text(
        analyzer=analyzers.autocomplete,
        search_analyzer='standard',
        fields=kad_int_fields,
    )

    indexletter = es.Keyword(
        fields=kad_text_fields,
    )

    indexnummer = es.Text(
        analyzer=analyzers.autocomplete,
        search_analyzer='standard',
        fields=kad_int_fields
    )

    order = es.Integer()
    centroid = es.GeoPoint()

    gemeente = es.Text(analyzer=analyzers.naam)
    gemeente_code = es.Keyword(normalizer=analyzers.lowercase)

    subtype = es.Keyword()
    _display = es.Keyword()

    class Meta:
        index = settings.ELASTIC_INDICES['BRK_OBJECT']


class KadastraalSubject(es.DocType):
    naam = es.Text(
        analyzer=analyzers.naam,
        fields={
            'raw': es.Keyword(),
            'ngram': es.Text(
                analyzer=analyzers.kad_sbj_naam,
                search_analyzer=analyzers.kad_obj_aanduiding_keyword)})

    natuurlijk_persoon = es.Boolean()
    geslachtsnaam = es.Text(analyzer=analyzers.naam)
    order = es.Integer()

    subtype = es.Keyword()
    _display = es.Keyword()

    class Meta:
        index = settings.ELASTIC_INDICES['BRK_SUBJECT']


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

    d.gemeente = ko.kadastrale_gemeente.naam
    d.gemeente_code = ko.kadastrale_gemeente.id.lower()

    d.sectie = ko.sectie.sectie
    d.objectnummer = ko.perceelnummer
    d.indexletter = ko.indexletter
    d.indexnummer = ko.indexnummer

    d.short_aanduiding = d.aanduiding[6:]

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
