from rest_framework import serializers
# from collections import OrderedDict

from rest_framework_gis.fields import GeometryField

from rest_framework.reverse import reverse

from datasets.brk import serializers as brk_serializers
from datasets.generic import rest

from . import models


class BagMixin(rest.DataSetSerializerMixin):
    dataset = 'bag'


class GebiedenMixin(rest.DataSetSerializerMixin):
    dataset = 'gebieden'

    def get_bbox(self, obj):
        if obj.geometrie:
            return obj.geometrie.extent


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


class BRKGemeenteLink(rest.LinksField):

    def get_url(self, obj, view_name, request, format):

        url_kwargs = {
            'pk': obj.naam
        }

        return reverse(
            view_name, kwargs=url_kwargs, request=request, format=format)


class Gemeente(BagMixin, serializers.HyperlinkedModelSerializer):

    url_field_name = '_links'
    serializer_url_field = BRKGemeenteLink

    _display = rest.DisplayField()

    class Meta:
        model = models.Gemeente
        fields = (
            '_display',
            '_links',
            'naam',
            'code',
        )


class GemeenteDetail(BagMixin, rest.HALSerializer):
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
    vbo_status = Status()

    class Meta:
        model = models.Nummeraanduiding
        fields = (
            '_links',
            '_display',
            'landelijk_id',
            'hoofdadres',
            'vbo_status',
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
    status = Status()
    hoofdadres = serializers.SerializerMethodField()

    class Meta:
        model = models.Verblijfsobject
        fields = (
            '_links',
            '_display',
            'landelijk_id',
            'id',
            'status',
            'hoofdadres',
        )
        lookup_field = 'landelijk_id'

    def get_hoofdadres(self, obj):
        return True if obj.hoofdadres else None


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


class StadsdeelDetail(GebiedenMixin, rest.HALSerializer):
    _display = rest.DisplayField()
    buurten = rest.RelatedSummaryField()
    gebiedsgerichtwerken = rest.RelatedSummaryField()
    buurtcombinaties = rest.RelatedSummaryField()
    gemeente = Gemeente()

    stadsdeelidentificatie = serializers.CharField(source='id')

    class Meta:
        model = models.Stadsdeel
        fields = (
            '_links',
            '_display',
            'stadsdeelidentificatie',
            'code',
            'date_modified',
            'begin_geldigheid',
            'einde_geldigheid',

            'naam',
            'gemeente',
            'brondocument_naam',
            'brondocument_datum',
            'geometrie',
            'buurten',
            'buurtcombinaties',
            'gebiedsgerichtwerken',
        )


class Buurtcombinatie(GebiedenMixin, rest.HALSerializer):
    _display = rest.DisplayField()

    class Meta:
        model = models.Buurtcombinatie
        fields = (
            '_links',
            '_display',
            'naam',
            'vollcode',
        )


class BuurtcombinatieDetail(GebiedenMixin, rest.HALSerializer):
    _display = rest.DisplayField()
    stadsdeel = Stadsdeel()
    buurten = rest.RelatedSummaryField()

    bbox = serializers.SerializerMethodField()

    _gemeente = Gemeente()

    buurtcombinatie_identificatie = serializers.CharField(source='id')
    volledige_code = serializers.CharField(source='vollcode')

    class Meta:
        model = models.Buurtcombinatie
        fields = (
            '_links',
            '_display',
            'buurtcombinatie_identificatie',
            'naam',
            'code',
            'volledige_code',
            'brondocument_naam',
            'brondocument_datum',
            'geometrie',
            'begin_geldigheid',
            'einde_geldigheid',
            'stadsdeel',
            'buurten',
            'bbox',
            '_gemeente',
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


class BuurtDetail(GebiedenMixin, rest.HALSerializer):
    _display = rest.DisplayField()
    bouwblokken = rest.RelatedSummaryField()
    ligplaatsen = rest.RelatedSummaryField()
    standplaatsen = rest.RelatedSummaryField()
    verblijfsobjecten = rest.RelatedSummaryField()
    buurtcombinatie = Buurtcombinatie()
    stadsdeel = Stadsdeel()

    _gemeente = Gemeente()

    bbox = serializers.SerializerMethodField()

    buurtidentificatie = serializers.CharField(source='id')
    volledige_code = serializers.CharField(source='vollcode')

    class Meta:
        model = models.Buurt
        fields = (
            '_links',
            '_display',
            'id',
            'buurtidentificatie',
            'code',
            'volledige_code',

            'naam',
            'stadsdeel',
            'brondocument_naam',
            'brondocument_datum',
            'begin_geldigheid',
            'einde_geldigheid',
            'bbox',
            'geometrie',
            'buurtcombinatie',
            'bouwblokken',
            'ligplaatsen',
            'standplaatsen',
            'verblijfsobjecten',

            '_gemeente',
        )


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
            'code',
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
    woonplaatsidentificatie = serializers.CharField(source='landelijk_id')
    sleutelverzendend = serializers.CharField(source='id')
    naam_17_posities = serializers.CharField(source='naam_ptt')

    class Meta:
        model = models.Woonplaats
        fields = (
            '_links',
            '_display',
            'sleutelverzendend',
            # 'id',
            'woonplaatsidentificatie',
            # 'landelijk_id',
            'date_modified',
            'document_mutatie',
            'document_nummer',
            'begin_geldigheid',
            'einde_geldigheid',
            'mutatie_gebruiker',

            'naam',
            # 'naam_ptt',
            'naam_17_posities',
            'gemeente',
            'openbare_ruimtes'
        )


class OpenbareRuimteDetail(BagMixin, rest.HALSerializer):
    _display = rest.DisplayField()
    status = Status()
    type = serializers.CharField(source='get_type_display')
    adressen = rest.RelatedSummaryField()
    woonplaats = Woonplaats()

    sleutelverzendend = serializers.CharField(source='id')
    openbare_ruimte_identificatie = serializers.CharField(
        source='landelijk_id')
    openbare_ruimte_code = serializers.CharField(source='code')
    naam_17_posities = serializers.CharField(source='naam_ptt')
    naam_24_posities = serializers.CharField(source='naam_nen')

    bbox = serializers.SerializerMethodField()

    class Meta:
        model = models.OpenbareRuimte
        fields = (
            '_links',
            '_display',
            'sleutelverzendend',
            'openbare_ruimte_identificatie',
            'openbare_ruimte_code',
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
            'naam_17_posities',
            'naam_24_posities',
            'straat_nummer',
            'woonplaats',
            'adressen',

            'bbox',
            'geometrie',
        )

    def get_bbox(self, obj):
        if obj.geometrie:
            return obj.geometrie.extent


class LigplaatsDetail(BagMixin, rest.HALSerializer):
    _display = rest.DisplayField()

    status = Status()
    hoofdadres = Nummeraanduiding()
    buurt = Buurt()
    adressen = rest.RelatedSummaryField()

    _buurtcombinatie = Buurtcombinatie()
    _stadsdeel = Stadsdeel()
    _gemeente = Gemeente()
    _woonplaats = Woonplaats()
    _gebiedsgerichtwerken = Gebiedsgerichtwerken()
    _grootstedelijkgebied = Grootstedelijkgebied()

    ligplaatsidentificatie = serializers.CharField(source='landelijk_id')
    sleutelverzendend = serializers.CharField(source='id')
    aanduiding_in_onderzoek = serializers.BooleanField(
        source='indicatie_in_onderzoek')

    class Meta:
        model = models.Ligplaats
        fields = (
            '_links',
            '_display',
            'sleutelverzendend',
            'ligplaatsidentificatie',
            'date_modified',
            'document_mutatie',
            'document_nummer',
            'begin_geldigheid',
            'einde_geldigheid',
            'mutatie_gebruiker',
            'status',
            'bron',

            'indicatie_geconstateerd',
            'aanduiding_in_onderzoek',

            'geometrie',
            'hoofdadres',
            'adressen',
            'buurt',
            '_buurtcombinatie',
            '_stadsdeel',
            '_gebiedsgerichtwerken',
            '_grootstedelijkgebied',
            '_gemeente',
            '_woonplaats',
        )


class NummeraanduidingDetail(BagMixin, rest.HALSerializer):
    _display = rest.DisplayField()
    status = Status()
    type = serializers.CharField(source='get_type_display')
    buurt = Buurt()
    buurtcombinatie = Buurtcombinatie()
    gebiedsgerichtwerken = Gebiedsgerichtwerken()
    grootstedelijkgebied = Grootstedelijkgebied()
    stadsdeel = Stadsdeel()
    openbare_ruimte = OpenbareRuimte()
    woonplaats = Woonplaats()
    bouwblok = Bouwblok()
    _geometrie = GeometryField()
    afstand = rest.DistanceGeometryField()

    nummeraanduidingidentificatie = serializers.CharField(
        source='landelijk_id')

    sleutelverzendend = serializers.CharField(source='id')

    def to_representation(self, instance):
        """
        Removes the afstand field if it is None
        """
        obj = super(NummeraanduidingDetail, self)
        representation = obj.to_representation(instance)
        if representation['afstand'] is None:
            try:
                representation.pop('afstand')
            except KeyError:
                # Ignore missing key -- a child serializer could
                # inherit a "to_representation" method
                # from its parent serializer that applies to a
                # field not present on
                # the child serializer.
                pass
        return representation

    class Meta:
        model = models.Nummeraanduiding
        fields = (
            '_links',
            '_display',
            'sleutelverzendend',
            'nummeraanduidingidentificatie',
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
            'gebiedsgerichtwerken',
            'grootstedelijkgebied',
            'stadsdeel',
            'woonplaats',
            'bouwblok',
            '_geometrie',
            'afstand',
        )


class StandplaatsDetail(BagMixin, rest.HALSerializer):
    _display = rest.DisplayField()
    status = Status()
    adressen = rest.RelatedSummaryField()
    hoofdadres = Nummeraanduiding()
    buurt = Buurt()

    _buurtcombinatie = Buurtcombinatie()
    _stadsdeel = Stadsdeel()
    _gemeente = Gemeente()
    _woonplaats = Woonplaats()
    _gebiedsgerichtwerken = Gebiedsgerichtwerken()
    _grootstedelijkgebied = Grootstedelijkgebied()

    standplaatsidentificatie = serializers.CharField(source='landelijk_id')
    sleutelverzendend = serializers.CharField(source='id')
    aanduiding_in_onderzoek = serializers.BooleanField(
        source='indicatie_in_onderzoek')

    class Meta:
        model = models.Standplaats
        fields = (
            '_links',
            '_display',

            'standplaatsidentificatie',
            'sleutelverzendend',

            'landelijk_id',
            'date_modified',
            'document_mutatie',
            'document_nummer',
            'begin_geldigheid',
            'einde_geldigheid',
            'mutatie_gebruiker',
            'status',
            'bron',

            'indicatie_geconstateerd',
            'aanduiding_in_onderzoek',

            'geometrie',
            'hoofdadres',
            'adressen',
            'buurt',

            '_buurtcombinatie',
            '_stadsdeel',
            '_gebiedsgerichtwerken',
            '_grootstedelijkgebied',
            '_gemeente',
            '_woonplaats',
        )


class KadastraalObjectField(serializers.HyperlinkedRelatedField):
    view_name = "kadastraalobject-detail"


class GebruiksdoelSerializer(serializers.ModelSerializer):
    verblijfsobject = serializers.ReadOnlyField(source='verblijfsobject_id')
    code = serializers.CharField()
    omschrijving = serializers.CharField()
    code_plus = serializers.CharField()
    omschrijving_plus = serializers.CharField()

    class Meta:
        model = models.Gebruiksdoel
        fields = (
            'verblijfsobject', 'code', 'omschrijving', 'code_plus',
            'omschrijving_plus')


class VerblijfsobjectDetailMixin(object):

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

    def get_gebruiksdoelen(self, obj):
        data = GebruiksdoelSerializer(
            instance=obj.gebruiksdoelen.all(), many=True).data
        for doel in data:  # we know verblijfsobject id (do not include again)
            doel.pop('verblijfsobject')
        return data


class VerblijfsobjectDetail(
        VerblijfsobjectDetailMixin, BagMixin, rest.HALSerializer):
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
    hoofdadres = Nummeraanduiding()
    buurt = Buurt()
    reden_afvoer = RedenAfvoer()
    reden_opvoer = RedenOpvoer()

    kadastrale_objecten = rest.RelatedSummaryField()

    panden = rest.RelatedSummaryField()
    adressen = rest.RelatedSummaryField()
    rechten = rest.RelatedSummaryField()
    beperkingen = rest.RelatedSummaryField()

    bouwblok = Bouwblok()

    _buurtcombinatie = Buurtcombinatie()
    _stadsdeel = Stadsdeel()
    _gebiedsgerichtwerken = Gebiedsgerichtwerken()
    _grootstedelijkgebied = Grootstedelijkgebied()
    _gemeente = Gemeente()
    _woonplaats = Woonplaats()

    verblijfsobjectidentificatie = serializers.CharField(
        source='landelijk_id')
    sleutelverzendend = serializers.CharField(source='id')
    aanduiding_in_onderzoek = serializers.BooleanField(
        source='indicatie_in_onderzoek')

    gebruiksdoelen = serializers.SerializerMethodField()

    class Meta:
        model = models.Verblijfsobject
        fields = (
            '_links',
            '_display',
            'sleutelverzendend',
            'verblijfsobjectidentificatie',
            'date_modified',
            'document_mutatie',
            'document_nummer',
            'begin_geldigheid',
            'einde_geldigheid',
            'mutatie_gebruiker',
            'status',
            'bron',

            'geometrie',
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
            'bouwblok',

            'indicatie_geconstateerd',
            'aanduiding_in_onderzoek',

            '_buurtcombinatie',
            '_stadsdeel',
            '_gebiedsgerichtwerken',
            '_grootstedelijkgebied',
            '_gemeente',
            '_woonplaats',

            'gebruiksdoelen',
        )


class PandDetail(BagMixin, rest.HALSerializer):
    _display = rest.DisplayField()
    status = Status()
    verblijfsobjecten = rest.RelatedSummaryField()
    bouwblok = Bouwblok()

    _adressen = rest.AdresFilterField()
    _monumenten = rest.ExternalRelationField('monumenten/monumenten/', 'betreft_pand')

    _buurt = Buurt()
    _buurtcombinatie = Buurtcombinatie()
    _stadsdeel = Stadsdeel()
    _gemeente = Gemeente()

    pandidentificatie = serializers.CharField(source='landelijk_id')
    sleutelverzendend = serializers.CharField(source='id')
    oorspronkelijk_bouwjaar = serializers.CharField(source='bouwjaar')

    class Meta:
        model = models.Pand
        fields = (
            '_links',
            '_display',
            'sleutelverzendend',
            'pandidentificatie',
            'date_modified',
            'document_mutatie',
            'document_nummer',
            'status',

            'geometrie',

            'oorspronkelijk_bouwjaar',

            'hoogste_bouwlaag',
            'laagste_bouwlaag',
            'pandnummer',
            'pandnaam',

            'verblijfsobjecten',

            '_adressen',
            '_monumenten',
            'bouwblok',

            'begin_geldigheid',
            'einde_geldigheid',
            'mutatie_gebruiker',

            '_buurt',
            '_buurtcombinatie',
            '_stadsdeel',
            '_gemeente',

        )


class BouwblokDetail(GebiedenMixin, rest.HALSerializer):
    _display = rest.DisplayField()
    panden = rest.RelatedSummaryField()
    buurt = Buurt()
    meetbouten = serializers.SerializerMethodField()

    _buurtcombinatie = Buurtcombinatie()
    _stadsdeel = Stadsdeel()
    _gemeente = Gemeente()

    bouwblokidentificatie = serializers.CharField(source='id')

    class Meta:
        model = models.Bouwblok
        fields = (
            '_links',
            '_display',
            'bouwblokidentificatie',
            'code',
            'buurt',
            'begin_geldigheid',
            'einde_geldigheid',
            'geometrie',
            'panden',
            'meetbouten',

            '_buurtcombinatie',
            '_stadsdeel',
            '_gemeente',
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

    buurten = rest.RelatedSummaryField()

    class Meta:
        model = models.Gebiedsgerichtwerken
        fields = (
            '_links',
            '_display',
            'naam',
            'code',
            'stadsdeel',
            'buurten',
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


class VerblijfsobjectNummeraanduiding(
        VerblijfsobjectDetailMixin, BagMixin, rest.HALSerializer):
    """
    Serializer used in custom nummeraanduiding endpoint
    """
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
    reden_afvoer = RedenAfvoer()
    reden_opvoer = RedenOpvoer()
    panden = rest.RelatedSummaryField()
    adressen = rest.RelatedSummaryField()

    kadastrale_objecten = \
        brk_serializers.KadastraalObjectNummeraanduiding(many=True)

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
            'panden',
            'adressen',
            'kadastrale_objecten',
        )


class VerblijfsobjectNummeraanduidingExp(VerblijfsobjectNummeraanduiding):

    kadastrale_objecten = \
        brk_serializers.KadastraalObjectNummeraanduidingExp(many=True)


class NummeraanduidingExpanded(BagMixin, rest.HALSerializer):
    """
    Serializer used in custom nummeraanduiding endpoint
    """
    _display = rest.DisplayField()
    status = Status()
    type = serializers.CharField(source='get_type_display')
    bouwblok = Bouwblok()

    buurt = Buurt()
    buurtcombinatie = Buurtcombinatie()
    stadsdeel = Stadsdeel()
    openbare_ruimte = OpenbareRuimte()
    gebiedsgerichtwerken = Gebiedsgerichtwerken()
    woonplaats = Woonplaats()
    gemeente = Gemeente()

    ligplaats = Ligplaats()
    standplaats = Standplaats()
    verblijfsobject = VerblijfsobjectNummeraanduidingExp()

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
            'bouwblok',

            'buurt',
            'buurtcombinatie',
            'stadsdeel',
            'gebiedsgerichtwerken',
            'woonplaats',
            'gemeente',

            'ligplaats',
            'standplaats',
            'verblijfsobject',
        )
