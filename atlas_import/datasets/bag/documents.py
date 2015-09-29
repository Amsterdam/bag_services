import elasticsearch_dsl as es

from . import models
from datasets.generic import analyzers


class Ligplaats(es.DocType):
    completions = es.String(analyzer=analyzers.autocomplete)
    straatnaam = es.String(analyzer=analyzers.adres)
    adres = es.String(analyzer=analyzers.adres)
    huisnummer = es.Integer()
    postcode = es.String()

    centroid = es.GeoPoint()

    class Meta:
        index = 'bag'


class Standplaats(es.DocType):
    completions = es.String(analyzer=analyzers.autocomplete)
    straatnaam = es.String(analyzer=analyzers.adres)
    adres = es.String(analyzer=analyzers.adres)
    huisnummer = es.Integer()
    postcode = es.String()

    centroid = es.GeoPoint()

    class Meta:
        index = 'bag'


class Verblijfsobject(es.DocType):
    completions = es.String(analyzer=analyzers.autocomplete)
    straatnaam = es.String(analyzer=analyzers.adres)
    adres = es.String(analyzer=analyzers.adres)
    huisnummer = es.Integer()

    postcode = es.String()
    centroid = es.GeoPoint()

    bestemming = es.String()
    kamers = es.Integer()
    oppervlakte = es.Integer()

    class Meta:
        index = 'bag'


class OpenbareRuimte(es.DocType):
    completions = es.String(analyzer=analyzers.autocomplete)
    naam = es.String(analyzer=analyzers.adres)
    postcode = es.String()

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
        dest.completions = [adres.adres(), adres.postcode]
        dest.adres = adres.adres()
        dest.postcode = adres.postcode
        dest.straatnaam = adres.openbare_ruimte.naam
        dest.huisnummer = int(adres.huisnummer)


def from_ligplaats(l: models.Ligplaats):
    d = Ligplaats(_id=l.id)
    update_adres(d, l.hoofdadres)
    d.centroid = get_centroid(l.geometrie)

    return d


def from_standplaats(s: models.Standplaats):
    d = Standplaats(_id=s.id)
    update_adres(d, s.hoofdadres)
    d.centroid = get_centroid(s.geometrie)

    return d


def from_verblijfsobject(v: models.Verblijfsobject):
    d = Verblijfsobject(_id=v.id)
    update_adres(d, v.hoofdadres)
    d.centroid = get_centroid(v.geometrie)

    d.bestemming = v.gebruiksdoel_omschrijving
    d.kamers = v.aantal_kamers
    d.oppervlakte = v.oppervlakte

    return d


def from_openbare_ruimte(o: models.OpenbareRuimte):
    d = OpenbareRuimte(_id=o.id)
    d.naam = o.naam
    postcodes = [p for p in o.adressen.values_list("postcode", flat=True).distinct() if p]
    d.postcode = postcodes
    d.completions = [d.naam] + postcodes

    return d
