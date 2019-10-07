from rest_framework import serializers

from rest_framework_gis.fields import GeometryField

from rest_framework.reverse import reverse

from datasets.brk import serializers as brk_serializers
from datasets.generic import rest

from . import models


class BboxMixin:
    def get_bbox(self, obj):
        if obj.geometrie:
            return obj.geometrie.extent


class BagMixin(rest.DataSetSerializerMixin):
    dataset = 'bag'


class GebiedenMixin(rest.DataSetSerializerMixin):
    dataset = 'gebieden'


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

    class Meta:
        model = models.Nummeraanduiding
        fields = (
            '_links',
            '_display',
            'landelijk_id',
            'type_adres',
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


class StadsdeelDetail(GebiedenMixin, BboxMixin, rest.HALSerializer):
    _display = rest.DisplayField()
    buurten = rest.RelatedSummaryField()
    gebiedsgerichtwerken = rest.RelatedSummaryField()
    buurtcombinaties = rest.RelatedSummaryField()
    gemeente = Gemeente()

    bbox = serializers.SerializerMethodField()

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
            'bbox',
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


class BuurtcombinatieDetail(GebiedenMixin, BboxMixin, rest.HALSerializer):
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


class BuurtDetail(GebiedenMixin, BboxMixin, rest.HALSerializer):
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


class BouwblokDetail(GebiedenMixin, BboxMixin, rest.HALSerializer):
    _display = rest.DisplayField()
    panden = rest.RelatedSummaryField()
    buurt = Buurt()
    meetbouten = serializers.SerializerMethodField()

    _buurtcombinatie = Buurtcombinatie()
    _stadsdeel = Stadsdeel()
    _gemeente = Gemeente()

    bouwblokidentificatie = serializers.CharField(source='id')

    bbox = serializers.SerializerMethodField()

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
            'bbox',
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


class GebiedsgerichtwerkenPraktijkgebieden(GebiedenMixin, rest.HALSerializer):
    _display = rest.DisplayField()

    class Meta:
        model = models.GebiedsgerichtwerkenPraktijkgebieden

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
            'gsg_type',
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

    class Meta:
        model = models.Woonplaats
        fields = (
            '_links',
            '_display',
            'woonplaatsidentificatie',
            'date_modified',
            'document_mutatie',
            'document_nummer',
            'begin_geldigheid',
            'einde_geldigheid',

            'naam',
            'gemeente',
            'openbare_ruimtes'
        )


class OpenbareRuimteDetail(BagMixin, BboxMixin, rest.HALSerializer):
    _display = rest.DisplayField()
    type = serializers.CharField(source='get_type_display')
    adressen = rest.RelatedSummaryField()
    woonplaats = Woonplaats()

    openbare_ruimte_identificatie = serializers.CharField(
        source='landelijk_id')
    naam_24_posities = serializers.CharField(source='naam_nen')

    bbox = serializers.SerializerMethodField()

    class Meta:
        model = models.OpenbareRuimte
        fields = (
            '_links',
            '_display',
            'openbare_ruimte_identificatie',
            'date_modified',
            'document_mutatie',
            'document_nummer',
            'begin_geldigheid',
            'einde_geldigheid',
            'status',
            'bron',
            'geometrie',

            'type',
            'naam',
            'omschrijving',
            'naam_24_posities',
            'woonplaats',
            'adressen',

            'bbox',
            'geometrie',
        )


class LigplaatsDetail(BagMixin, BboxMixin, rest.HALSerializer):
    _display = rest.DisplayField()
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
    aanduiding_in_onderzoek = serializers.BooleanField(
        source='indicatie_in_onderzoek')

    bbox = serializers.SerializerMethodField()

    class Meta:
        model = models.Ligplaats
        fields = (
            '_links',
            '_display',
            'ligplaatsidentificatie',
            'date_modified',
            'document_mutatie',
            'document_nummer',
            'begin_geldigheid',
            'einde_geldigheid',
            'status',
            'bron',

            'indicatie_geconstateerd',
            'aanduiding_in_onderzoek',

            'bbox',
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
    type = serializers.CharField(source='get_type_display')
    buurt = Buurt()
    buurtcombinatie = Buurtcombinatie()
    gebiedsgerichtwerken = Gebiedsgerichtwerken()
    grootstedelijkgebied = Grootstedelijkgebied()
    stadsdeel = Stadsdeel()
    openbare_ruimte = OpenbareRuimte()
    verblijfsobject = serializers.HyperlinkedRelatedField(allow_null=True,
                                                          queryset=models.Verblijfsobject.objects.all(), required=False,
                                                          view_name='verblijfsobject-detail',
                                                          lookup_field='landelijk_id', lookup_url_kwarg='pk')
    ligplaats = serializers.HyperlinkedRelatedField(allow_null=True,
                                                    queryset=models.Ligplaats.objects.all(), required=False,
                                                    view_name='ligplaats-detail',
                                                    lookup_field='landelijk_id', lookup_url_kwarg='pk')
    standplaats = serializers.HyperlinkedRelatedField(allow_null=True,
                                                      queryset=models.Standplaats.objects.all(), required=False,
                                                      view_name='standplaats-detail',
                                                      lookup_field='landelijk_id', lookup_url_kwarg='pk')

    woonplaats = Woonplaats()
    bouwblok = Bouwblok()
    _geometrie = GeometryField()
    afstand = rest.DistanceGeometryField()

    nummeraanduidingidentificatie = serializers.CharField(
        source='landelijk_id')

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
            'nummeraanduidingidentificatie',
            'date_modified',
            'document_mutatie',
            'document_nummer',
            'begin_geldigheid',
            'einde_geldigheid',
            'status',
            'bron',
            'adres',

            'postcode',
            'huisnummer',
            'huisletter',
            'huisnummer_toevoeging',
            'type',
            'openbare_ruimte',
            'type_adres',
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


class StandplaatsDetail(BagMixin, BboxMixin, rest.HALSerializer):
    _display = rest.DisplayField()
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
    aanduiding_in_onderzoek = serializers.BooleanField(
        source='indicatie_in_onderzoek')

    bbox = serializers.SerializerMethodField()

    class Meta:
        model = models.Standplaats
        fields = (
            '_links',
            '_display',

            'standplaatsidentificatie',

            'landelijk_id',
            'date_modified',
            'document_mutatie',
            'document_nummer',
            'begin_geldigheid',
            'einde_geldigheid',
            'status',
            'bron',

            'indicatie_geconstateerd',
            'aanduiding_in_onderzoek',

            'bbox',
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

    class Meta:
        model = models.Gebruiksdoel
        fields = (
            'verblijfsobject', 'code', 'omschrijving',)


class VerblijfsobjectDetailMixin(object):

    def get_gebruiksdoelen(self, obj):
        data = GebruiksdoelSerializer(
            instance=obj.gebruiksdoelen.all(), many=True).data
        for doel in data:  # we know verblijfsobject id (do not include again)
            doel.pop('verblijfsobject')
        return data


class VerblijfsobjectDetail(
        VerblijfsobjectDetailMixin, BagMixin,
        BboxMixin, rest.HALSerializer):
    _display = rest.DisplayField()
    eigendomsverhouding = Eigendomsverhouding()
    gebruik = Gebruik()
    toegang = Toegang()
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
    aanduiding_in_onderzoek = serializers.BooleanField(
        source='indicatie_in_onderzoek')

    gebruiksdoelen = serializers.SerializerMethodField()

    bbox = serializers.SerializerMethodField()

    class Meta:
        model = models.Verblijfsobject
        fields = (
            '_links',
            '_display',
            'verblijfsobjectidentificatie',
            'date_modified',
            'document_mutatie',
            'document_nummer',
            'begin_geldigheid',
            'einde_geldigheid',
            'status',
            'bron',

            'bbox',
            'geometrie',
            'oppervlakte',
            'verdieping_toegang',
            'verhuurbare_eenheden',
            'bouwlagen',
            'hoogste_bouwlaag',
            'laagste_bouwlaag',
            'aantal_kamers',
            'reden_afvoer',
            'reden_opvoer',
            'eigendomsverhouding',
            'gebruik',
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
            'gebruiksdoel_woonfunctie',
            'gebruiksdoel_gezondheidszorgfunctie',

            '_buurtcombinatie',
            '_stadsdeel',
            '_gebiedsgerichtwerken',
            '_grootstedelijkgebied',
            '_gemeente',
            '_woonplaats',

            'gebruiksdoelen',
        )


class PandDetail(BagMixin, BboxMixin, rest.HALSerializer):
    _display = rest.DisplayField()
    verblijfsobjecten = rest.RelatedSummaryField()
    bouwblok = Bouwblok()

    _adressen = rest.AdresFilterField()
    _monumenten = rest.ExternalRelationField('monumenten/monumenten/', 'betreft_pand')

    _buurt = Buurt()
    _buurtcombinatie = Buurtcombinatie()
    _stadsdeel = Stadsdeel()
    _gemeente = Gemeente()

    pandidentificatie = serializers.CharField(source='landelijk_id')
    oorspronkelijk_bouwjaar = serializers.CharField(source='bouwjaar')

    bbox = serializers.SerializerMethodField()

    class Meta:
        model = models.Pand
        fields = (
            '_links',
            '_display',
            'pandidentificatie',
            'date_modified',
            'document_mutatie',
            'document_nummer',
            'status',

            'bbox',
            'geometrie',

            'oorspronkelijk_bouwjaar',

            'bouwlagen',
            'hoogste_bouwlaag',
            'laagste_bouwlaag',
            'pandnaam',
            'ligging',
            'type_woonobject',

            'verblijfsobjecten',

            '_adressen',
            '_monumenten',
            'bouwblok',

            'begin_geldigheid',
            'einde_geldigheid',

            '_buurt',
            '_buurtcombinatie',
            '_stadsdeel',
            '_gemeente',

        )


class GebiedsgerichtwerkenDetail(GebiedenMixin, BboxMixin, rest.HALSerializer):
    _display = rest.DisplayField()

    stadsdeel = Stadsdeel()

    buurten = rest.RelatedSummaryField()

    bbox = serializers.SerializerMethodField()

    class Meta:
        model = models.Gebiedsgerichtwerken
        fields = (
            '_links',
            '_display',
            'naam',
            'code',
            'stadsdeel',
            'buurten',
            'bbox',
            'geometrie',
        )


class GebiedsgerichtwerkenPraktijkgebiedenDetail(GebiedenMixin, BboxMixin, rest.HALSerializer):
    _display = rest.DisplayField()

    bbox = serializers.SerializerMethodField()

    class Meta:
        model = models.GebiedsgerichtwerkenPraktijkgebieden
        fields = (
            '_links',
            '_display',
            'naam',
            'bbox',
            'geometrie',
        )


class GrootstedelijkgebiedDetail(GebiedenMixin, BboxMixin, rest.HALSerializer):
    _display = rest.DisplayField()

    bbox = serializers.SerializerMethodField()

    class Meta:
        model = models.Grootstedelijkgebied
        fields = (
            '_links',
            '_display',
            'naam',
            'gsg_type',
            'bbox',
            'geometrie',
        )


class UnescoDetail(GebiedenMixin, BboxMixin, rest.HALSerializer):
    _display = rest.DisplayField()

    bbox = serializers.SerializerMethodField()

    class Meta:
        model = models.Unesco
        fields = (
            '_links',
            '_display',
            'naam',
            'bbox',
            'geometrie',
        )


class VerblijfsobjectNummeraanduiding(
        VerblijfsobjectDetailMixin, BagMixin, rest.HALSerializer):
    """
    Serializer used in custom nummeraanduiding endpoint
    """
    _display = rest.DisplayField()
    eigendomsverhouding = Eigendomsverhouding()
    gebruik = Gebruik()
    toegang = Toegang()
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
            'status',
            'bron',

            'geometrie',
            'oppervlakte',
            'verdieping_toegang',
            'verhuurbare_eenheden',
            'bouwlagen',
            'aantal_kamers',
            'reden_afvoer',
            'reden_opvoer',
            'eigendomsverhouding',
            'gebruik',
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
            'status',
            'bron',
            'adres',
            'postcode',
            'huisnummer',
            'huisletter',
            'huisnummer_toevoeging',
            'type',
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
