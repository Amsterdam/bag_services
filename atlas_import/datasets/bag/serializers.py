from rest_framework import serializers, reverse

from datasets.generic import rest
from . import models


class BagMixin(rest.DataSetSerializerMixin):
    dataset = 'bag'


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
    class Meta:
        model = models.Woonplaats
        fields = (
            '_links',
            'code',
        )


class WoonplaatsDetail(BagMixin, rest.HALSerializer):
    gemeente = 'Gemeente'

    class Meta:
        model = models.Woonplaats
        fields = (
            '_links',
            'code',
            'date_modified',
            'document_mutatie',
            'document_nummer',

            'naam',
            'naam_ptt',
            'gemeente',
        )


class OpenbareRuimte(BagMixin, rest.HALSerializer):
    class Meta:
        model = models.OpenbareRuimte
        fields = (
            '_links',
            'code',
        )


class OpenbareRuimteDetail(BagMixin, rest.HALSerializer):
    status = Status()
    type = serializers.CharField(source='get_type_display')
    woonplaats = Woonplaats()

    class Meta:
        model = models.OpenbareRuimte
        fields = (
            '_links',
            'id',
            'code',
            'date_modified',
            'document_mutatie',
            'document_nummer',
            'status',
            'bron',

            'type',
            'naam',
            'naam_ptt',
            'naam_nen',
            'straat_nummer',
            'woonplaats',
        )


class Ligplaats(BagMixin, rest.HALSerializer):
    class Meta:
        model = models.Ligplaats
        fields = (
            '_links',
            'identificatie',
        )


class LigplaatsDetail(BagMixin, rest.HALSerializer):
    status = Status()
    hoofdadres = serializers.HyperlinkedRelatedField(
        source='hoofdadres.id',
        view_name='nummeraanduiding-detail',
        read_only=True,
    )

    class Meta:
        model = models.Ligplaats
        fields = (
            '_links',
            'id',
            'identificatie',
            'date_modified',
            'document_mutatie',
            'document_nummer',
            'status',
            'bron',

            'geometrie',
            'hoofdadres',
            'adressen',
            'buurt',
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        expand = 'full' in self.context['request'].query_params if self.context else False

        if expand:
            self.fields['adressen'] = serializers.ManyRelatedField(child_relation=Nummeraanduiding())


class Nummeraanduiding(BagMixin, rest.HALSerializer):
    class Meta:
        model = models.Nummeraanduiding
        fields = (
            '_links',
            'code',
        )


class NummeraanduidingDetail(BagMixin, rest.HALSerializer):
    status = Status()
    openbare_ruimte = OpenbareRuimte()
    ligplaats = Ligplaats()
    verblijfsobject = 'Verblijfsobject'
    standplaats = 'Standplaats'
    verblijfsobject = 'Verblijfsobject'
    type = serializers.CharField(source='get_type_display')

    class Meta:
        model = models.Nummeraanduiding
        fields = (
            '_links',
            'id',
            'code',
            'date_modified',
            'document_mutatie',
            'document_nummer',
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
        )


class Standplaats(BagMixin, rest.HALSerializer):
    class Meta:
        model = models.Standplaats
        fields = (
            '_links',
            'identificatie',
        )


class RelatedSummaryField(serializers.HyperlinkedRelatedField):
    view_name = ''


class StandplaatsDetail(BagMixin, rest.HALSerializer):
    status = Status()
    adressen = serializers.SerializerMethodField()
    hoofdadres = serializers.HyperlinkedRelatedField(
        source='hoofdadres.id',
        view_name='nummeraanduiding-detail',
        read_only=True,
    )

    class Meta:
        model = models.Standplaats
        fields = (
            '_links',
            'id',
            'identificatie',
            'date_modified',
            'document_mutatie',
            'document_nummer',
            'status',
            'bron',

            'geometrie',
            'hoofdadres',
            'adressen',
            'buurt',
        )

    def adressen(self, obj):
        import ipdb;
        ipdb.set_trace()
        return dict(
            count=len(obj),
            url=reverse.reverse('nummeraanduiding-list', request=self.context['request'])
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        expand = 'full' in self.context['request'].query_params

        if expand:
            self.fields['adressen'] = serializers.ManyRelatedField(child_relation=Nummeraanduiding())


class KadastraalObjectField(serializers.HyperlinkedRelatedField):
    view_name = "kadastraalobject-detail"


class Verblijfsobject(BagMixin, rest.HALSerializer):
    class Meta:
        model = models.Verblijfsobject
        fields = (
            '_links',
            'identificatie',
        )


class VerblijfsobjectDetail(BagMixin, rest.HALSerializer):
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
    hoofdadres = serializers.HyperlinkedRelatedField(
        source='hoofdadres.id',
        view_name='nummeraanduiding-detail',
        read_only=True,
    )
    kadastrale_objecten = KadastraalObjectField(many=True, read_only=True)

    class Meta:
        model = models.Verblijfsobject
        fields = (
            '_links',
            'id',
            'identificatie',
            'date_modified',
            'document_mutatie',
            'document_nummer',
            'status',
            'bron',

            'geometrie',
            'gebruiksdoel',
            'oppervlakte',
            'bouwlaag_toegang',
            'status_coordinaat',
            'bouwlagen',
            'type_woonobject',
            'woningvoorraad',
            'aantal_kamers',
            'reden_afvoer',
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
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        expand = 'full' in self.context['request'].query_params

        if expand:
            self.fields['adressen'] = serializers.ManyRelatedField(child_relation=Nummeraanduiding())
            self.fields['panden'] = serializers.ManyRelatedField(child_relation=Pand())

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


class Pand(BagMixin, rest.HALSerializer):
    class Meta:
        model = models.Pand
        fields = (
            '_links',
            'identificatie',
        )


class PandDetail(BagMixin, rest.HALSerializer):
    status = Status()
    verblijfsobjecten = Verblijfsobject(many=True)

    class Meta:
        model = models.Pand
        fields = (
            '_links',
            'id',
            'identificatie',
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
        )


class Gemeente(BagMixin, rest.HALSerializer):
    class Meta:
        model = models.Gemeente
        fields = (
            '_links',
            'code',
        )


class GemeenteDetail(BagMixin, rest.HALSerializer):
    class Meta:
        model = models.Gemeente
        fields = (
            '_links',
            'id',
            'code',
            'date_modified',

            'naam',
            'verzorgingsgebied',
        )


class GebiedenMixin(rest.DataSetSerializerMixin):
    dataset = 'gebieden'


class Stadsdeel(GebiedenMixin, rest.HALSerializer):
    class Meta:
        model = models.Stadsdeel
        fields = (
            '_links',
            'code',
            'naam',
        )


class StadsdeelDetail(GebiedenMixin, rest.HALSerializer):
    class Meta:
        model = models.Stadsdeel
        fields = (
            '_links',
            'id',
            'code',
            'date_modified',

            'naam',
            'gemeente',
            'ingang_cyclus',
            'brondocument_naam',
            'brondocument_datum',
            'geometrie',
        )


class Buurt(GebiedenMixin, rest.HALSerializer):
    class Meta:
        model = models.Buurt
        fields = (
            '_links',
            'code',
        )


class BuurtDetail(GebiedenMixin, rest.HALSerializer):
    stadsdeel = Stadsdeel()

    class Meta:
        model = models.Buurt
        fields = (
            '_links',
            'code',

            'naam',
            'stadsdeel',
            'ingang_cyclus',
            'brondocument_naam',
            'brondocument_datum',
            'geometrie',
        )


class Bouwblok(GebiedenMixin, rest.HALSerializer):
    class Meta:
        model = models.Bouwblok
        fields = (
            '_links',
            'code',
        )


class BouwblokDetail(GebiedenMixin, rest.HALSerializer):
    buurt = Buurt()

    class Meta:
        model = models.Bouwblok
        fields = (
            '_links',
            'code',
            'buurt',
            'ingang_cyclus',
            'geometrie',
        )


class Buurtcombinatie(GebiedenMixin, rest.HALSerializer):
    class Meta:
        model = models.Buurtcombinatie
        fields = (
            '_links',
            'naam',
        )


class BuurtcombinatieDetail(GebiedenMixin, rest.HALSerializer):
    class Meta:
        model = models.Buurtcombinatie
        fields = (
            '_links',
            'naam',
            'code',
            'vollcode',
            'brondocument_naam',
            'brondocument_datum',
            'ingang_cyclus',
            'geometrie',
        )


class Gebiedsgerichtwerken(GebiedenMixin, rest.HALSerializer):
    class Meta:
        model = models.Gebiedsgerichtwerken
        fields = (
            '_links',
            'naam',
        )


class GebiedsgerichtwerkenDetail(GebiedenMixin, rest.HALSerializer):
    stadsdeel = Stadsdeel()

    class Meta:
        model = models.Gebiedsgerichtwerken
        fields = (
            '_links',
            'naam',
            'code',
            'stadsdeel',
            'geometrie',
        )


class Grootstedelijkgebied(GebiedenMixin, rest.HALSerializer):
    class Meta:
        model = models.Grootstedelijkgebied
        fields = (
            '_links',
            'naam',
        )


class GrootstedelijkgebiedDetail(GebiedenMixin, rest.HALSerializer):
    class Meta:
        model = models.Grootstedelijkgebied
        fields = (
            '_links',
            'naam',
            'geometrie',
        )


class Unesco(GebiedenMixin, rest.HALSerializer):
    class Meta:
        model = models.Unesco
        fields = (
            '_links',
            'naam',
        )


class UnescoDetail(GebiedenMixin, rest.HALSerializer):
    class Meta:
        model = models.Unesco
        fields = (
            '_links',
            'naam',
            'geometrie',
        )
