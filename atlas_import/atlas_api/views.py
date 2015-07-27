from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets
from atlas import models
from atlas_api import serializers


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

