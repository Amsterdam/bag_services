import elasticsearch_dsl as es

from . import models
from datasets.generic import analyzers


class Ligplaats(es.DocType):
    straatnaam = es.String(analyzer=analyzers.adres)
    adres = es.String(analyzer=analyzers.adres)
    huisnummer = es.Integer()
    postcode = es.String(analyzer=analyzers.postcode)
    order = es.Integer()

    centroid = es.GeoPoint()

    class Meta:
        index = 'bag'


class Standplaats(es.DocType):
    straatnaam = es.String(analyzer=analyzers.adres)
    adres = es.String(analyzer=analyzers.adres)
    huisnummer = es.Integer()
    postcode = es.String(analyzer=analyzers.postcode)
    order = es.Integer()

    centroid = es.GeoPoint()

    class Meta:
        index = 'bag'


class Verblijfsobject(es.DocType):
    straatnaam = es.String(analyzer=analyzers.adres)
    adres = es.String(analyzer=analyzers.adres)
    huisnummer = es.Integer()
    postcode = es.String(analyzer=analyzers.postcode)
    order = es.Integer()

    centroid = es.GeoPoint()

    bestemming = es.String()
    kamers = es.Integer()
    oppervlakte = es.Integer()

    class Meta:
        index = 'bag'


class OpenbareRuimte(es.DocType):
    naam = es.String(analyzer=analyzers.adres)
    postcode = es.String(analyzer=analyzers.postcode)
    order = es.Integer()

    subtype = es.String(analyzer=analyzers.subtype)

    class Meta:
        index = 'bag'


def get_centroid(geom):
    if not geom:
        return None

    result = geom.centroid
    result.transform('wgs84')
    return result.coords


def update_adres(dest, adres: models.Nummeraanduiding):
    if adres:
        dest.adres = adres.adres()
        dest.postcode = "{}-{}".format(adres.postcode, adres.toevoeging)
        dest.straatnaam = adres.openbare_ruimte.naam
        dest.huisnummer = adres.huisnummer
        dest.huisnummer_toevoeging = adres.toevoeging


def from_ligplaats(l: models.Ligplaats):
    d = Ligplaats(_id=l.id)
    update_adres(d, l.hoofdadres)
    d.centroid = get_centroid(l.geometrie)
    d.order = analyzers.orderings['adres']

    return d


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
    d.subtype = o.get_type_name()
    d.naam = o.naam
    postcodes = set()
    for a in o.adressen.all():
        if a.postcode:
            postcodes.add(a.postcode)

    d.postcode = list(postcodes)
    d.order = analyzers.orderings['openbare_ruimte']

    return d
