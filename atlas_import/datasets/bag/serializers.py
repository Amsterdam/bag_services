from rest_framework import serializers

from . import models
from datasets.generic import rest


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
            'date_modified',
            'document_mutatie',
            'document_nummer',

            'naam',
            'naam_ptt',
            'gemeente',
        )


class OpenbareRuimte(BagMixin, rest.HALSerializer):
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


class Nummeraanduiding(BagMixin, rest.HALSerializer):
    status = Status()
    openbare_ruimte = OpenbareRuimte()
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


class Ligplaats(BagMixin, rest.HALSerializer):
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


class Standplaats(BagMixin, rest.HALSerializer):
    status = Status()
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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        expand = 'full' in self.context['request'].query_params

        if expand:
            self.fields['adressen'] = serializers.ManyRelatedField(child_relation=Nummeraanduiding())


class KadastraalObjectField(serializers.HyperlinkedRelatedField):
    view_name = "kadastraalobject-detail"


class Verblijfsobject(BagMixin, rest.HALSerializer):
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
    status = Status()

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


class GebiedenMixin(rest.DataSetSerializerMixin):
    dataset = 'gebieden'


class Gemeente(GebiedenMixin, rest.HALSerializer):
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


class Stadsdeel(GebiedenMixin, rest.HALSerializer):
    class Meta:
        model = models.Stadsdeel
        fiels = (
            '_links',
            'id',
            'code',
            'date_modified',

            'naam',
            'gemeente',
        )


class Buurt(GebiedenMixin, rest.HALSerializer):
    class Meta:
        model = models.Buurt
        fields = (
            '_links',
            'code',

            'naam',
            'stadsdeel',
        )


class Bouwblok(GebiedenMixin, rest.HALSerializer):
    class Meta:
        model = models.Bouwblok
        fields = (
            '_links',
            'code',
            'buurt',
        )
