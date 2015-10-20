from rest_framework import metadata

from . import serializers, models
from datasets.generic import rest


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
    serializer_class = serializers.Ligplaats
    template_name = "bag/ligplaats.html"


class StandplaatsViewSet(rest.AtlasViewSet):
    """
    Een STANDPLAATS is een door het bevoegde gemeentelijke orgaan als zodanig aangewezen terrein of gedeelte daarvan
    dat bestemd is voor het permanent plaatsen van een niet direct en niet duurzaam met de aarde verbonden en voor
    woon -, bedrijfsmatige, of recreatieve doeleinden geschikte ruimte.

    [Stelselpedia](http://www.amsterdam.nl/stelselpedia/bag-index/catalogus-bag/objectklasse-4/)
    """

    metadata_class = ExpansionMetadata
    queryset = models.Standplaats.objects.all()
    serializer_class = serializers.Standplaats
    template_name = "bag/standplaats.html"


class VerblijfsobjectViewSet(rest.AtlasViewSet):
    """
    Een VERBLIJFSOBJECT is de kleinste binnen één of meer panden gelegen en voor woon -, bedrijfsmatige, of recreatieve
    doeleinden geschikte eenheid van gebruik die ontsloten wordt via een eigen afsluitbare toegang vanaf de openbare
    weg, een erf of een gedeelde verkeersruimte, onderwerp kan zijn van goederenrechtelijke rechtshandelingen en in
    functioneel opzicht zelfstandig is.

    [Stelselpedia](http://www.amsterdam.nl/stelselpedia/bag-index/catalogus-bag/objectklasse-0/)
    """

    metadata_class = ExpansionMetadata
    queryset = models.Verblijfsobject.objects.all()
    serializer_class = serializers.Verblijfsobject
    template_name = "bag/verblijfsobject.html"


class NummeraanduidingViewSet(rest.AtlasViewSet):
    """
    Een nummeraanduiding, in de volksmond ook wel adres genoemd, is een door het bevoegde gemeentelijke orgaan als
    zodanig toegekende aanduiding van een verblijfsobject, standplaats of ligplaats.

    [Stelselpedia](http://www.amsterdam.nl/stelselpedia/bag-index/catalogus-bag/objectklasse-2/)
    """

    metadata_class = ExpansionMetadata
    queryset = models.Nummeraanduiding.objects.all()
    serializer_class = serializers.Nummeraanduiding
    template_name = "bag/nummeraanduiding.html"


class PandViewSet(rest.AtlasViewSet):
    """
    Een PAND is de kleinste bij de totstandkoming functioneel en bouwkundig-constructief zelfstandige eenheid die
    direct en duurzaam met de aarde is verbonden en betreedbaar en afsluitbaar is.

    [Stelselpedia](http://www.amsterdam.nl/stelselpedia/bag-index/catalogus-bag/objectklasse-pand/)
    """

    metadata_class = ExpansionMetadata
    queryset = models.Pand.objects.all()
    serializer_class = serializers.Pand
    template_name = "bag/pand.html"


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
    serializer_class = serializers.OpenbareRuimte
    template_name = "bag/openbare_ruimte.html"


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
    serializer_class = serializers.Gemeente


class StadsdeelViewSet(rest.AtlasViewSet):
    """
    Door de Amsterdamse gemeenteraad vastgestelde begrenzing van een stadsdeel, ressorterend onder een stadsdeelbestuur.

    [Stelselpedia](https://www.amsterdam.nl/stelselpedia/gebieden-index/catalogus/stadsdeel/)
    """

    metadata_class = ExpansionMetadata
    queryset = models.Stadsdeel.objects.all()
    serializer_class = serializers.Stadsdeel


class BuurtViewSet(rest.AtlasViewSet):
    """
    Een aaneengesloten gedeelte van een buurt, waarvan de grenzen zo veel mogelijk gebaseerd zijn op topografische
    elementen.

    [Stelselpedia](https://www.amsterdam.nl/stelselpedia/gebieden-index/catalogus/buurt/)
    """

    metadata_class = ExpansionMetadata
    queryset = models.Buurt.objects.all()
    serializer_class = serializers.Buurt


class BouwblokViewSet(rest.AtlasViewSet):
    """
    Een bouwblok is het kleinst mogelijk afgrensbare gebied, in zijn geheel tot een buurt behorend, dat geheel of
    grotendeels door bestaande of aan te leggen wegen en/of waterlopen is of zal zijn ingesloten en waarop tenminste
    één gebouw staat.

    [Stelselpedia](https://www.amsterdam.nl/stelselpedia/gebieden-index/catalogus/bouwblok/)
    """

    metadata_class = ExpansionMetadata
    queryset = models.Bouwblok.objects.all()
    serializer_class = serializers.Bouwblok
