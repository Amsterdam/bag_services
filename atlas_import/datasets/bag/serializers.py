from rest_framework import serializers

from datasets.generic import rest
from . import models


class ExpandMixin(object):
    expand = False

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if 'request' in self.context:
            self.expand = 'full' in self.context['request'].query_params

            # make it possible to exclude geometrie from output as the response gets very big
            if 'nogeo' in self.context['request'].query_params:
                if 'geometrie'in self.fields:
                    del self.fields['geometrie']


class BagMixin(rest.DataSetSerializerMixin):
    dataset = 'bag'


class GebiedenMixin(rest.DataSetSerializerMixin):
    dataset = 'gebieden'


class Status(serializers.ModelSerializer):
    class Meta:
        model = models.Status
        fields = ('code', 'omschrijving')


class Eigendomsverhouding(serializers.ModelSerializer):
    class Meta:
        model = models.Eigendomsverhouding
        fields = ('code', 'omschrijving')


class Financieringswijze(serializers.ModelSerializer):
    class Meta:
        model = models.Financieringswijze
        fields = ('code', 'omschrijving')


class RedenAfvoer(serializers.ModelSerializer):
    class Meta:
        model = models.RedenAfvoer
        fields = ('code', 'omschrijving')


class RedenOpvoer(serializers.ModelSerializer):
    class Meta:
        model = models.RedenOpvoer
        fields = ('code', 'omschrijving')


class Gebruik(serializers.ModelSerializer):
    class Meta:
        model = models.Gebruik
        fields = ('code', 'omschrijving')


class Ligging(serializers.ModelSerializer):
    class Meta:
        model = models.Ligging
        fields = ('code', 'omschrijving')


class LocatieIngang(serializers.ModelSerializer):
    class Meta:
        model = models.LocatieIngang
        fields = ('code', 'omschrijving')


class Toegang(serializers.ModelSerializer):
    class Meta:
        model = models.Toegang
        fields = ('code', 'omschrijving')


class Woonplaats(BagMixin, rest.HALSerializer):
    _display = rest.DisplayField()

    class Meta:
        model = models.Woonplaats
        fields = (
            '_links',
            '_display',
            'landelijk_id',
        )


class Gemeente(BagMixin, rest.HALSerializer):
    _display = rest.DisplayField()

    class Meta:
        model = models.Gemeente
        fields = (
            '_links',
            '_display',
            'code',
        )


class GemeenteDetail(ExpandMixin, BagMixin, rest.HALSerializer):
    _display = rest.DisplayField()
    woonplaatsen = rest.RelatedSummaryField()

    class Meta:
        model = models.Gemeente
        fields = (
            '_links',
            '_display',
            'id',
            'code',
            'date_modified',
            'begin_geldigheid',
            'einde_geldigheid',

            'naam',
            'verzorgingsgebied',
            'woonplaatsen',
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.expand:
            self.fields['woonplaatsen'] = Woonplaats(many=True)


class OpenbareRuimte(BagMixin, rest.HALSerializer):
    _display = rest.DisplayField()

    class Meta:
        model = models.OpenbareRuimte
        fields = (
            '_links',
            '_display',
            'landelijk_id',
        )


class Nummeraanduiding(BagMixin, rest.HALSerializer):
    _display = rest.DisplayField()

    class Meta:
        model = models.Nummeraanduiding
        fields = (
            '_links',
            '_display',
            'landelijk_id',
            'hoofdadres',
        )


class Ligplaats(BagMixin, rest.HALSerializer):
    _display = rest.DisplayField()

    class Meta:
        model = models.Ligplaats
        fields = (
            '_links',
            '_display',
            'landelijk_id',
        )

    def display(self, obj):
        return obj.hoofdadres.adres()


class Standplaats(BagMixin, rest.HALSerializer):
    _display = rest.DisplayField()

    class Meta:
        model = models.Standplaats
        fields = (
            '_links',
            '_display',
            'landelijk_id',
        )


class Verblijfsobject(BagMixin, rest.HALSerializer):
    _display = rest.DisplayField()

    class Meta:
        model = models.Verblijfsobject
        fields = (
            '_links',
            '_display',
            'landelijk_id',
        )


class Pand(BagMixin, rest.HALSerializer):
    _display = rest.DisplayField()

    class Meta:
        model = models.Pand
        fields = (
            '_links',
            '_display',
            'landelijk_id',
        )


class Stadsdeel(GebiedenMixin, rest.HALSerializer):
    _display = rest.DisplayField()

    class Meta:
        model = models.Stadsdeel
        fields = (
            '_links',
            '_display',
            'code',
            'naam',
        )


class StadsdeelDetail(ExpandMixin, GebiedenMixin, rest.HALSerializer):
    _display = rest.DisplayField()
    buurten = rest.RelatedSummaryField()
    gebiedsgerichtwerken = rest.RelatedSummaryField()
    buurtcombinaties = rest.RelatedSummaryField()
    gemeente = Gemeente()

    class Meta:
        model = models.Stadsdeel
        fields = (
            '_links',
            '_display',
            'id',
            'code',
            'date_modified',
            'begin_geldigheid',
            'einde_geldigheid',

            'naam',
            'gemeente',
            'ingang_cyclus',
            'brondocument_naam',
            'brondocument_datum',
            'geometrie',
            'buurten',
            'buurtcombinaties',
            'gebiedsgerichtwerken',
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.expand:
            self.fields['gemeente'] = GemeenteDetail(context=self.context)


class Buurtcombinatie(GebiedenMixin, rest.HALSerializer):
    _display = rest.DisplayField()

    class Meta:
        model = models.Buurtcombinatie
        fields = (
            '_links',
            '_display',
            'naam',
        )


class BuurtcombinatieDetail(ExpandMixin, GebiedenMixin, rest.HALSerializer):
    _display = rest.DisplayField()
    stadsdeel = Stadsdeel()
    buurten = rest.RelatedSummaryField()

    class Meta:
        model = models.Buurtcombinatie
        fields = (
            '_links',
            '_display',
            'id',
            'naam',
            'code',
            'vollcode',
            'brondocument_naam',
            'brondocument_datum',
            'geometrie',
            'begin_geldigheid',
            'einde_geldigheid',
            'stadsdeel',
            'buurten',
        )


class Buurt(GebiedenMixin, rest.HALSerializer):
    _display = rest.DisplayField()

    class Meta:
        model = models.Buurt
        fields = (
            '_links',
            '_display',
            'code',
            'naam',
        )


class BuurtDetail(ExpandMixin, GebiedenMixin, rest.HALSerializer):
    _display = rest.DisplayField()
    bouwblokken = rest.RelatedSummaryField()
    ligplaatsen = rest.RelatedSummaryField()
    standplaatsen = rest.RelatedSummaryField()
    verblijfsobjecten = rest.RelatedSummaryField()
    buurtcombinatie = Buurtcombinatie()
    stadsdeel = Stadsdeel()

    class Meta:
        model = models.Buurt
        fields = (
            '_links',
            '_display',
            'id',
            'code',
            'vollcode',

            'naam',
            'stadsdeel',
            'ingang_cyclus',
            'brondocument_naam',
            'brondocument_datum',
            'begin_geldigheid',
            'einde_geldigheid',
            'geometrie',
            'buurtcombinatie',
            'bouwblokken',
            'ligplaatsen',
            'standplaatsen',
            'verblijfsobjecten',
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.expand:
            self.fields['stadsdeel'] = StadsdeelDetail(context=self.context)
            self.fields['buurtcombinatie'] = BuurtcombinatieDetail(context=self.context)


class Bouwblok(GebiedenMixin, rest.HALSerializer):
    _display = rest.DisplayField()

    class Meta:
        model = models.Bouwblok
        fields = (
            '_links',
            '_display',
            'id',
        )


class Gebiedsgerichtwerken(GebiedenMixin, rest.HALSerializer):
    _display = rest.DisplayField()

    class Meta:
        model = models.Gebiedsgerichtwerken
        fields = (
            '_links',
            '_display',
            'naam',
        )


class Grootstedelijkgebied(GebiedenMixin, rest.HALSerializer):
    _display = rest.DisplayField()

    class Meta:
        model = models.Grootstedelijkgebied
        fields = (
            '_links',
            '_display',
            'naam',
        )


class Unesco(GebiedenMixin, rest.HALSerializer):
    _display = rest.DisplayField()

    class Meta:
        model = models.Unesco
        fields = (
            '_links',
            '_display',
            'naam',
        )


class WoonplaatsDetail(BagMixin, rest.HALSerializer):
    _display = rest.DisplayField()
    openbare_ruimtes = rest.RelatedSummaryField()
    gemeente = Gemeente()

    class Meta:
        model = models.Woonplaats
        fields = (
            '_links',
            '_display',
            'id',
            'landelijk_id',
            'date_modified',
            'document_mutatie',
            'document_nummer',
            'begin_geldigheid',
            'einde_geldigheid',
            'mutatie_gebruiker',

            'naam',
            'naam_ptt',
            'gemeente',
            'openbare_ruimtes'
        )


class OpenbareRuimteDetail(BagMixin, rest.HALSerializer):
    _display = rest.DisplayField()
    status = Status()
    type = serializers.CharField(source='get_type_display')
    adressen = rest.RelatedSummaryField()
    woonplaats = Woonplaats()

    class Meta:
        model = models.OpenbareRuimte
        fields = (
            '_links',
            '_display',
            'id',
            'landelijk_id',
            'code',
            'date_modified',
            'document_mutatie',
            'document_nummer',
            'begin_geldigheid',
            'einde_geldigheid',
            'mutatie_gebruiker',
            'status',
            'bron',
            'geometrie',

            'type',
            'naam',
            'naam_ptt',
            'naam_nen',
            'straat_nummer',
            'woonplaats',
            'adressen',

            'geometrie',
        )


class LigplaatsDetail(ExpandMixin, BagMixin, rest.HALSerializer):
    _display = rest.DisplayField()

    status = Status()
    hoofdadres = Nummeraanduiding()
    buurt = Buurt()
    adressen = rest.RelatedSummaryField()

    class Meta:
        model = models.Ligplaats
        fields = (
            '_links',
            '_display',
            'id',
            'landelijk_id',
            'date_modified',
            'document_mutatie',
            'document_nummer',
            'begin_geldigheid',
            'einde_geldigheid',
            'mutatie_gebruiker',
            'status',
            'bron',

            'geometrie',
            'hoofdadres',
            'adressen',
            'buurt',
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.expand:
            self.fields['buurt'] = BuurtDetail(context=self.context)


class NummeraanduidingDetail(BagMixin, rest.HALSerializer):
    _display = rest.DisplayField()
    status = Status()
    type = serializers.CharField(source='get_type_display')
    buurt = Buurt()
    buurtcombinatie = Buurtcombinatie()
    stadsdeel = Stadsdeel()
    openbare_ruimte = OpenbareRuimte()
    woonplaats = Woonplaats()
    bouwblok = Bouwblok()

    class Meta:
        model = models.Nummeraanduiding
        fields = (
            '_links',
            '_display',
            'id',
            'landelijk_id',
            'date_modified',
            'document_mutatie',
            'document_nummer',
            'begin_geldigheid',
            'einde_geldigheid',
            'mutatie_gebruiker',
            'status',
            'bron',
            'adres',

            'postcode',
            'huisnummer',
            'huisletter',
            'huisnummer_toevoeging',
            'type',
            'adres_nummer',
            'openbare_ruimte',
            'hoofdadres',
            'ligplaats',
            'standplaats',
            'verblijfsobject',
            'buurt',
            'buurtcombinatie',
            'stadsdeel',
            'woonplaats',
            'bouwblok',
        )


class StandplaatsDetail(ExpandMixin, BagMixin, rest.HALSerializer):
    _display = rest.DisplayField()
    status = Status()
    adressen = rest.RelatedSummaryField()
    hoofdadres = Nummeraanduiding()
    buurt = Buurt()

    class Meta:
        model = models.Standplaats
        fields = (
            '_links',
            '_display',
            'id',
            'landelijk_id',
            'date_modified',
            'document_mutatie',
            'document_nummer',
            'begin_geldigheid',
            'einde_geldigheid',
            'mutatie_gebruiker',
            'status',
            'bron',

            'geometrie',
            'hoofdadres',
            'adressen',
            'buurt',
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.expand:
            self.fields['buurt'] = BuurtDetail(context=self.context)


class KadastraalObjectField(serializers.HyperlinkedRelatedField):
    view_name = "kadastraalobject-detail"


class VerblijfsobjectDetail(ExpandMixin, BagMixin, rest.HALSerializer):
    _display = rest.DisplayField()
    status = Status()
    eigendomsverhouding = Eigendomsverhouding()
    financieringswijze = Financieringswijze()
    gebruik = Gebruik()
    ligging = Ligging()
    locatie_ingang = LocatieIngang()
    toegang = Toegang()
    status_coordinaat = serializers.SerializerMethodField()
    type_woonobject = serializers.SerializerMethodField()
    gebruiksdoel = serializers.SerializerMethodField()
    hoofdadres = Nummeraanduiding()
    buurt = Buurt()
    reden_afvoer = RedenAfvoer()
    reden_opvoer = RedenOpvoer()
    kadastrale_objecten = rest.RelatedSummaryField()
    panden = rest.RelatedSummaryField()
    adressen = rest.RelatedSummaryField()
    rechten = rest.RelatedSummaryField()
    beperkingen = rest.RelatedSummaryField()

    class Meta:
        model = models.Verblijfsobject
        fields = (
            '_links',
            '_display',
            'id',
            'landelijk_id',
            'date_modified',
            'document_mutatie',
            'document_nummer',
            'begin_geldigheid',
            'einde_geldigheid',
            'mutatie_gebruiker',
            'status',
            'bron',

            'geometrie',
            'gebruiksdoel',
            'oppervlakte',
            'bouwlaag_toegang',
            'status_coordinaat',
            'verhuurbare_eenheden',
            'bouwlagen',
            'type_woonobject',
            'woningvoorraad',
            'aantal_kamers',
            'reden_afvoer',
            'reden_opvoer',
            'eigendomsverhouding',
            'financieringswijze',
            'gebruik',
            'ligging',
            'locatie_ingang',
            'toegang',
            'hoofdadres',
            'adressen',
            'buurt',
            'panden',
            'kadastrale_objecten',
            'rechten',
            'beperkingen',
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.expand:
            self.fields['adressen'] = serializers.ManyRelatedField(
                child_relation=Nummeraanduiding())
            self.fields['panden'] = serializers.ManyRelatedField(
                child_relation=PandDetail())
            self.fields['buurt'] = BuurtDetail(context=self.context)

    def get_gebruiksdoel(self, obj):
        return dict(
            code=obj.gebruiksdoel_code,
            omschrijving=obj.gebruiksdoel_omschrijving,
        )

    def get_status_coordinaat(self, obj):
        return dict(
            code=obj.status_coordinaat_code,
            omschrijving=obj.status_coordinaat_omschrijving,
        )

    def get_type_woonobject(self, obj):
        return dict(
            code=obj.type_woonobject_code,
            omschrijving=obj.type_woonobject_omschrijving,
        )


class PandDetail(ExpandMixin, BagMixin, rest.HALSerializer):
    _display = rest.DisplayField()
    status = Status()
    verblijfsobjecten = rest.RelatedSummaryField()
    bouwblok = Bouwblok()

    class Meta:
        model = models.Pand
        fields = (
            '_links',
            '_display',
            'id',
            'landelijk_id',
            'date_modified',
            'document_mutatie',
            'document_nummer',
            'status',

            'geometrie',

            'bouwjaar',
            'hoogste_bouwlaag',
            'laagste_bouwlaag',
            'pandnummer',

            'verblijfsobjecten',
            'bouwblok',

            'begin_geldigheid',
            'einde_geldigheid',
            'mutatie_gebruiker',

        )


class BouwblokDetail(GebiedenMixin, rest.HALSerializer):
    _display = rest.DisplayField()
    panden = rest.RelatedSummaryField()
    buurt = Buurt()
    meetbouten = serializers.SerializerMethodField()

    class Meta:
        model = models.Bouwblok
        fields = (
            '_links',
            '_display',
            'id',
            'code',
            'buurt',
            'ingang_cyclus',
            'begin_geldigheid',
            'einde_geldigheid',
            'geometrie',
            'panden',
            'meetbouten',
        )

    def get_meetbouten(self, obj):
        link = "/meetbouten/meetbout/?bouwbloknummer={}".format(obj.code)
        req = self.context.get('request')
        if req:
            return req.build_absolute_uri(link)

        return link


class GebiedsgerichtwerkenDetail(GebiedenMixin, rest.HALSerializer):
    _display = rest.DisplayField()
    stadsdeel = Stadsdeel()

    class Meta:
        model = models.Gebiedsgerichtwerken
        fields = (
            '_links',
            '_display',
            'naam',
            'code',
            'stadsdeel',
            'geometrie',
        )


class GrootstedelijkgebiedDetail(GebiedenMixin, rest.HALSerializer):
    _display = rest.DisplayField()

    class Meta:
        model = models.Grootstedelijkgebied
        fields = (
            '_links',
            '_display',
            'naam',
            'geometrie',
        )


class UnescoDetail(GebiedenMixin, rest.HALSerializer):
    _display = rest.DisplayField()

    class Meta:
        model = models.Unesco
        fields = (
            '_links',
            '_display',
            'naam',
            'geometrie',
        )
