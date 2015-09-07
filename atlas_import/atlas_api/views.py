# Create your views here.
from django.conf import settings
from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search
from rest_framework import viewsets, metadata
from rest_framework.response import Response
from rest_framework.reverse import reverse

from atlas_api.serializers import Autocomplete


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
