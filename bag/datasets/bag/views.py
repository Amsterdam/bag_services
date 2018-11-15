import logging

from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.geos import Point
from django.contrib.gis.measure import D
from django.db.models import Prefetch
from django.shortcuts import get_object_or_404
from django.views.generic import RedirectView
from django_filters.rest_framework import FilterSet
from django_filters.rest_framework import filters
from rest_framework.reverse import reverse
from rest_framework.metadata import SimpleMetadata
from rest_framework import serializers as validation

from datasets.generic import rest
from . import serializers, models


LOG = logging.getLogger(__name__)


def parse_xyr(value: str) -> (Point, int):
    """
    Parse x, y, radius input.
    """
    try:
        x, y, radius = value.split(',')
    except ValueError:
        raise validation.ValidationError(
            "Locatie must be rdx,rdy,radius or lat,long,radius"
        )

    try:
        # Converting , to . and then to float
        x = float(x)
        y = float(y)
        radius = int(radius)
    except ValueError:
        raise validation.ValidationError(
            "Locatie must be x: float, y: float, r: int"
        )

    # Checking if the given coords are in RD, otherwise converting
    if y > 10:
        point = Point(x, y, srid=28992)
    else:
        point = Point(y, x, srid=4326).transform(28992, clone=True)

    return point, radius


class ExpansionMetadata(SimpleMetadata):
    def determine_metadata(self, request, view):
        result = super().determine_metadata(request, view)
        result['parameters'] = dict(
            full=dict(
                type="string",
                description="If present, related entities are inlined",
                required=False
            )
        )
        return result


class LigplaatsViewSet(rest.DatapuntViewSet):
    """
    Ligplaats

    Een LIGPLAATS is een door het bevoegde gemeentelijke orgaan
    als zodanig aangewezen plaats in het water
    al dan niet aangevuld met een op de oever aanwezig
    terrein of een gedeelte daarvan,
    die bestemd is voor het permanent afmeren van een voor woon-,
    bedrijfsmatige of recreatieve doeleinden geschikt
    vaartuig.

    [Stelselpedia](http://www.amsterdam.nl/stelselpedia/bag-index/catalogus-bag/objectklasse-1/)
    """

    metadata_class = ExpansionMetadata
    queryset = models.Ligplaats.objects.all().order_by('id')
    queryset_detail = models.Ligplaats.objects.select_related(
        'buurt',
        'buurt__buurtcombinatie',
        'buurt__stadsdeel',
        'buurt__stadsdeel__gemeente',
        '_gebiedsgerichtwerken',

    )
    serializer_detail_class = serializers.LigplaatsDetail
    serializer_class = serializers.Ligplaats
    filter_fields = ('buurt', 'buurt__vollcode', 'landelijk_id')

    def get_object(self):
        pk = self.kwargs['pk']
        if pk and len(pk) == 16:
            obj = get_object_or_404(models.Ligplaats, landelijk_id=pk)
        else:
            obj = get_object_or_404(models.Ligplaats, pk=pk)

        return obj


class StandplaatsViewSet(rest.DatapuntViewSet):
    """
    Standplaats

    Een STANDPLAATS is een door het bevoegde gemeentelijke orgaan
    als zodanig aangewezen terrein of gedeelte daarvan
    dat bestemd is voor het permanent plaatsen van een
    niet direct en niet duurzaam met de aarde verbonden en voor
    woon -, bedrijfsmatige, of recreatieve doeleinden geschikte ruimte.

    [Stelselpedia](http://www.amsterdam.nl/stelselpedia/bag-index/catalogus-bag/objectklasse-4/)
    """

    metadata_class = ExpansionMetadata
    queryset = models.Standplaats.objects.all()
    queryset_detail = models.Standplaats.objects.select_related(
        'buurt',
        'buurt__buurtcombinatie',
        'buurt__stadsdeel',
        'buurt__stadsdeel__gemeente',
        '_gebiedsgerichtwerken',
    )
    serializer_detail_class = serializers.StandplaatsDetail
    serializer_class = serializers.Standplaats
    filter_fields = (
        'buurt',
        'buurt__vollcode',
        'landelijk_id'
    )

    def get_object(self):
        pk = self.kwargs['pk']
        if pk and len(pk) == 16:
            obj = get_object_or_404(models.Standplaats, landelijk_id=pk)
        else:
            obj = get_object_or_404(models.Standplaats, pk=pk)

        return obj


class VerblijfsobjectFilter(FilterSet):

    pand = filters.CharFilter(method="pand_filter", label="pand")
    panden__id = filters.CharFilter(method="pand_filter")
    panden__landelijk_id = filters.CharFilter(method="pand_filter")

    class Meta:
        model = models.Verblijfsobject

        fields = (
            'kadastrale_objecten__id',
            'pand',
            'landelijk_id',
            'panden__id',
            'panden__landelijk_id',
            'buurt',
            'buurt__vollcode',
            'oppervlakte',
            '_huisnummer',
            '_huisletter',
            '_huisnummer_toevoeging',
            '_openbare_ruimte_naam',
        )

    def pand_filter(self, queryset, filter_name, value):

        if len(value) == 16:
            return queryset.filter(panden__landelijk_id=value)
        else:
            return queryset.filter(panden__id=value)


class VerblijfsobjectViewSet(rest.DatapuntViewSet):
    """
    Verblijfsobject

    Een VERBLIJFSOBJECT is de kleinste binnen één of meer panden
    gelegen en voor woon -, bedrijfsmatige, of recreatieve
    doeleinden geschikte eenheid van gebruik die ontsloten wordt
    via een eigen afsluitbare toegang vanaf de openbare
    weg, een erf of een gedeelde verkeersruimte, onderwerp kan
    zijn van goederenrechtelijke rechtshandelingen en in
    functioneel opzicht zelfstandig is.

    [Stelselpedia](http://www.amsterdam.nl/stelselpedia/bag-index/catalogus-bag/objectklasse-0/)
    """

    metadata_class = ExpansionMetadata
    queryset = models.Verblijfsobject.objects
    queryset_detail = models.Verblijfsobject.objects.select_related(
        'buurt',
        'buurt__buurtcombinatie',
        'buurt__stadsdeel',
        'buurt__stadsdeel__gemeente',
        'status',
        'reden_afvoer',
        'eigendomsverhouding',
        'gebruik',
        'ligging',
        'toegang',
        'reden_opvoer',
        '_gebiedsgerichtwerken',
    ).prefetch_related(
        'gebruiksdoelen'
    )
    serializer_detail_class = serializers.VerblijfsobjectDetail
    serializer_class = serializers.Verblijfsobject

    filter_class = VerblijfsobjectFilter

    def get_object(self):
        pk = self.kwargs['pk']
        if pk and len(pk) == 16:
            obj = get_object_or_404(models.Verblijfsobject, landelijk_id=pk)
        else:
            obj = get_object_or_404(models.Verblijfsobject, pk=pk)

        return obj


class NummeraanduidingFilter(FilterSet):
    """
    Filter nummeraanduidingkjes
    """

    verblijfsobject = filters.CharFilter(method="vbo_filter", label='vbo')
    ligplaats = filters.CharFilter(method="ligplaats_filter")
    standplaats = filters.CharFilter(method="standplaats_filter")

    postcode = filters.CharFilter(method="postcode_filter")
    huisnummer = filters.NumberFilter()
    huisletter = filters.CharFilter()
    huisnummer_toevoeging = filters.CharFilter()
    openbare_ruimte = filters.CharFilter(method="openbare_ruimte_filter")
    locatie = filters.CharFilter(method="locatie_filter", label='x,y,r')

    pand = filters.CharFilter(method="pand_filter", label='pand')

    kadastraalobject = filters.CharFilter(method="kot_filter", label='kot')

    class Meta:
        model = models.Nummeraanduiding
        fields = [
            'verblijfsobject',
            'ligplaats',
            'standplaats',
            'landelijk_id',
            'openbare_ruimte',
            'postcode',
            'hoofdadres',
            'huisnummer',
            'huisletter',
            'huisnummer_toevoeging',
            'pand',
            'kadastraalobject',
            'locatie',
        ]

    def postcode_filter(self, queryset, _filter_name, value):
        """
        Support for incomplete postcode
        """
        if len(value) < 6:
            return queryset.filter(postcode__istartswith=value)
        return queryset.filter(postcode__iexact=value)

    def openbare_ruimte_filter(self, queryset, _filter_name, value):
        """
        Support for either openbareruimte id or name
        """
        if value.isdigit():
            if len(value) == 16:
                return queryset.filter(
                    openbare_ruimte__landelijk_id=value)
            return queryset.filter(openbare_ruimte_id=value)
        return queryset.filter(openbare_ruimte__naam__icontains=value)

    def locatie_filter(self, queryset, _filter_name, value):
        """
        Filter based on the geolocation. This filter actually
        expect 3 numerical values: x, y and radius
        The value given is broken up by ',' and converterd
        to the value tuple
        """
        point, radius = parse_xyr(value)

        # Creating one big queryset
        qs = queryset.filter(
            _geom__dwithin=(point, D(m=radius))
        ).annotate(afstand=Distance('_geom', point))

        return qs.order_by('afstand')

    def pand_filter(self, queryset, _filter_name, value):
        """
        Filter using a pand landelijk id
        """
        queryset = queryset.prefetch_related(None)
        queryset = queryset.select_related(None)
        # ligplaatsen en standplaatsen hebben we NIET nodig.
        queryset = queryset.select_related('verblijfsobject__status')
        m_po = models.Pand.objects
        pand = m_po.get(landelijk_id=value)   # noqa
        ids = pand.verblijfsobjecten.values_list(
            'adressen__landelijk_id', flat=True)
        return queryset.filter(landelijk_id__in=ids)

    def kot_filter(self, queryset, _filter_name, value):
        """Filter based on the kadastral object"""
        m_vbo = models.Verblijfsobject.objects
        vbos = m_vbo.select_related('adressen').filter(
            kadastrale_objecten__id=value)
        ids = vbos.values_list('adressen__landelijk_id', flat=True)
        return queryset.filter(landelijk_id__in=ids)

    def vbo_filter(self, queryset, _filter_name, value):
        """Filter based on verblijfsobject"""

        if len(value) == 16:
            return queryset.filter(verblijfsobject__landelijk_id=value)
        else:
            return queryset.filter(verblijfsobject__id=value)

    def ligplaats_filter(self, queryset, _filter_name, value):
        """Filter based on ligplaats"""

        if len(value) == 16:
            return queryset.filter(ligplaats__landelijk_id=value)
        else:
            return queryset.filter(ligplaats__id=value)

    def standplaats_filter(self, queryset, _filter_name, value):
        """Filter based on standplaats"""

        if len(value) == 16:
            return queryset.filter(standplaats__landelijk_id=value)
        else:
            return queryset.filter(standplaats__id=value)


class NummeraanduidingViewSet(rest.DatapuntViewSet):
    """
    Nummeraanduiding

    Een nummeraanduiding, in de volksmond ook wel adres genoemd,
    is een door het bevoegde gemeentelijke orgaan als
    zodanig toegekende aanduiding van een verblijfsobject,
    standplaats of ligplaats.

    [Stelselpedia]
    (http://www.amsterdam.nl/stelselpedia/bag-index/catalogus-bag/objectklasse-2/)

    bag/nummeraanduiding/?pand=0363100012171966

    TIP! detailed=1 if you want all fields in the list view!

    """

    metadata_class = ExpansionMetadata
    queryset = (
        models.Nummeraanduiding.objects.all().order_by('id')
        .select_related(
            'verblijfsobject',
            'standplaats',
            'ligplaats',
            'verblijfsobject__status',
            'standplaats__status',
            'ligplaats__status',
        )
    )
    queryset_detail = models.Nummeraanduiding.objects.prefetch_related(
        Prefetch('verblijfsobject__panden',
                 queryset=models.Pand.objects.select_related('bouwblok'))
    ).select_related(
        'status',
        'openbare_ruimte',
        'openbare_ruimte__woonplaats',
        'verblijfsobject',
        'verblijfsobject__buurt',
        'verblijfsobject__buurt__buurtcombinatie',
        'verblijfsobject__buurt__stadsdeel',
    )
    serializer_detail_class = serializers.NummeraanduidingDetail
    serializer_class = serializers.Nummeraanduiding
    filter_class = NummeraanduidingFilter
    detailed_keyword = 'detailed'

    def list(self, request, *args, **kwargs):
        # Checking if a detailed response is required
        if request.GET.get(self.detailed_keyword, False):
            self.serializer_class = self.serializer_detail_class
        return super().list(request, *args, **kwargs)

    def get_object(self):
        pk = self.kwargs['pk']
        if pk and len(pk) == 16:
            obj = get_object_or_404(models.Nummeraanduiding, landelijk_id=pk)
        else:
            obj = get_object_or_404(models.Nummeraanduiding, pk=pk)

        return obj


class PandenFilter(FilterSet):
    """
    Filter panden met landelijke ids
    """

    verblijfsobject = filters.CharFilter(method="vbo_filter", label="verblijfsobject")
    verblijfsobjecten__id = filters.CharFilter(method="vbo_filter", label="vbo_id")

    locatie = filters.CharFilter(method="locatie_filter", label='locatie')

    class Meta:
        model = models.Pand

        fields = (
            'verblijfsobject',
            'verblijfsobjecten__id',
            'verblijfsobjecten__landelijk_id',
            'landelijk_id',
            'bouwblok',
            'bouwblok__buurt',
            'bouwblok__buurt__stadsdeel',
            'locatie',
        )

    def vbo_filter(self, queryset, _filter_name, value):
        """Filter based on verblijfsobject"""

        if len(value) == 16:
            return queryset.filter(verblijfsobjecten__landelijk_id=value)

        return queryset.filter(verblijfsobjecten__id=value)

    def locatie_filter(self, queryset, _filter_name, value):
        """
        Filter based on the geolocation. This filter actually
        expect 3 numerical values: x, y and radius
        The value given is broken up by ',' and converterd
        to the value tuple
        """
        point, radius = parse_xyr(value)

        opr = queryset.filter(
            geometrie__dwithin=(point, D(m=radius))
        ).annotate(afstand=Distance('geometrie', point))

        return opr.order_by('afstand')


class PandViewSet(rest.DatapuntViewSet):
    """
    Pand

    Een PAND is de kleinste bij de totstandkoming functioneel en
    bouwkundig-constructief zelfstandige eenheid die
    direct en duurzaam met de aarde is verbonden en
    betreedbaar en afsluitbaar is.

    [Stelselpedia]
    (http://www.amsterdam.nl/stelselpedia/bag-index/catalogus-bag/objectklasse-pand/)

    TIP! detailed=1 if you want all fields in the list view!
    """

    metadata_class = ExpansionMetadata
    queryset = models.Pand.objects.all().order_by('id').select_related(
        'status',
        'bouwblok',
        'bouwblok__buurt',
        'bouwblok__buurt__stadsdeel',
        'bouwblok__buurt__buurtcombinatie',
        'bouwblok__buurt__stadsdeel__gemeente',
    ).prefetch_related(
        'verblijfsobjecten'
    )

    queryset_detail = queryset

    serializer_detail_class = serializers.PandDetail
    serializer_class = serializers.Pand

    filter_class = PandenFilter

    detailed_keyword = 'detailed'

    def get_object(self):
        pk = self.kwargs['pk']
        if pk and len(pk) == 16:
            obj = get_object_or_404(models.Pand, landelijk_id=pk)
        else:
            obj = get_object_or_404(models.Pand, pk=pk)

        return obj

    def list(self, request, *args, **kwargs):
        # Checking if a detailed response is required
        if request.GET.get(self.detailed_keyword, False):
            self.serializer_class = self.serializer_detail_class
        return super().list(request, *args, **kwargs)


class OpenbareRuimteFilter(FilterSet):
    """
    Filter openbare ruimte
    """

    locatie = filters.CharFilter(method="locatie_filter", label='locatie')

    class Meta:
        model = models.OpenbareRuimte

        fields = (
            'landelijk_id',
            'naam',
            'code',
            'type',
            'locatie',
            'adressen__postcode',
            'adressen__huisnummer',
            'adressen__huisletter',
            'adressen__huisnummer_toevoeging',
        )

    def locatie_filter(self, queryset, _filter_name, value):
        """
        Filter based on the geolocation. This filter actually
        expect 3 numerical values: x, y and radius
        The value given is broken up by ',' and converterd
        to the value tuple
        """
        point, radius = parse_xyr(value)

        opr = queryset.filter(
            geometrie__dwithin=(point, D(m=radius))
        ).annotate(afstand=Distance('geometrie', point))

        return opr.order_by('afstand')


class OpenbareRuimteViewSet(rest.DatapuntViewSet):
    """
    OpenbareRuimte

    Een OPENBARE RUIMTE is een door het [bevoegde gemeentelijke orgaan
    als zodanig aangewezen en van een naam
    voorziene
    [buitenruimte]
    (http://www.amsterdam.nl/stelselpedia/bag-index/handboek-inwinnen/openbare-ruimte/)
    die binnen één woonplaats is gelegen.

    Als openbare ruimte worden onder meer aangemerkt weg, water,
    terrein, spoorbaan en landschappelijk gebied.

    Bron: [Catalogus BAG (ministerie van VROM, 2009)](
    http://www.kadaster.nl/web/artikel/download/BAG-grondslagen-catalogus.htm).

    [Stelselpedia]
    (http://www.amsterdam.nl/stelselpedia/bag-index/catalogus-bag/objectklasse-3/)
    """  # noqa

    metadata_class = ExpansionMetadata
    queryset = models.OpenbareRuimte.objects.distinct()
    serializer_detail_class = serializers.OpenbareRuimteDetail
    serializer_class = serializers.OpenbareRuimte

    filter_class = OpenbareRuimteFilter

    def get_object(self):
        pk = self.kwargs['pk']
        if pk and len(pk) == 16:
            obj = get_object_or_404(models.OpenbareRuimte, landelijk_id=pk)
        else:
            obj = get_object_or_404(models.OpenbareRuimte, pk=pk)

        return obj


class WoonplaatsViewSet(rest.DatapuntViewSet):
    """
    Woonplaats

    Een WOONPLAATS is een door het bevoegde gemeentelijke orgaan
    als zodanig aangewezen en van een naam voorzien gedeelte
    van het grondgebied van de gemeente. Vanaf 10 januari 2014
    bestaat alleen nog de woonplaats Amsterdam met
    Woonplaatsidentificatie 3594.

    [Stelselpedia](https://www.amsterdam.nl/stelselpedia/bag-index/catalogus-bag/objectklasse/)   # noqa
    """  # noqa

    metadata_class = ExpansionMetadata
    queryset = models.Woonplaats.objects.all().order_by('id')
    serializer_detail_class = serializers.WoonplaatsDetail
    serializer_class = serializers.Woonplaats

    filter_fields = (
        'naam',
        'landelijk_id',
    )

    def get_object(self):
        pk = self.kwargs['pk']
        if pk and len(pk) <= 4:
            obj = get_object_or_404(models.Woonplaats, landelijk_id=pk)
        else:
            obj = get_object_or_404(models.Woonplaats, pk=pk)

        return obj


class StadsdeelViewSet(rest.DatapuntViewSet):
    """
    Stadsdeel

    Door de Amsterdamse gemeenteraad vastgestelde begrenzing van
    een stadsdeel, ressorterend onder een stadsdeelbestuur.

    [Stelselpedia]
    (https://www.amsterdam.nl/stelselpedia/gebieden-index/catalogus/stadsdeel/)
    """

    metadata_class = ExpansionMetadata
    queryset = models.Stadsdeel.objects.all().order_by('id')
    queryset_detail = models.Stadsdeel.objects.select_related(
        'gemeente',
    )
    serializer_detail_class = serializers.StadsdeelDetail
    serializer_class = serializers.Stadsdeel

    filter_fields = ('code',)

    def get_object(self):
        pk = self.kwargs['pk']
        if pk and len(pk) == 1:
            obj = get_object_or_404(models.Stadsdeel, code=pk)
        else:
            obj = get_object_or_404(models.Stadsdeel, pk=pk)

        return obj


class BuurtViewSet(rest.DatapuntViewSet):
    """
    Buurt

    Een aaneengesloten gedeelte van een buurt, waarvan de grenzen
    zo veel mogelijk gebaseerd zijn op topografische
    elementen.

    [Stelselpedia]
    (https://www.amsterdam.nl/stelselpedia/gebieden-index/catalogus/buurt/)
    """

    metadata_class = ExpansionMetadata
    queryset = models.Buurt.objects.all().order_by('naam')
    queryset_detail = models.Buurt.objects.select_related(
        'stadsdeel',
        'stadsdeel__gemeente',
        'buurtcombinatie',
    )
    serializer_detail_class = serializers.BuurtDetail
    serializer_class = serializers.Buurt
    filter_fields = (
        'stadsdeel', 'buurtcombinatie', 'gebiedsgerichtwerken',
        'code', 'vollcode')


class BouwblokViewSet(rest.DatapuntViewSet):
    """
    Bouwblok

    Een bouwblok is het kleinst mogelijk afgrensbare gebied,
    in zijn geheel tot een buurt behorend, dat geheel of
    grotendeels door bestaande of aan te leggen wegen
    en/of waterlopen is of zal zijn ingesloten en waarop tenminste
    één gebouw staat.

    [Stelselpedia]
    (https://www.amsterdam.nl/stelselpedia/gebieden-index/catalogus/bouwblok/)
    """

    metadata_class = ExpansionMetadata
    queryset = models.Bouwblok.objects.all()
    queryset_detail = models.Bouwblok.objects.select_related(
        'buurt',
        'buurt__stadsdeel',
        'buurt__stadsdeel__gemeente',
    )
    serializer_detail_class = serializers.BouwblokDetail
    serializer_class = serializers.Bouwblok
    filter_fields = ('buurt', 'code')

    def get_object(self):
        pk = self.kwargs['pk']
        if pk and len(pk) == 4:
            obj = get_object_or_404(models.Bouwblok, code=pk)
        else:
            obj = get_object_or_404(models.Bouwblok, pk=pk)

        return obj


class BuurtcombinatieViewSet(rest.DatapuntViewSet):
    """
    Buurtcombinatie

    Een aaneengesloten gedeelte van het grondgebied van een
    gemeente, waarvan de grenzen zo veel mogelijk zijn
    gebaseerd op sociaal-geografische kenmerken.

    [Stelselpedia]
    (https://www.amsterdam.nl/stelselpedia/gebieden-index/catalogus/buurtcombinatie/)
    """
    metadata_class = ExpansionMetadata
    queryset = models.Buurtcombinatie.objects.all()
    queryset_detail = models.Buurtcombinatie.objects.select_related(
        'stadsdeel',
        'stadsdeel__gemeente',
    )
    serializer_detail_class = serializers.BuurtcombinatieDetail
    serializer_class = serializers.Buurtcombinatie
    filter_fields = (
        'stadsdeel', 'vollcode', 'code', 'naam', 'stadsdeel',
        'buurten')


class GebiedsgerichtwerkenViewSet(rest.DatapuntViewSet):
    """
    Gebiedsgerichtwerken

    Gebiedsgericht werken is een manier van werken om samenwerken in
    de stad te verbeteren. De samenwerking betreft
    gemeente, bewoners, ondernemers, (lokale) partners
    en maatschappelijke organisaties.

    [Stelselpedia]
    (https://www.amsterdam.nl/stelselpedia/gebieden-index/catalogus/gebiedsgericht/)
    """

    metadata_class = ExpansionMetadata
    queryset = models.Gebiedsgerichtwerken.objects.all().order_by('naam')
    serializer_detail_class = serializers.GebiedsgerichtwerkenDetail
    serializer_class = serializers.Gebiedsgerichtwerken

    filter_fields = ('stadsdeel__id', 'stadsdeel')


class GrootstedelijkgebiedViewSet(rest.DatapuntViewSet):
    """
    Grootstedelijkgebied

    Grootstedelijke gebieden zijn gebieden binnen de gemeente
    Amsterdam, waar de gemeenteraad, het college van
    burgemeester en wethouders of de burgemeester bevoegd is.

    [Stelselpedia]
    (https://www.amsterdam.nl/stelselpedia/gebieden-index/catalogus/grootstedelijk/)
    """
    metadata_class = ExpansionMetadata
    queryset = models.Grootstedelijkgebied.objects.all().order_by('naam')
    serializer_detail_class = serializers.GrootstedelijkgebiedDetail
    serializer_class = serializers.Grootstedelijkgebied


class UnescoViewSet(rest.DatapuntViewSet):
    """
    Unseco

    De Amsterdamse grachtengordel staat op de UNESCO Werelderfgoedlijst,
    wat betekent dat er internationale erkenning
    is van het bijzondere karakter van dit deel van de historische
    binnenstad. Het aanwijzen van cultureel erfgoed is
    bedoeld om het beter te kunnen bewaren voor toekomstige generaties.

    [Stelselpedia]
    (https://www.amsterdam.nl/stelselpedia/gebieden-index/catalogus/unesco-werelderfgoed/)
    """
    metadata_class = ExpansionMetadata
    queryset = models.Unesco.objects.all()
    serializer_detail_class = serializers.UnescoDetail
    serializer_class = serializers.Unesco


class BouwblokCodeView(RedirectView):
    """
    Bouwblokcode
    """

    permanent = False

    def get_redirect_url(self, *args, **kwargs):
        bouwblok = get_object_or_404(
            models.Bouwblok, code__iexact=kwargs['code'])
        return reverse('bouwblok-detail', kwargs=dict(pk=bouwblok.pk))


class StadsdeelCodeView(RedirectView):
    permanent = False

    def get_redirect_url(self, *args, **kwargs):
        stadsdeel = get_object_or_404(
            models.Stadsdeel, code__iexact=kwargs['code'])
        return reverse('stadsdeel-detail', kwargs=dict(pk=stadsdeel.pk))
