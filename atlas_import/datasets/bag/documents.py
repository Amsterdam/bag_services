import elasticsearch_dsl as es

from . import models


adres_analyzer = es.analyzer('adres', tokenizer='keyword', filter=['standard', 'lowercase', 'asciifolding'])


class Ligplaats(es.DocType):
    adres = es.String(analyzer=adres_analyzer)
    postcode = es.String()
    centroid = es.GeoPoint()

    class Meta:
        index = 'bag'


class Standplaats(es.DocType):
    adres = es.String(analyzer=adres_analyzer)
    postcode = es.String()
    centroid = es.GeoPoint()

    class Meta:
        index = 'bag'


class Verblijfsobject(es.DocType):
    adres = es.String(analyzer=adres_analyzer)
    postcode = es.String()
    centroid = es.GeoPoint()

    bestemming = es.String()
    kamers = es.Integer()
    oppervlakte = es.Integer()

    class Meta:
        index = 'bag'


class OpenbareRuimte(es.DocType):
    naam = es.String(analyzer=adres_analyzer)

    class Meta:
        index = 'bag'


def get_centroid(geom):
    if not geom:
        return None

    result = geom.centroid
    result.transform('wgs84')
    return result.coords


def from_ligplaats(l: models.Ligplaats):
    d = Ligplaats(_id=l.id)
    if l.hoofdadres:
        d.adres = l.hoofdadres.adres()
        d.postcode = l.hoofdadres.postcode
    d.centroid = get_centroid(l.geometrie)

    return d


def from_standplaats(s: models.Standplaats):
    d = Standplaats(_id=s.id)
    if s.hoofdadres:
        d.adres = s.hoofdadres.adres()
        d.postcode = s.hoofdadres.postcode
    d.centroid = get_centroid(s.geometrie)

    return d


def from_verblijfsobject(v: models.Verblijfsobject):
    d = Verblijfsobject(_id=v.id)
    if v.hoofdadres:
        d.adres = v.hoofdadres.adres()
        d.postcode = v.hoofdadres.postcode
    d.centroid = get_centroid(v.geometrie)

    d.bestemming = v.gebruiksdoel_omschrijving
    d.kamers = v.aantal_kamers
    d.oppervlakte = v.oppervlakte

    return d


def from_openbare_ruimte(o: models.OpenbareRuimte):
    d = OpenbareRuimte(_id=o.id)
    d.naam = o.naam

    return d
