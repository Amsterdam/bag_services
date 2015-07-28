import elasticsearch_dsl as es

from atlas import models

class Ligplaats(es.DocType):
    type = es.String()
    adres = es.String()
    postcode = es.String()
    centroid = es.GeoPoint()

    class Meta:
        index = 'atlas'

class Standplaats(es.DocType):
    type = es.String()
    adres = es.String()
    postcode = es.String()
    centroid = es.GeoPoint()

    class Meta:
        index = 'atlas'

class Verblijfsobject(es.DocType):
    type = es.String()
    adres = es.String()
    postcode = es.String()
    centroid = es.GeoPoint()

    bestemming = es.String()
    kamers = es.Integer()
    oppervlakte = es.Integer()

    class Meta:
        index = 'atlas'


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
