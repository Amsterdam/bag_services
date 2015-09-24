from django import template
from django.template import loader, RequestContext, Context

from rest_framework import metadata, viewsets, renderers

from . import serializers, models


class HTMLDetailRenderer(renderers.BaseRenderer):
    format = 'html'
    media_type = 'text/html+detail'

    def render(self, data, accepted_media_type=None, renderer_context=None):
        view = renderer_context['view']
        request = renderer_context['request']

        # todo: not very smart
        obj = view.queryset.get(pk=data['id'])

        tmpl = loader.get_template(view.template_name)
        ctx = RequestContext(request, dict(data=data, object=obj))
        return tmpl.render(ctx)


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


class LigplaatsViewSet(viewsets.ReadOnlyModelViewSet):
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


class StandplaatsViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Een STANDPLAATS is een door het bevoegde gemeentelijke orgaan als zodanig aangewezen terrein of gedeelte daarvan
    dat bestemd is voor het permanent plaatsen van een niet direct en niet duurzaam met de aarde verbonden en voor
    woon -, bedrijfsmatige, of recreatieve doeleinden geschikte ruimte.

    [Stelselpedia](http://www.amsterdam.nl/stelselpedia/bag-index/catalogus-bag/objectklasse-4/)
    """

    metadata_class = ExpansionMetadata
    queryset = models.Standplaats.objects.all()
    serializer_class = serializers.Standplaats


class VerblijfsobjectViewSet(viewsets.ReadOnlyModelViewSet):
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
    renderer_classes = (renderers.JSONRenderer, renderers.BrowsableAPIRenderer, HTMLDetailRenderer)
    template_name = "bag/verblijfsobject.html"


class NummeraanduidingViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Een nummeraanduiding, in de volksmond ook wel adres genoemd, is een door het bevoegde gemeentelijke orgaan als
    zodanig toegekende aanduiding van een verblijfsobject, standplaats of ligplaats.

    [Stelselpedia](http://www.amsterdam.nl/stelselpedia/bag-index/catalogus-bag/objectklasse-2/)
    """

    metadata_class = ExpansionMetadata
    queryset = models.Nummeraanduiding.objects.all()
    serializer_class = serializers.Nummeraanduiding


class PandViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Een PAND is de kleinste bij de totstandkoming functioneel en bouwkundig-constructief zelfstandige eenheid die
    direct en duurzaam met de aarde is verbonden en betreedbaar en afsluitbaar is.

    [Stelselpedia](http://www.amsterdam.nl/stelselpedia/bag-index/catalogus-bag/objectklasse-pand/)
    """

    metadata_class = ExpansionMetadata
    queryset = models.Pand.objects.all()
    serializer_class = serializers.Pand


class OpenbareRuimteViewSet(viewsets.ReadOnlyModelViewSet):
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
