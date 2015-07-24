import elasticsearch_dsl as es

from atlas import models

Adres = es.Nested(properties=dict(
    straatnaam=es.String(),
    huisnummer=es.Integer(),
    huisletter=es.String(),
    toevoeging=es.String(),
    postcode=es.String(),
    woonplaats=es.String()
))


def from_nummeraanduiding(nummeraanduiding):
    return dict(
        straatnaam=nummeraanduiding.openbare_ruimte.naam,
        huisnummer=nummeraanduiding.huisnummer,
        huisletter=nummeraanduiding.huisletter,
        toevoeging=nummeraanduiding.huisnummer_toevoeging,
        postcode=nummeraanduiding.postcode,
        woonplaats=nummeraanduiding.openbare_ruimte.woonplaats.naam,
    )


class AdresseerbaarObject(es.DocType):
    type = es.String()
    adres = Adres

    class Meta:
        index = 'atlas'


def from_ligplaats(l: models.Ligplaats):
    d = AdresseerbaarObject(_id=l.id, type="ligplaats")
    if l.hoofdadres:
        d.adres = from_nummeraanduiding(l.hoofdadres)

    return d


def from_standplaats(s: models.Standplaats):
    d = AdresseerbaarObject(_id=s.id, type="standplaats")
    if s.hoofdadres:
        d.adres = from_nummeraanduiding(s.hoofdadres)

    return d


def from_verblijfsobject(v: models.Verblijfsobject):
    d = AdresseerbaarObject(_id=v.id, type="verblijfsobject")
    if v.hoofdadres:
        d.adres = from_nummeraanduiding(v.hoofdadres)

    return d