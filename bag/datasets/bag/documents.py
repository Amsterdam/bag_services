# Python
# Packages

import elasticsearch_dsl as es
from django.conf import settings

from search import analyzers
from . import models


naam_fields = {
    'raw': es.Keyword(normalizer=analyzers.lowercase),
    'ngram': es.Text(
        analyzer=analyzers.autocomplete, search_analyzer='standard'),
}

postcode_fields = {
    'raw': es.Keyword(
        normalizer=analyzers.lowercase),
}


text_fields = {
    'raw': es.Keyword(),
    'ngram_edge': es.Text(
        analyzer=analyzers.autocomplete, search_analyzer='standard'
    ),
    'ngram': es.Text(analyzer=analyzers.ngram),
    'keyword': es.Keyword(normalizer=analyzers.lowercase),
}


class Nummeraanduiding(es.DocType):
    """
    All bag objects should have one or more adresses

    Een nummeraanduiding, in de volksmond ook wel adres genoemd, is een door
    het bevoegde gemeentelijke orgaan als
    zodanig toegekende aanduiding van een verblijfsobject, standplaats of
    ligplaats.

    [Stelselpedia](http://www.amsterdam.nl/stelselpedia/bag-index/catalogus-bag/objectklasse-2/)
    """
    straatnaam = es.Text(
        analyzer=analyzers.adres,
        fields={
            'raw': es.Keyword(),
            'ngram_edge': es.Text(
                analyzer=analyzers.autocomplete, search_analyzer='standard'
            ),
            'ngram': es.Text(analyzer=analyzers.ngram),
        }
    )

    straatnaam_keyword = es.Keyword()

    straatnaam_nen = es.Text(
        analyzer=analyzers.adres,
        fields={
            'raw': es.Keyword(),
            'ngram_edge': es.Text(
                analyzer=analyzers.autocomplete, search_analyzer='standard'
            ),
            'ngram': es.Text(analyzer=analyzers.ngram),
        }
    )

    straatnaam_nen_keyword = es.Keyword()

    straatnaam_ptt = es.Text(
        analyzer=analyzers.adres, fields={
            'raw': es.Keyword(),
            'ngram_edge': es.Text(
                analyzer=analyzers.autocomplete, search_analyzer='standard'
            ),
            'ngram': es.Text(analyzer=analyzers.ngram),
            'keyword': es.Keyword(normalizer=analyzers.lowercase),

        }
    )

    straatnaam_ptt_keyword = es.Keyword()

    adres = es.Text(
        analyzer=analyzers.adres,
        fields={
            'raw': es.Keyword(),
            'ngram_edge': es.Text(
                analyzer=analyzers.autocomplete, search_analyzer='standard'
            ),
            'ngram': es.Text(analyzer=analyzers.ngram)
        }
    )

    comp_address = es.Text(
        analyzer=analyzers.adres, fields={
            'raw': es.Keyword(),
            'ngram': es.Text(
                analyzer=analyzers.autocomplete, search_analyzer='standard')
        }
    )
    comp_address_nen = es.Text(
        analyzer=analyzers.adres,
        fields={
            'raw': es.Keyword(),
            'ngram': es.Text(
                analyzer=analyzers.autocomplete,
                search_analyzer='standard')
        }
    )
    comp_address_ptt = es.Text(
        analyzer=analyzers.adres,
        fields={
            'raw': es.Keyword(),
            'ngram': es.Text(
                analyzer=analyzers.autocomplete, search_analyzer='standard')
        }
    )
    comp_address_pcode = es.Text(
        analyzer=analyzers.adres,
        fields={
            'raw': es.Keyword(),
            'ngram': es.Text(
                analyzer=analyzers.autocomplete, search_analyzer='standard')
        }
    )

    huisnummer = es.Integer(
        fields={'variation': es.Text(analyzer=analyzers.huisnummer)})

    toevoeging = es.Text(
        analyzer=analyzers.toevoeging,
        fields={'keyword': es.Keyword()}
    )

    postcode = es.Text(
        analyzer=analyzers.postcode,
        fields=postcode_fields,
    )

    order = es.Integer()

    hoofdadres = es.Boolean()
    status = es.Nested(
        properties={
            'code': es.Keyword(normalizer=analyzers.lowercase),
            'omschrijving': es.Text()
        }
    )

    vbo_status = es.Nested(
        properties={
            'code': es.Keyword(normalizer=analyzers.lowercase),
            'omschrijving': es.Text()
        }
    )

    subtype = es.Keyword()
    _display = es.Keyword()

    class Meta:
        index = settings.ELASTIC_INDICES['NUMMERAANDUIDING']


class Bouwblok(es.DocType):
    """
    Bouwblok searchable fields.
    """
    code = es.Text(
        analyzer=analyzers.bouwblokid,
        fields={
            'keyword': es.Keyword()
        },
    )

    subtype = es.Keyword()

    _display = es.Keyword()

    class Meta:
        index = settings.ELASTIC_INDICES['BAG_BOUWBLOK']


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

    id = es.Keyword()

    _display = es.Keyword()

    naam = es.Text(
        analyzer=analyzers.adres,
        fields={
            'keyword': es.Keyword(),
            'ngram_edge': es.Text(
                analyzer=analyzers.autocomplete,
                search_analyzer='standard'
            ),
            'ngram': es.Text(analyzer=analyzers.ngram),
        }
    )

    naam_nen = es.Text(
        analyzer=analyzers.adres,
        fields=text_fields
    )

    naam_ptt = es.Text(
        analyzer=analyzers.adres,
        fields=text_fields
    )

    postcode = es.Text(
        analyzer=analyzers.postcode,
        search_analyzer='standard',
        fields=postcode_fields
    )

    g_code = es.Text(
        analyzer=analyzers.autocomplete,
        fields={
            'keyword': es.Keyword(),
            'ngram': es.Text(analyzer=analyzers.ngram),
        }
    )

    # gebied order
    order = es.Integer()

    subtype = es.Keyword()

    centroid = es.GeoPoint()

    class Meta:
        index = settings.ELASTIC_INDICES['BAG_GEBIED']


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
    doc._display = '{} (bouwblok)'.format(n.code)
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

    doc.hoofdadres = n.hoofdadres

    if n.status:
        doc.status.append({
            'code': n.status.code,
            'omschrijving': n.status.omschrijving
        })

    # verblijfsobject status
    if n.adresseerbaar_object and n.adresseerbaar_object.status:
        doc.vbo_status.append({
            'code': n.adresseerbaar_object.status.code,
            'omschrijving': n.adresseerbaar_object.status.omschrijving
        })

    if n.bron:
        doc.bron = n.bron.omschrijving

    # if not doc.subtype:
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

    # We can have many descriptions and extended descriptions,
    # we add all of them in a text field here:
    descriptions = []
    for gd in v.gebruiksdoelen.all():
        descriptions.extend([gd.omschrijving, gd.omschrijving_plus])
    d.bestemming = ' '.join(descriptions)

    d.kamers = v.aantal_kamers
    d.oppervlakte = v.oppervlakte
    d.order = analyzers.orderings['adres']
    d._display = d.adres

    return d


def from_openbare_ruimte(o: models.OpenbareRuimte):
    d = Gebied(_id=o.id)
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

    d.centroid = get_centroid(o.geometrie, 'wgs84')

    return d


def from_unesco(u: models.Unesco):
    d = Gebied(_id='unseco{}'.format(u.id))

    d.subtype = 'unesco'

    d._display = '{} ({})'.format(u.naam, d.subtype)

    d.subtype_id = u.id
    d.naam = u.naam
    d.centroid = get_centroid(u.geometrie, 'wgs84')
    d.order = 1
    return d


def from_buurt(b: models.Buurt):
    d = Gebied(_id='buurt{}'.format(b.id))
    d.subtype = 'buurt'

    d.subtype_id = b.id
    d.naam = b.naam
    d._display = '{} ({})'.format(b.naam, d.subtype)
    d.g_code = b.code
    d.centroid = get_centroid(b.geometrie, 'wgs84')
    d.order = 6
    return d


def from_buurtcombinatie(bc: models.Buurtcombinatie):
    d = Gebied(_id='buurtcombinatie{}'.format(bc.id))
    d.subtype = 'buurtcombinatie'

    d.subtype_id = bc.id
    d.naam = bc.naam
    d._display = '{} ({})'.format(bc.naam, 'wijk')
    d.g_code = bc.code
    d.order = 5
    d.centroid = get_centroid(bc.geometrie, 'wgs84')
    return d


def from_gebiedsgerichtwerken(gg: models.Gebiedsgerichtwerken):
    d = Gebied(_id='gebiedsgericht{}'.format(gg.id))
    d.subtype = 'gebiedsgerichtwerken'

    d.subtype_id = gg.id
    d.naam = gg.naam
    d._display = '{} ({})'.format(gg.naam, 'gebiedsgericht werken')
    d.g_code = gg.code
    d.centroid = get_centroid(gg.geometrie, 'wgs84')
    d.order = 4
    return d


def from_stadsdeel(sd: models.Stadsdeel):
    d = Gebied(_id='stadsdeel{}'.format(sd.id))
    d.subtype = 'stadsdeel'

    d.subtype_id = sd.id
    d.naam = sd.naam
    d._display = '{} ({})'.format(sd.naam, d.subtype)
    d.g_code = sd.code
    d.order = 3
    d.centroid = get_centroid(sd.geometrie, 'wgs84')
    return d


def from_grootstedelijk(gs: models.Grootstedelijkgebied):
    d = Gebied(_id='stadsdeel{}'.format(gs.id))
    d.subtype = 'grootstedelijk'

    d.subtype_id = gs.id
    d.naam = gs.naam
    d._display = '{} ({})'.format(gs.naam, 'grootstedelijk gebied')
    d.centroid = get_centroid(gs.geometrie, 'wgs84')
    d.order = 2
    return d


def from_gemeente(g: models.Gemeente):
    d = Gebied(_id='gemeente{}'.format(g.id))
    d.subtype = 'gemeente'

    d.subtype_id = g.naam.lower()
    d.naam = g.naam
    d._display = '{} ({})'.format(g.naam, d.subtype)
    d.g_code = g.code
    d.order = 1
    return d


def from_woonplaats(w: models.Woonplaats):
    d = Gebied(_id='woonplaats{}'.format(g.id))
    d.subtype = 'woonplaats'

    d.subtype_id = w.id
    d.naam = w.naam
    d._display = '{} ({})'.format(w.naam, d.subtype)
    d.g_code = w.landelijk_id
    d.order = 2
    return d
