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
        all = es.MetaField(enabled=False)


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

    _display = es.String(index='not_analyzed')

    class Meta:
        index = settings.ELASTIC_INDICES['BAG']
        all = es.MetaField(enabled=False)


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

    _display = es.String(index='not_analyzed')

    class Meta:
        index = settings.ELASTIC_INDICES['BAG']


class OpenbareRuimte(es.DocType):

    naam = es.String(
        analyzer=analyzers.adres,
        fields={
            'raw': es.String(index='not_analyzed'),
            'ngram_edge': es.String(
                analyzer=analyzers.autocomplete, search_analyzer='standard'
            ),
            'ngram': es.String(analyzer=analyzers.ngram),
            'keyword': es.String(analyzer=analyzers.subtype),

        }
    )

    naam_nen = es.String(
        analyzer=analyzers.adres,
        fields={
            'raw': es.String(index='not_analyzed'),
            'ngram_edge': es.String(
                analyzer=analyzers.autocomplete, search_analyzer='standard'
            ),
            'ngram': es.String(analyzer=analyzers.ngram),
            'keyword': es.String(analyzer=analyzers.subtype),

        }
    )

    naam_ptt = es.String(
        analyzer=analyzers.adres, fields={
            'raw': es.String(index='not_analyzed'),
            'ngram_edge': es.String(
                analyzer=analyzers.autocomplete, search_analyzer='standard'
            ),
            'ngram': es.String(analyzer=analyzers.ngram),
            'keyword': es.String(analyzer=analyzers.subtype),

        }
    )

    postcode = es.String(
        analyzer=analyzers.postcode,
        fields={
            'raw': es.String(index='not_analyzed'),
            'ngram': es.String(analyzer=analyzers.postcode_ng)})
    order = es.Integer()

    subtype = es.String(analyzer=analyzers.subtype)
    _display = es.String(index='not_analyzed')

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
        analyzer=analyzers.adres,
        fields={
            'raw': es.String(index='not_analyzed'),
            'ngram_edge': es.String(
                analyzer=analyzers.autocomplete, search_analyzer='standard'
            ),
            'ngram': es.String(analyzer=analyzers.ngram),
            'keyword': es.String(analyzer=analyzers.subtype),
        }
    )

    straatnaam_keyword = es.String(analyzer=analyzers.subtype)

    straatnaam_nen = es.String(
        analyzer=analyzers.adres,
        fields={
            'raw': es.String(index='not_analyzed'),
            'ngram_edge': es.String(
                analyzer=analyzers.autocomplete, search_analyzer='standard'
            ),
            'ngram': es.String(analyzer=analyzers.ngram),
            'keyword': es.String(analyzer=analyzers.subtype),

        }
    )

    straatnaam_nen_keyword = es.String(analyzer=analyzers.subtype)

    straatnaam_ptt = es.String(
        analyzer=analyzers.adres, fields={
            'raw': es.String(index='not_analyzed'),
            'ngram_edge': es.String(
                analyzer=analyzers.autocomplete, search_analyzer='standard'
            ),
            'ngram': es.String(analyzer=analyzers.ngram),
            'keyword': es.String(analyzer=analyzers.subtype),

        }
    )

    straatnaam_ptt_keyword = es.String(analyzer=analyzers.subtype)

    adres = es.String(
        analyzer=analyzers.adres,
        fields={
            'raw': es.String(index='not_analyzed'),
            'ngram_edge': es.String(
                analyzer=analyzers.autocomplete, search_analyzer='standard'
            ),
            'ngram': es.String(analyzer=analyzers.ngram)
        }
    )

    comp_address = es.String(
        analyzer=analyzers.adres, fields={
            'raw': es.String(index='not_analyzed'),
            'ngram': es.String(
                analyzer=analyzers.autocomplete, search_analyzer='standard')
            }
        )
    comp_address_nen = es.String(
        analyzer=analyzers.adres,
        fields={
            'raw': es.String(index='not_analyzed'),
            'ngram': es.String(
                analyzer=analyzers.autocomplete,
                search_analyzer='standard')
            }
        )
    comp_address_ptt = es.String(
        analyzer=analyzers.adres,
        fields={
            'raw': es.String(index='not_analyzed'),
            'ngram': es.String(
                analyzer=analyzers.autocomplete, search_analyzer='standard')
            }
        )
    comp_address_pcode = es.String(
        analyzer=analyzers.adres,
        fields={
            'raw': es.String(index='not_analyzed'),
            'ngram': es.String(
                analyzer=analyzers.autocomplete, search_analyzer='standard')
            }
        )

    huisnummer = es.Integer(
        fields={'variation': es.String(analyzer=analyzers.huisnummer)})

    toevoeging = es.String(analyzer=analyzers.toevoeging,
        fields={'raw': es.String(index='not_analyzed')}
    )

    postcode = es.String(
        analyzer=analyzers.postcode,
        fields={
            'raw': es.String(index='not_analyzed'),
            'ngram': es.String(analyzer=analyzers.postcode_ng)})

    order = es.Integer()

    subtype = es.String(analyzer=analyzers.subtype)
    _display = es.String(index='not_analyzed')

    class Meta:
        index = settings.ELASTIC_INDICES['NUMMERAANDUIDING']
        all = es.MetaField(enabled=False)


class Bouwblok(es.DocType):
    """
    Elasticsearch doc for the bouwblok model
    """
    code = es.String(
        analyzer=analyzers.bouwblokid,
        fields={
            'raw': es.String(index='not_analyzed'),
        },
    )

    subtype = es.String(analyzer=analyzers.subtype)

    _display = es.String(index='not_analyzed')

    class Meta:
        index = settings.ELASTIC_INDICES['BAG']
        all = es.MetaField(enabled=False)


class Gebied(es.DocType):
    """
    Een vindbaar gebied

    Unesco
    Buurt
    Buurtcombinatie
    Stadsdeel
    Grootstedelijk
    Gemeente
    Woonplaats
    """

    id = es.String()

    _display = es.String(index='not_analyzed')

    naam = es.String(
        analyzer=analyzers.adres,
        fields={
            'raw': es.String(index='not_analyzed'),
            'ngram_edge': es.String(
                analyzer=analyzers.autocomplete, search_analyzer='standard'
            ),
            'ngram': es.String(analyzer=analyzers.ngram),
        }
    )

    g_code = es.String(
        analyzer=analyzers.autocomplete,
        fields={
            'raw': es.String(index='not_analyzed'),
            'ngram': es.String(analyzer=analyzers.ngram),
        }
    )

    subtype = es.String(analyzer=analyzers.subtype)

    centroid = es.GeoPoint()

    class Meta:
        index = settings.ELASTIC_INDICES['BAG']
        all = es.MetaField(enabled=False)


class ExactLocation(es.DocType):
    """
    Elasticsearch doc for exact location data
    """
    nummeraanduiding_id = es.String()
    address = es.String(index='not_analyzed')
    postcode_huisnummer = es.String(index='not_analyzed')
    postcode_toevoeging = es.String(index='not_analyzed', boost=5)
    subtype = es.String(analyzer=analyzers.subtype)
    geometrie = es.GeoPoint()

    _display = es.String(index='not_analyzed')

    class Meta:
        index = settings.ELASTIC_INDICES['BAG']
        all = es.MetaField(enabled=False)


def get_centroid(geom, transform=None):
    """
    Finds the centroid of a geometrie object
    An optional transform string can be given noting
    the name of the system to translate to, i.e. 'wgs84'
    """
    if not geom:
        return None

    result = geom.centroid
    if transform:
        result.transform(transform)
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
        doc.centroid = get_centroid(vo.geometrie, 'wgs84')
        doc.subtype_id = vo.id
        doc.order = analyzers.orderings['adres']


def add_standplaats(doc, sp: models.Standplaats):
    if sp:
        doc.centroid = get_centroid(sp.geometrie, 'wgs84')
        doc.subtype_id = sp.id
        doc.order = analyzers.orderings['adres']


def add_ligplaats(doc, lp: models.Ligplaats):
    if lp:
        doc.centroid = get_centroid(lp.geometrie, 'wgs84')
        doc.subtype_id = lp.id
        doc.order = analyzers.orderings['adres']


def from_ligplaats(l: models.Ligplaats):
    # id unique
    d = Ligplaats(_id=l.id)

    update_adres(d, l.hoofdadres)

    d.centroid = get_centroid(l.geometrie, 'wgs84')
    d.order = analyzers.orderings['adres']
    d._display = d.adres

    return d


def from_bouwblok(n: models.Bouwblok):
    doc = Bouwblok(_id=n.id)
    doc.code = n.code
    doc.subtype = 'bouwblok'
    doc._display = n.code
    return doc

def from_nummeraanduiding_ruimte(n: models.Nummeraanduiding):

    doc = Nummeraanduiding(_id=n.id)
    doc.adres = n.adres()
    doc.comp_address = "{0} {1}".format(n.openbare_ruimte.naam,
                                            n.toevoeging)
    doc.comp_address_nen = "{0} {1}".format(n.openbare_ruimte.naam_nen,
                                                n.toevoeging)
    doc.comp_address_ptt = "{0} {1}".format(n.openbare_ruimte.naam_ptt,
                                                n.toevoeging)
    doc.comp_address_pcode = "{0} {1}".format(n.postcode, n.toevoeging)
    doc.postcode = n.postcode
    doc.straatnaam = n.openbare_ruimte.naam
    doc.straatnaam_nen = n.openbare_ruimte.naam_nen
    doc.straatnaam_ptt = n.openbare_ruimte.naam_ptt
    doc.straatnaam_keyword = n.openbare_ruimte.naam
    doc.straatnaam_nen_keyword = n.openbare_ruimte.naam_nen
    doc.straatnaam_ptt_keyword = n.openbare_ruimte.naam_ptt
    doc.huisnummer = n.huisnummer
    doc.toevoeging = n.toevoeging

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

    doc._display = n.adres()

    return doc


def from_standplaats(s: models.Standplaats):

    d = Standplaats(_id=s.id)

    update_adres(d, s.hoofdadres)

    d.centroid = get_centroid(s.geometrie, 'wgs84')
    d.order = analyzers.orderings['adres']
    d._display = d.adres
    return d


def from_verblijfsobject(v: models.Verblijfsobject):
    d = Verblijfsobject(_id=v.id)
    update_adres(d, v.hoofdadres)
    d.centroid = get_centroid(v.geometrie, 'wgs84')

    d.bestemming = v.gebruiksdoel_omschrijving
    d.kamers = v.aantal_kamers
    d.oppervlakte = v.oppervlakte
    d.order = analyzers.orderings['adres']
    d._display = d.adres

    return d


def from_openbare_ruimte(o: models.OpenbareRuimte):
    d = OpenbareRuimte(_id=o.id)
    d.type = 'Openbare ruimte'
    # weg, water, spoorbaan, terrein, kunstwerk (brug), landschap,..
    d.subtype = o.get_type_display().lower()

    d.naam = o.naam
    d.naam_nen = o.naam_nen
    d.naam_ptt = o.naam_ptt

    postcodes = set()

    for a in o.adressen.all():
        if a.postcode:
            postcodes.add(a.postcode)

    d.postcode = list(postcodes)
    d.order = analyzers.orderings['openbare_ruimte']
    d._display = d.naam
    return d


def from_unesco(u: models.Unesco):
    d = Gebied(_id='unseco{}'.format(u.id))
    d.subtype = 'unesco'

    d._display = 'unesco %s' % u.naam
    d.subtype_id = u.id
    d.naam = d._display
    d.centroid = get_centroid(u.geometrie, 'wgs84')
    return d


def from_buurt(b: models.Buurt):
    d = Gebied(_id='buurt{}'.format(b.id))
    d.subtype = 'buurt'

    d.subtype_id = b.id
    d.naam = b.naam
    d._display = '{} - {}'.format(b.naam, b.code)
    d.g_code = b.code
    d.centroid = get_centroid(b.geometrie, 'wgs84')
    return d


def from_buurtcombinatie(bc: models.Buurtcombinatie):
    d = Gebied(_id='buurtcombinatie{}'.format(bc.id))
    d.subtype = 'buurtcombinatie'

    d.subtype_id = bc.id
    d.naam = bc.naam
    d._display = '{} - {}'.format(bc.naam, bc.code)
    d.g_code = bc.code
    d.centroid = get_centroid(bc.geometrie, 'wgs84')
    return d


def from_stadsdeel(sd: models.Stadsdeel):
    d = Gebied(_id='stadsdeel{}'.format(sd.id))
    d.subtype = 'stadsdeel'

    d.subtype_id = sd.id
    d.naam = sd.naam
    d._display = '{} - {}'.format(sd.naam, sd.code)
    d.g_code = sd.code
    d.centroid = get_centroid(sd.geometrie, 'wgs84')
    return d


def from_grootstedelijk(gs: models.Grootstedelijkgebied):
    d = Gebied()
    d = Gebied(_id='stadsdeel{}'.format(gs.id))
    d.subtype = 'grootstedelijk'

    d.subtype_id = gs.id
    d.naam = gs.naam
    d._display = gs.naam
    d.centroid = get_centroid(gs.geometrie, 'wgs84')
    return d


def from_gemeente(g: models.Gemeente):
    d = Gebied()
    d.subtype = 'gemeente'

    d.subtype_id = g.naam.lower()
    d.naam = g.naam
    d._display = '{} - {}'.format(g.naam, g.code)
    d.g_code = g.code
    # d.centroid = get_centroid(g.geometrie, 'wgs84')
    return d


def from_woonplaats(w: models.Woonplaats):
    d = Gebied()
    d.subtype = 'woonplaats'

    d.subtype_id = w.id
    d.naam = w.naam
    d._display = '{} - {}'.format(w.naam, w.landelijk_id)
    d.g_code = w.landelijk_id
    return d


def exact_from_nummeraanduiding(n: models.Nummeraanduiding):
    doc = ExactLocation(_id=n.id)
    doc.adres = n.adres()
    doc.nummeraanduiding_id = n.id
    doc.postcode_huisnummer = '{0} {1}'.format(n.postcode, n.huisnummer)
    doc.postcode_toevoeging = '{0} {1}'.format(n.postcode, n.toevoeging)
    doc.subtype='exact'

    # Retriving the geolocation is dependent on the geometrie
    if n.verblijfsobject:
        doc.geometrie = get_centroid(n.verblijfsobject.geometrie, 'wgs84')
    elif n.standplaats:
        doc.geometrie = get_centroid(n.standplaats.geometrie, 'wgs84')
    elif n.ligplaats:
        doc.geometrie = get_centroid(n.ligplaats.geometrie, 'wgs84')
    else:
        print('Failed to find geolocation for nummeraanduiduing {}'.format(n.id))
    doc._display = doc.adres

    return doc

