from rest_framework import serializers

from atlas import models


class Autocomplete(serializers.Serializer):

    query = serializers.CharField()
    items = serializers.ListField(child=serializers.CharField())

    def update(self, instance, validated_data):
        raise ValueError("readonly")

    def create(self, validated_data):
        raise ValueError("readonly")



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


class Gemeente(serializers.ModelSerializer):
    class Meta:
        model = models.Gemeente
        fields = (
            'id',
            'code',
            'date_created',
            'date_modified',
            'vervallen',

            'naam',
            'verzorgingsgebied',
        )


class Stadsdeel(serializers.ModelSerializer):
    gemeente = Gemeente()

    class Meta:
        model = models.Stadsdeel
        fiels = (
            'id',
            'code',
            'date_created',
            'date_modified',
            'vervallen',

            'naam',
            'gemeente',
        )


class Buurt(serializers.ModelSerializer):
    stadsdeel = Stadsdeel()

    class Meta:
        model = models.Buurt
        fields = (
            'id',
            'code',
            'vervallen',

            'naam',
            'stadsdeel',
        )


class Woonplaats(serializers.ModelSerializer):
    gemeente = Gemeente()

    class Meta:
        model = models.Woonplaats
        fields = (
            'id',
            'code',
            'date_created',
            'date_modified',
            'document_mutatie',
            'document_nummer',
            'vervallen',

            'naam',
            'naam_ptt',
            'gemeente',
        )


class OpenbareRuimte(serializers.ModelSerializer):
    status = Status()
    type = serializers.CharField(source='get_type_display')
    woonplaats = Woonplaats()

    class Meta:
        model = models.OpenbareRuimte
        fields = (
            'id',
            'code',
            'date_created',
            'date_modified',
            'document_mutatie',
            'document_nummer',
            'status',
            'bron',
            'vervallen',

            'type',
            'naam',
            'naam_ptt',
            'naam_nen',
            'straat_nummer',
            'woonplaats',
        )


class Nummeraanduiding(serializers.HyperlinkedModelSerializer):
    status = Status()
    openbare_ruimte = OpenbareRuimte()
    type = serializers.CharField(source='get_type_display')

    class Meta:
        model = models.Nummeraanduiding
        fields = (
            'id',
            'code',
            'url',
            'date_created',
            'date_modified',
            'document_mutatie',
            'document_nummer',
            'status',
            'bron',
            'vervallen',
            'adres',

            'postcode',
            'huisnummer',
            'huisletter',
            'huisnummer_toevoeging',
            'type',
            'adres_nummer',
            'openbare_ruimte',
            'ligplaatsen',
            'standplaatsen',
            'verblijfsobjecten',
        )

class Ligplaats(serializers.HyperlinkedModelSerializer):
    status = Status()
    buurt = Buurt()

    class Meta:
        model = models.Ligplaats
        fields = (
            'id',
            'identificatie',
            'url',
            'date_created',
            'date_modified',
            'document_mutatie',
            'document_nummer',
            'status',
            'bron',
            'vervallen',

            'hoofdadres',
            'buurt',
        )


class Standplaats(serializers.HyperlinkedModelSerializer):
    status = Status()
    buurt = Buurt()

    class Meta:
        model = models.Standplaats
        fields = (
            'id',
            'identificatie',
            'url',
            'date_created',
            'date_modified',
            'document_mutatie',
            'document_nummer',
            'status',
            'bron',
            'vervallen',

            'hoofdadres',
            'buurt',
        )


class Verblijfsobject(serializers.HyperlinkedModelSerializer):
    status = Status()
    buurt = Buurt()
    eigendomsverhouding = Eigendomsverhouding()
    financieringswijze = Financieringswijze()
    gebruik = Gebruik()
    ligging = Ligging()
    locatie_ingang = LocatieIngang()
    toegang = Toegang()
    status_coordinaat = serializers.SerializerMethodField()
    type_woonobject = serializers.SerializerMethodField()
    gebruiksdoel = serializers.SerializerMethodField()

    class Meta:
        model = models.Verblijfsobject
        fields = (
            'id',
            'identificatie',
            'url',
            'date_created',
            'date_modified',
            'document_mutatie',
            'document_nummer',
            'status',
            'bron',
            'vervallen',

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
            'buurt',
            'panden',
        )

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

class Pand(serializers.HyperlinkedModelSerializer):

    status = Status()

    class Meta:
        model = models.Pand
        fields = (
            'id',
            'identificatie',
            'url',
            'date_created',
            'date_modified',
            'document_mutatie',
            'document_nummer',
            'status',
            'vervallen',

            'bouwjaar',
            'hoogste_bouwlaag',
            'laagste_bouwlaag',
            'pandnummer',

            'verblijfsobjecten',
        )