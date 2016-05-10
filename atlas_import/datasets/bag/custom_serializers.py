from rest_framework import serializers

from datasets.generic import rest
from datasets.bag import models
from datasets.bag import serializers as bag_serializers
from datasets.brk import custom_serializers as brk_serializers


class VerblijfsobjectNummeraanduiding(bag_serializers.VerblijfsobjectDetailMixin, bag_serializers.BagMixin,
                                      rest.HALSerializer):
    """
    Serializer used in custom nummeraanduiding endpoint
    """
    _display = rest.DisplayField()
    status = bag_serializers.Status()
    eigendomsverhouding = bag_serializers.Eigendomsverhouding()
    financieringswijze = bag_serializers.Financieringswijze()
    gebruik = bag_serializers.Gebruik()
    ligging = bag_serializers.Ligging()
    locatie_ingang = bag_serializers.LocatieIngang()
    toegang = bag_serializers.Toegang()
    status_coordinaat = serializers.SerializerMethodField()
    type_woonobject = serializers.SerializerMethodField()
    gebruiksdoel = serializers.SerializerMethodField()
    reden_afvoer = bag_serializers.RedenAfvoer()
    reden_opvoer = bag_serializers.RedenOpvoer()
    bouwblok = bag_serializers.Bouwblok()
    # panden = rest.RelatedSummaryField()
    # adressen = rest.RelatedSummaryField()
    kadastrale_objecten = brk_serializers.KadastraalObjectNummeraanduiding(many=True)

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
            'bouwblok',
            'hoofdadres',
            # 'adressen',
            # 'panden',
            'kadastrale_objecten',
        )


class NummeraanduidingExpanded(bag_serializers.BagMixin, rest.HALSerializer):
    """
    Serializer used in custom nummeraanduiding endpoint
    """
    _display = rest.DisplayField()
    status = bag_serializers.Status()
    type = serializers.CharField(source='get_type_display')
    bouwblok = bag_serializers.Bouwblok()

    buurt = bag_serializers.Buurt()
    buurtcombinatie = bag_serializers.Buurtcombinatie()
    stadsdeel = bag_serializers.Stadsdeel()
    openbare_ruimte = bag_serializers.OpenbareRuimte()
    woonplaats = bag_serializers.Woonplaats()
    gemeente = bag_serializers.Gemeente()

    ligplaats = bag_serializers.Ligplaats()
    standplaats = bag_serializers.Standplaats()
    verblijfsobject = VerblijfsobjectNummeraanduiding()

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
            'woonplaats',
            'gemeente',

            'ligplaats',
            'standplaats',
            'verblijfsobject',
        )
