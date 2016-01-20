import elasticsearch_dsl as es

from . import models
from datasets.generic import analyzers
from django.conf import settings


class Ligplaats(es.DocType):
    straatnaam = es.String(analyzer=analyzers.adres)

    adres = es.String(analyzer=analyzers.adres)
    huisnummer_variation = es.String(analyzer=analyzers.huisnummer)
    huisnummer = es.Integer()

    postcode = es.String(analyzer=analyzers.postcode)
    order = es.Integer()

    centroid = es.GeoPoint()

    class Meta:
        index = settings.ELASTIC_INDICES['BAG']


class Standplaats(es.DocType):
    straatnaam = es.String(analyzer=analyzers.adres)
    adres = es.String(analyzer=analyzers.adres)

    huisnummer_variation = es.String(analyzer=analyzers.huisnummer)
    huisnummer = es.Integer()

    postcode = es.String(analyzer=analyzers.postcode)
    order = es.Integer()

    centroid = es.GeoPoint()

    class Meta:
        index = settings.ELASTIC_INDICES['BAG']


class Verblijfsobject(es.DocType):
    straatnaam = es.String(analyzer=analyzers.adres)
    adres = es.String(analyzer=analyzers.adres)
    huisnummer_variation = es.String(analyzer=analyzers.huisnummer)
    huisnummer = es.Integer()
    postcode = es.String(analyzer=analyzers.postcode)
    order = es.Integer()

    centroid = es.GeoPoint()

    bestemming = es.String()
    kamers = es.Integer()
    oppervlakte = es.Integer()

    class Meta:
        index = settings.ELASTIC_INDICES['BAG']


class OpenbareRuimte(es.DocType):
    naam = es.String(analyzer=analyzers.adres)
    postcode = es.String(analyzer=analyzers.postcode)
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
    straatnaam = es.String(analyzer=analyzers.adres)
    adres = es.String(analyzer=analyzers.adres)
    huisnummer_variation = es.String(analyzer=analyzers.huisnummer)
    huisnummer = es.Integer()
    postcode = es.String(analyzer=analyzers.postcode)

    order = es.Integer()

    subtype = es.String(analyzer=analyzers.subtype)

    class Meta:
        index = settings.ELASTIC_INDICES['NUMMERAANDUIDING']


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
        dest.huisnummer_variation = adres.huisnummer


def add_verblijfsobject(doc, vo: models.Verblijfsobject):
    if vo:
        doc.centroid = get_centroid(vo.geometrie)
        doc.bestemming = vo.gebruiksdoel_omschrijving
        doc.kamers = vo.aantal_kamers
        doc.oppervlakte = vo.oppervlakte
        doc.bagtype = 'Verblijfsobject'


def add_standplaats(doc, sp: models.Standplaats):
    if sp:
        doc.centroid = get_centroid(sp.geometrie)
        doc.bagtype = 'Standplaats'


def add_ligplaats(doc, lp: models.Ligplaats):
    if lp:
        doc.centroid = get_centroid(lp.geometrie)
        doc.bagtype = 'Ligplaats'


def from_ligplaats(l: models.Ligplaats):
    # id unique
    d = Ligplaats(_id=l.id)

    update_adres(d, l.hoofdadres)

    d.centroid = get_centroid(l.geometrie)
    d.order = analyzers.orderings['adres']

    return d


def from_nummeraanduiding_ruimte(n: models.Nummeraanduiding):
    d = Nummeraanduiding(_id=n.id)
    d.adres = n.adres()
    d.postcode = "{}-{}".format(n.postcode, n.toevoeging)
    d.straatnaam = n.openbare_ruimte.naam
    d.huisnummer = n.huisnummer
    d.huisnummer_variation = n.huisnummer

    # d.adresseerbaar_object = n.adresseerbaar_object

    if n.buurt:
        d.buurt = n.buurt.naam

    if n.stadsdeel:
        d.stadsdeel = n.stadsdeel.naam

    if n.woonplaats:
        d.woonplaats = n.woonplaats.naam
    if n.buurtcombinatie:
        d.buurtcombinatie = n.buurtcombinatie.naam

    if n.bron:
        d.bron = n.bron.omschrijving

    d.subtype = n.get_type_display()

    if d.subtype == 'Verblijfsobject':
        add_verblijfsobject(d, n.verblijfsobject)
    elif d.subtype == 'Standplaats':
        pass
        add_standplaats(d, n.standplaats)
    elif d.subtype == 'Ligplaats':
        add_ligplaats(d, n.ligplaats)
    elif d.subtype == 'Overig gebouwd object':
        pass
    elif d.subtype == 'Overig terrein':
        pass

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
    d.type = 'Openbare ruimte'
    d.subtype = o.get_type_display()
    d.naam = o.naam
    postcodes = set()

    for a in o.adressen.all():
        if a.postcode:
            postcodes.add(a.postcode)

    d.postcode = list(postcodes)
    d.order = analyzers.orderings['openbare_ruimte']

    return d
