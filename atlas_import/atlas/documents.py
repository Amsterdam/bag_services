import elasticsearch_dsl as es

from atlas import models

class Ligplaats(es.DocType):
    type = es.String()
    adres = es.String()
    postcode = es.String()

    class Meta:
        index = 'atlas'

class Standplaats(es.DocType):
    type = es.String()
    adres = es.String()
    postcode = es.String()

    class Meta:
        index = 'atlas'

class Verblijfsobject(es.DocType):
    type = es.String()
    adres = es.String()
    postcode = es.String()
    bestemming = es.String()
    kamers = es.Integer()
    oppervlakte = es.Integer()

    class Meta:
        index = 'atlas'


def from_ligplaats(l: models.Ligplaats):
    d = Ligplaats(_id=l.id)
    if l.hoofdadres:
        d.adres = l.hoofdadres.adres()
        d.postcode = l.hoofdadres.postcode

    return d


def from_standplaats(s: models.Standplaats):
    d = Standplaats(_id=s.id)
    if s.hoofdadres:
        d.adres = s.hoofdadres.adres()
        d.postcode = s.hoofdadres.postcode

    return d


def from_verblijfsobject(v: models.Verblijfsobject):
    d = Verblijfsobject(_id=v.id)
    if v.hoofdadres:
        d.adres = v.hoofdadres.adres()
        d.postcode = v.hoofdadres.postcode

    d.bestemming = v.gebruiksdoel_omschrijving
    d.kamers = v.aantal_kamers
    d.oppervlakte = v.oppervlakte

    return d
