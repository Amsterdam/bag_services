# Python
import json
# Packages
import elasticsearch_dsl as es
# Project
from . import models
from datasets.generic import analyzers
from django.conf import settings


class Ligplaats(es.DocType):
    straatnaam = es.String(
        analyzer=analyzers.adres,
        fields={
            'raw': es.String(index='not_analyzed'),
            'ngram': es.String(
                analyzer=analyzers.autocomplete, search_analyzer='standard'),
        },
    )
    adres = es.String(
        analyzer=analyzers.adres,
        fields={
            'raw': es.String(index='not_analyzed'),
            'ngram': es.String(
                analyzer=analyzers.autocomplete, search_analyzer='standard',
            ),
        },
    )
    huisnummer = es.Integer(
        fields={'variation': es.String(analyzer=analyzers.huisnummer)},
    )
    postcode = es.String(
        analyzer=analyzers.postcode,
        fields={
            'raw': es.String(index='not_analyzed'),
            'ngram': es.String(analyzer=analyzers.postcode_ng),
        },
    )
    order = es.Integer()

    centroid = es.GeoPoint()

    class Meta:
        index = settings.ELASTIC_INDICES['BAG']


class Standplaats(es.DocType):
    straatnaam = es.String(
        analyzer=analyzers.adres,
        fields={
            'raw': es.String(index='not_analyzed'),
            'ngram': es.String(
                analyzer=analyzers.autocomplete, search_analyzer='standard')})

    adres = es.String(
        analyzer=analyzers.adres, fields={
            'raw': es.String(index='not_analyzed'),
            'ngram': es.String(
                analyzer=analyzers.autocomplete, search_analyzer='standard')})
    huisnummer = es.Integer(
        fields={'variation': es.String(analyzer=analyzers.huisnummer)})
    postcode = es.String(
        analyzer=analyzers.postcode,
        fields={
            'raw': es.String(index='not_analyzed'),
            'ngram': es.String(analyzer=analyzers.postcode_ng)})
    order = es.Integer()

    centroid = es.GeoPoint()

    class Meta:
        index = settings.ELASTIC_INDICES['BAG']


class Verblijfsobject(es.DocType):
    straatnaam = es.String(
        analyzer=analyzers.adres,
        fields={
            'raw': es.String(index='not_analyzed'),
            'ngram': es.String(
                analyzer=analyzers.autocomplete, search_analyzer='standard')})
    adres = es.String(
        analyzer=analyzers.adres,
        fields={
            'raw': es.String(index='not_analyzed'),
            'ngram': es.String(
                analyzer=analyzers.autocomplete, search_analyzer='standard')})
    huisnummer = es.Integer(
        fields={'variation': es.String(analyzer=analyzers.huisnummer)})
    postcode = es.String(
        analyzer=analyzers.postcode,
        fields={
            'raw': es.String(index='not_analyzed'),
            'ngram': es.String(analyzer=analyzers.postcode_ng)})
    order = es.Integer()

    centroid = es.GeoPoint()

    bestemming = es.String()
    kamers = es.Integer()
    oppervlakte = es.Integer()

    class Meta:
        index = settings.ELASTIC_INDICES['BAG']


class OpenbareRuimte(es.DocType):
    naam = es.String(
        analyzer=analyzers.adres, fields={
            'raw': es.String(index='not_analyzed'),
            'ngram': es.String(
                analyzer=analyzers.autocomplete,
                search_analyzer='standard')})
    postcode = es.String(
        analyzer=analyzers.postcode,
        fields={
            'raw': es.String(index='not_analyzed'),
            'ngram': es.String(analyzer=analyzers.postcode_ng)})
    order = es.Integer()

    subtype = es.String(analyzer=analyzers.subtype)

    class Meta:
        index = settings.ELASTIC_INDICES['BAG']


class Nummeraanduiding(es.DocType):
    """
    All bag objects should have one or more adresses

    Een nummeraanduiding, in de volksmond ook wel adres genoemd, is een door
    het bevoegde gemeentelijke orgaan als
    zodanig toegekende aanduiding van een verblijfsobject, standplaats of
    ligplaats.

    [Stelselpedia](http://www.amsterdam.nl/stelselpedia/bag-index/catalogus-bag/objectklasse-2/)
    """
    straatnaam = es.String(
        analyzer=analyzers.adres, copy_to='address_copy',
        fields={
            'raw': es.String(index='not_analyzed'),
            'ngram': es.String(
                analyzer=analyzers.autocomplete, search_analyzer='standard')})
    straatnaam_nen = es.String(
        analyzer=analyzers.adres,
        fields={
            'raw': es.String(index='not_analyzed'),
            'ngram': es.String(
                analyzer=analyzers.autocomplete, search_analyzer='standard')})

    straatnaam_ptt = es.String(
        analyzer=analyzers.adres, fields={
            'raw': es.String(index='not_analyzed'),
            'ngram': es.String(
                analyzer=analyzers.autocomplete,
                search_analyzer='standard')})

    adres = es.String(
        analyzer=analyzers.adres,
        fields={
            'raw': es.String(index='not_analyzed'),
            'ngram': es.String(
                analyzer=analyzers.autocomplete,
                search_analyzer='standard')})
    comp_address = es.String(
        analyzer=analyzers.adres, fields={
            'raw': es.String(index='not_analyzed'),
            'ngram': es.String(
                analyzer=analyzers.autocomplete, search_analyzer='standard')})
    comp_address_nen = es.String(
        analyzer=analyzers.adres,
        fields={
            'raw': es.String(index='not_analyzed'),
            'ngram': es.String(
                analyzer=analyzers.autocomplete,
                search_analyzer='standard')})

    comp_address_ptt = es.String(
        analyzer=analyzers.adres,
        fields={
            'raw': es.String(index='not_analyzed'),
            'ngram': es.String(
                analyzer=analyzers.autocomplete, search_analyzer='standard')})
    address_copy = es.String(
            analyzer=analyzers.adres,
            fields={
                'raw': es.String(index='not_analyzed'),
                'ngram': es.String(
                    analyzer=analyzers.autocomplete,
                    search_analyzer='standard')})
    huisnummer = es.Integer(
        copy_to='address_copy',
        fields={'variation': es.String(analyzer=analyzers.huisnummer)})
    postcode = es.String(
        analyzer=analyzers.postcode,
        copy_to='address_copy',
        fields={
            'raw': es.String(index='not_analyzed'),
            'ngram': es.String(analyzer=analyzers.postcode_ng)})

    order = es.Integer()

    subtype = es.String(analyzer=analyzers.subtype)

    class Meta:
        index = settings.ELASTIC_INDICES['NUMMERAANDUIDING']


class Bouwblok(es.DocType):
    """
    Elasticsearch doc for the bouwblok model
    """
    code = es.String(
        analyzer=analyzers.bouwblok,
        fields={
            'raw': es.String(index='not_analyzed'),
        },
    )

    subtype = es.String(analyzer=analyzers.subtype)

    class Meta:
        index = settings.ELASTIC_INDICES['BAG']


class ExactLocation(es.DocType):
    """
    Elasticsearch doc for exact location data
    """
    postcode = es.String(analyzer=analyzers.subtype)
    huisnummer = es.Integer(analyzer=analyzers.subtype)
    toevoeging = es.String(analyzer=analyzers.subtype)
    address = es.String(analyzer=analyzers.subtype)
    postcode_huisnummer = es.String(analyzer=analyzers.subtype)
    postcode_toevoeging = es.String(analyzer=analyzers.subtype)

    geometrie = es.GeoPoint()

    class Meta:
        index = settings.ELASTIC_INDICES['BAG']


def get_centroid(geom):
    if not geom:
        return None

    result = geom.centroid
    result.transform('wgs84')
    return result.coords


def update_adres(dest, adres: models.Nummeraanduiding):  # flake8: noqa
    if adres:
        dest.adres = adres.adres()
        dest.postcode = adres.postcode
        dest.straatnaam = adres.openbare_ruimte.naam
        dest.straatnaam_raw = adres.openbare_ruimte.naam

        dest.huisnummer = adres.huisnummer


def add_verblijfsobject(doc, vo: models.Verblijfsobject):
    if vo:
        doc.centroid = get_centroid(vo.geometrie)
        doc.subtype_id = vo.id
        doc.order = analyzers.orderings['adres']


def add_standplaats(doc, sp: models.Standplaats):
    if sp:
        doc.centroid = get_centroid(sp.geometrie)
        doc.subtype_id = sp.id
        doc.order = analyzers.orderings['adres']


def add_ligplaats(doc, lp: models.Ligplaats):
    if lp:
        doc.centroid = get_centroid(lp.geometrie)
        doc.subtype_id = lp.id
        doc.order = analyzers.orderings['adres']


def from_ligplaats(l: models.Ligplaats):
    # id unique
    d = Ligplaats(_id=l.id)

    update_adres(d, l.hoofdadres)

    d.centroid = get_centroid(l.geometrie)
    d.order = analyzers.orderings['adres']

    return d


def from_bouwblok(n: models.Bouwblok):
    doc = Bouwblok(_id=n.id)
    doc.code = n.code
    doc.subtype = 'bouwblok'

    return doc

def from_nummeraanduiding_ruimte(n: models.Nummeraanduiding):
    doc = Nummeraanduiding(_id=n.id)
    doc.adres = n.adres()
    doc.comp_address = "{0} {1} {2}".format(n.openbare_ruimte.naam,
                                            n.postcode, n.toevoeging)
    doc.comp_address_nen = "{0} {1} {2}".format(n.openbare_ruimte.naam_nen,
                                                n.postcode, n.toevoeging)
    doc.comp_address_ptt = "{0} {1} {2}".format(n.openbare_ruimte.naam_ptt,
                                                n.postcode, n.toevoeging)
    doc.postcode = n.postcode
    doc.straatnaam = n.openbare_ruimte.naam
    doc.straatnaam_nen = n.openbare_ruimte.naam_nen
    doc.straatnaam_ptt = n.openbare_ruimte.naam_ptt
    doc.huisnummer = n.huisnummer

    if n.bron:
        doc.bron = n.bron.omschrijving

    #if not doc.subtype:
    #    return doc

    doc.subtype = n.get_type_display().lower()

    if doc.subtype == 'verblijfsobject':
        add_verblijfsobject(doc, n.verblijfsobject)
    elif doc.subtype == 'standplaats':
        add_standplaats(doc, n.standplaats)
    elif doc.subtype == 'ligplaats':
        add_ligplaats(doc, n.ligplaats)
    elif doc.subtype == 'overig gebouwd object':
        pass
    elif doc.subtype == 'overig terrein':
        pass

    return doc


def from_standplaats(s: models.Standplaats):

    d = Standplaats(_id=s.id)

    update_adres(d, s.hoofdadres)

    d.centroid = get_centroid(s.geometrie)
    d.order = analyzers.orderings['adres']

    return d


def from_verblijfsobject(v: models.Verblijfsobject):
    d = Verblijfsobject(_id=v.id)
    update_adres(d, v.hoofdadres)
    d.centroid = get_centroid(v.geometrie)

    d.bestemming = v.gebruiksdoel_omschrijving
    d.kamers = v.aantal_kamers
    d.oppervlakte = v.oppervlakte
    d.order = analyzers.orderings['adres']

    return d


def from_openbare_ruimte(o: models.OpenbareRuimte):
    d = OpenbareRuimte(_id=o.id)
    d.type = 'Openbare ruimte'
    d.subtype = o.get_type_display().lower()
    d.naam = o.naam
    postcodes = set()

    for a in o.adressen.all():
        if a.postcode:
            postcodes.add(a.postcode)

    d.postcode = list(postcodes)
    d.order = analyzers.orderings['openbare_ruimte']

    return d


def exact_from_nummeraanduiding(n: models.Nummeraanduiding):
    doc = ExactLocation(_id=n.id)
    doc.adres = n.adres()
    doc.postcode = n.postcode
    doc.huisnummer = n.huisnummer
    doc.toevoeging = n.toevoeging
    doc.postcode_huisnummer = '{0} {1}'.format(n.postcode, n.huisnummer)
    doc.postcode_toevoeging = '{0} {1}'.format(n.postcode, n.toevoeging)
    # Retriving the geolocation is dependent on the geometrie
    if n.verblijfsobject:
        doc.geometrie = n.verblijfsobject.geometrie.geojson
    elif n.standplaats:
        doc.geometrie = n.standplaats.geometrie,geojson
    elif n.ligplaats:
        doc.geometrie = (get_centroid(n.ligplaats.geometrie).geojson)
    doc.geometrie = json.loads(doc.geometrie)
    return doc

