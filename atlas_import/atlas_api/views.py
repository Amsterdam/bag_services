# Create your views here.
from django.conf import settings
from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search
from rest_framework import viewsets, metadata
from rest_framework.response import Response
from rest_framework.reverse import reverse

from atlas import models
from atlas_api import serializers
from atlas_api.serializers import Autocomplete


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


def _get_url(request, doc_type, id):
    if doc_type == "ligplaats":
        return reverse('ligplaats-detail', args=(id,), request=request)

    if doc_type == "standplaats":
        return reverse('standplaats-detail', args=(id,), request=request)

    if doc_type == "verblijfsobject":
        return reverse('verblijfsobject-detail', args=(id,), request=request)

    return None


class TypeaheadMetadata(metadata.SimpleMetadata):
    def determine_metadata(self, request, view):
        result = super().determine_metadata(request, view)
        result['parameters'] = dict(
            q=dict(
                type="string",
                description="The query to search for",
                required=False
            )
        )
        return result


class TypeaheadViewSet(viewsets.ViewSet):
    """
    Given a query parameter `q`, this function returns a subset of all objects that (partially) match the
    specified query.
    """

    metadata_class = TypeaheadMetadata

    def list(self, request, *args, **kwargs):
        if 'q' not in request.QUERY_PARAMS:
            return Response([])

        query = request.QUERY_PARAMS['q']

        client = Elasticsearch(settings.ELASTIC_SEARCH_HOSTS)
        s = Search(client)
        for part in query.split():
            s = s.query("match_phrase_prefix", _all=part)
        result = s.index("atlas").execute()

        data = [dict(
            id=h.meta.id,
            url=_get_url(request, h.meta.doc_type, h.meta.id),
            type=h.meta.doc_type,
            adres=h.get('adres'),
            postcode=h.get('postcode'),
            oppervlakte=h.get('oppervlakte'),
            kamers=h.get('kamers'),
            bestemming=h.get('bestemming'),
            centroid=h.get('centroid'),
        ) for h in result]

        autocomplete = Autocomplete(data=data)
        return Response(autocomplete.initial_data)
