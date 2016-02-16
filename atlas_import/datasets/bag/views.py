from django.db.models import Prefetch
from django.shortcuts import get_object_or_404
from django.views.generic import RedirectView
from rest_framework import metadata
from rest_framework.reverse import reverse

from datasets.generic import rest
from . import serializers, models


class ExpansionMetadata(metadata.SimpleMetadata):
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


class LigplaatsViewSet(rest.AtlasViewSet):
    """
    Een LIGPLAATS is een door het bevoegde gemeentelijke orgaan als zodanig aangewezen plaats in het water
    al dan niet aangevuld met een op de oever aanwezig terrein of een gedeelte daarvan,
    die bestemd is voor het permanent afmeren van een voor woon-, bedrijfsmatige of recreatieve doeleinden geschikt
    vaartuig.

    [Stelselpedia](http://www.amsterdam.nl/stelselpedia/bag-index/catalogus-bag/objectklasse-1/)
    """

    metadata_class = ExpansionMetadata
    queryset = models.Ligplaats.objects.all()
    serializer_detail_class = serializers.LigplaatsDetail
    serializer_class = serializers.Ligplaats
    filter_fields = ('buurt',)


class StandplaatsViewSet(rest.AtlasViewSet):
    """
    Een STANDPLAATS is een door het bevoegde gemeentelijke orgaan als zodanig aangewezen terrein of gedeelte daarvan
    dat bestemd is voor het permanent plaatsen van een niet direct en niet duurzaam met de aarde verbonden en voor
    woon -, bedrijfsmatige, of recreatieve doeleinden geschikte ruimte.

    [Stelselpedia](http://www.amsterdam.nl/stelselpedia/bag-index/catalogus-bag/objectklasse-4/)
    """

    metadata_class = ExpansionMetadata
    queryset = models.Standplaats.objects.all()
    serializer_detail_class = serializers.StandplaatsDetail
    serializer_class = serializers.Standplaats
    filter_fields = ('buurt',)


class VerblijfsobjectViewSet(rest.AtlasViewSet):
    """
    Een VERBLIJFSOBJECT is de kleinste binnen één of meer panden gelegen en voor woon -, bedrijfsmatige, of recreatieve
    doeleinden geschikte eenheid van gebruik die ontsloten wordt via een eigen afsluitbare toegang vanaf de openbare
    weg, een erf of een gedeelde verkeersruimte, onderwerp kan zijn van goederenrechtelijke rechtshandelingen en in
    functioneel opzicht zelfstandig is.

    [Stelselpedia](http://www.amsterdam.nl/stelselpedia/bag-index/catalogus-bag/objectklasse-0/)
    """

    metadata_class = ExpansionMetadata
    queryset = models.Verblijfsobject.objects
    serializer_detail_class = serializers.VerblijfsobjectDetail
    serializer_class = serializers.Verblijfsobject
    filter_fields = ('kadastrale_objecten__id', 'panden__id', 'buurt',)


class NummeraanduidingViewSet(rest.AtlasViewSet):
    """
    Een nummeraanduiding, in de volksmond ook wel adres genoemd, is een door het bevoegde gemeentelijke orgaan als
    zodanig toegekende aanduiding van een verblijfsobject, standplaats of ligplaats.

    [Stelselpedia](http://www.amsterdam.nl/stelselpedia/bag-index/catalogus-bag/objectklasse-2/)
    """

    metadata_class = ExpansionMetadata
    queryset = models.Nummeraanduiding.objects.all()
    queryset_detail = models.Nummeraanduiding.objects.prefetch_related(
            Prefetch('verblijfsobject__panden', queryset=models.Pand.objects.select_related('bouwblok'))
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
    filter_fields = ('verblijfsobject', 'ligplaats', 'standplaats', 'openbare_ruimte')


class PandViewSet(rest.AtlasViewSet):
    """
    Een PAND is de kleinste bij de totstandkoming functioneel en bouwkundig-constructief zelfstandige eenheid die
    direct en duurzaam met de aarde is verbonden en betreedbaar en afsluitbaar is.

    [Stelselpedia](http://www.amsterdam.nl/stelselpedia/bag-index/catalogus-bag/objectklasse-pand/)
    """

    metadata_class = ExpansionMetadata
    queryset = models.Pand.objects.all()
    serializer_detail_class = serializers.PandDetail
    serializer_class = serializers.Pand
    filter_fields = ('verblijfsobjecten__id', 'bouwblok',)


class OpenbareRuimteViewSet(rest.AtlasViewSet):
    """
    Een OPENBARE RUIMTE is een door het [bevoegde gemeentelijke orgaan als zodanig aangewezen en van een naam
    voorziene buitenruimte](http://www.amsterdam.nl/stelselpedia/bag-index/handboek-inwinnen/openbare-ruimte/)
    die binnen één woonplaats is gelegen.

    Als openbare ruimte worden onder meer aangemerkt weg, water, terrein, spoorbaan en landschappelijk gebied.

    Bron: [Catalogus BAG (ministerie van VROM, 2009)](
    http://www.kadaster.nl/web/artikel/download/BAG-grondslagen-catalogus.htm).

    [Stelselpedia](http://www.amsterdam.nl/stelselpedia/bag-index/catalogus-bag/objectklasse-3/)
    """

    metadata_class = ExpansionMetadata
    queryset = models.OpenbareRuimte.objects.all()
    serializer_detail_class = serializers.OpenbareRuimteDetail
    serializer_class = serializers.OpenbareRuimte


class WoonplaatsViewSet(rest.AtlasViewSet):
    """
    Een WOONPLAATS is een door het bevoegde gemeentelijke orgaan als zodanig aangewezen en van een naam voorzien
    gedeelte
    van het grondgebied van de gemeente. Vanaf 10 januari 2014 bestaat alleen nog de woonplaats Amsterdam met
    Woonplaatsidentificatie 3594.

    [Stelselpedia](https://www.amsterdam.nl/stelselpedia/bag-index/catalogus-bag/objectklasse/)
    """

    metadata_class = ExpansionMetadata
    queryset = models.Woonplaats.objects.all()
    serializer_detail_class = serializers.WoonplaatsDetail
    serializer_class = serializers.Woonplaats


# gebieden
class GemeenteViewSet(rest.AtlasViewSet):
    """
    Een gemeente is een afgebakend gedeelte van het grondgebied van Nederland, ingesteld op basis van artikel 123 van
    de Grondwet.

    Verder is een gemeente zelfstandig, heeft zij zelfbestuur en is onderdeel van de staat. Zij staat onder bestuur van
    een raad, een burgemeester en wethouders.

    De gemeentegrens wordt door de centrale overheid vastgesteld, en door het Kadaster vastgelegd.

    [Stelselpedia](https://www.amsterdam.nl/stelselpedia/brk-index/catalogus/objectklasse-2/)
    """

    metadata_class = ExpansionMetadata
    queryset = models.Gemeente.objects.all()
    serializer_detail_class = serializers.GemeenteDetail
    serializer_class = serializers.Gemeente
    template_name = "gebieden/gemeente.html"


class StadsdeelViewSet(rest.AtlasViewSet):
    """
    Door de Amsterdamse gemeenteraad vastgestelde begrenzing van een stadsdeel, ressorterend onder een stadsdeelbestuur.

    [Stelselpedia](https://www.amsterdam.nl/stelselpedia/gebieden-index/catalogus/stadsdeel/)
    """

    metadata_class = ExpansionMetadata
    queryset = models.Stadsdeel.objects.all()
    serializer_detail_class = serializers.StadsdeelDetail
    serializer_class = serializers.Stadsdeel


class BuurtViewSet(rest.AtlasViewSet):
    """
    Een aaneengesloten gedeelte van een buurt, waarvan de grenzen zo veel mogelijk gebaseerd zijn op topografische
    elementen.

    [Stelselpedia](https://www.amsterdam.nl/stelselpedia/gebieden-index/catalogus/buurt/)
    """

    metadata_class = ExpansionMetadata
    queryset = models.Buurt.objects.all()
    serializer_detail_class = serializers.BuurtDetail
    serializer_class = serializers.Buurt
    filter_fields = ('stadsdeel', 'buurtcombinatie')


class BouwblokViewSet(rest.AtlasViewSet):
    """
    Een bouwblok is het kleinst mogelijk afgrensbare gebied, in zijn geheel tot een buurt behorend, dat geheel of
    grotendeels door bestaande of aan te leggen wegen en/of waterlopen is of zal zijn ingesloten en waarop tenminste
    één gebouw staat.

    [Stelselpedia](https://www.amsterdam.nl/stelselpedia/gebieden-index/catalogus/bouwblok/)
    """

    metadata_class = ExpansionMetadata
    queryset = models.Bouwblok.objects.all()
    serializer_detail_class = serializers.BouwblokDetail
    serializer_class = serializers.Bouwblok
    filter_fields = ('buurt',)


class BuurtcombinatieViewSet(rest.AtlasViewSet):
    """
    Een aaneengesloten gedeelte van het grondgebied van een gemeente, waarvan de grenzen zo veel mogelijk zijn
    gebaseerd op sociaal-geografische kenmerken.

    [Stelselpedia](https://www.amsterdam.nl/stelselpedia/gebieden-index/catalogus/buurtcombinatie/)
    """
    metadata_class = ExpansionMetadata
    queryset = models.Buurtcombinatie.objects.all()
    serializer_detail_class = serializers.BuurtcombinatieDetail
    serializer_class = serializers.Buurtcombinatie
    filter_fields = ('stadsdeel',)


class GebiedsgerichtwerkenViewSet(rest.AtlasViewSet):
    """
    Gebiedsgericht werken is een manier van werken om samenwerken in de stad te verbeteren. De samenwerking betreft
    gemeente, bewoners, ondernemers, (lokale) partners en maatschappelijke organisaties.

    [Stelselpedia](https://www.amsterdam.nl/stelselpedia/gebieden-index/catalogus/gebiedsgericht/)
    """

    metadata_class = ExpansionMetadata
    queryset = models.Gebiedsgerichtwerken.objects.all()
    serializer_detail_class = serializers.GebiedsgerichtwerkenDetail
    serializer_class = serializers.Gebiedsgerichtwerken
    filter_fields = ('stadsdeel',)


class GrootstedelijkgebiedViewSet(rest.AtlasViewSet):
    """
    Grootstedelijke gebieden zijn gebieden binnen de gemeente Amsterdam, waar de gemeenteraad, het college van
    burgemeester en wethouders of de burgemeester bevoegd is.

    [Stelselpedia](https://www.amsterdam.nl/stelselpedia/gebieden-index/catalogus/grootstedelijk/)
    """
    metadata_class = ExpansionMetadata
    queryset = models.Grootstedelijkgebied.objects.all()
    serializer_detail_class = serializers.GrootstedelijkgebiedDetail
    serializer_class = serializers.Grootstedelijkgebied


class UnescoViewSet(rest.AtlasViewSet):
    """
    De Amsterdamse grachtengordel staat op de UNESCO Werelderfgoedlijst, wat betekent dat er internationale erkenning
    is van het bijzondere karakter van dit deel van de historische binnenstad. Het aanwijzen van cultureel erfgoed is
    bedoeld om het beter te kunnen bewaren voor toekomstige generaties.

    [Stelselpedia](https://www.amsterdam.nl/stelselpedia/gebieden-index/catalogus/unesco-werelderfgoed/)
    """
    metadata_class = ExpansionMetadata
    queryset = models.Unesco.objects.all()
    serializer_detail_class = serializers.UnescoDetail
    serializer_class = serializers.Unesco


class BouwblokCodeView(RedirectView):

    permanent = True

    def get_redirect_url(self, *args, **kwargs):
        bouwblok = get_object_or_404(models.Bouwblok, code__iexact=kwargs['code'])
        return reverse('bouwblok-detail', kwargs=dict(pk=bouwblok.pk))