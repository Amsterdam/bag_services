import elasticsearch_dsl as es

from datasets.generic import analyzers


class KadastraalObject(es.DocType):
    aanduiding = es.String(analyzer=analyzers.kadastrale_aanduiding)
    adres = es.String(analyzer=analyzers.adres)

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
        d.naam = ks.naam_niet_natuurlijke_persoon
    else:
        titel = ks.titel_of_predikaat.omschrijving if ks.titel_of_predikaat else None

        d.natuurlijk_persoon = True
        d.naam = " ".join([part for part in (titel,
                                             ks.voorletters or ks.voornamen,
                                             ks.voorvoegsel,
                                             ks.geslachtsnaam) if part])
        d.geslachtsnaam = ks.geslachtsnaam
        d.geboortedatum = ks.geboortedatum

    return d


def from_kadastraal_object(ko):
    d = KadastraalObject(_id=ko.id)

    d.aanduiding = ko.id
    return d
