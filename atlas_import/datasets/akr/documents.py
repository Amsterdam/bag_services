import elasticsearch_dsl as es

from datasets.generic import analyzers


class KadastraalObject(es.DocType):
    aanduiding = es.String(analyzer=analyzers.kadastrale_aanduiding)
    adres = es.String(analyzer=analyzers.adres)
    centroid = es.GeoPoint()

    class Meta:
        index = 'brk'


class KadastraalSubject(es.DocType):
    naam = es.String(analyzer=analyzers.naam)
    natuurlijk_persoon = es.Boolean()
    geslachtsnaam = es.String(analyzer=analyzers.naam)
    geboortedatum = es.Date()

    class Meta:
        index = 'brk'


def from_kadastraal_subject(ks):
    d = KadastraalSubject(_id=ks.pk)

    if ks.naam_niet_natuurlijke_persoon:
        d.natuurlijk_persoon = False
    else:
        d.natuurlijk_persoon = True

        d.geslachtsnaam = ks.geslachtsnaam
        d.geboortedatum = ks.geboortedatum

    d.naam = ks.volledige_naam()

    return d


def from_kadastraal_object(ko):
    d = KadastraalObject(_id=ko.id)

    d.aanduiding = ko.id
    if ko.geometrie:
        centroid = ko.geometrie
        centroid.transform('wgs84')

        d.centroid = centroid.coords

    return d
