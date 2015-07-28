# Create your views here.
from django.conf import settings
from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search
from rest_framework import viewsets
from rest_framework.decorators import api_view

from rest_framework.response import Response

from atlas import models
from atlas_api import serializers
from atlas_api.serializers import Autocomplete


class LigplaatsViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = models.Ligplaats.objects.all()
    serializer_class = serializers.Ligplaats


class StandplaatsViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = models.Standplaats.objects.all()
    serializer_class = serializers.Standplaats


class VerblijfsobjectViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = models.Verblijfsobject.objects.all()
    serializer_class = serializers.Verblijfsobject


class NummeraanduidingViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = models.Nummeraanduiding.objects.all()
    serializer_class = serializers.Nummeraanduiding


class PandViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = models.Pand.objects.all()
    serializer_class = serializers.Pand


@api_view(['GET'])
def search(request):
    query = request.GET['q']

    client = Elasticsearch(settings.ELASTIC_SEARCH_HOSTS)
    s = Search(client)
    for part in query.split():
        s = s.query("match_phrase_prefix", _all=part)

    result = s.execute()
    data = [dict(id=h.meta.id, value=h.adres) for h in result]
    autocomplete = Autocomplete(data=data)
    return Response(autocomplete.initial_data)
