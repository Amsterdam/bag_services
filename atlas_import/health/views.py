from django.conf import settings
from django.db import connection
from django.http import HttpResponse
from elasticsearch import Elasticsearch

from atlas_api.views import get_autocomplete_response
from datasets.bag.models import Verblijfsobject


def health(request):
    # check database
    with connection.cursor() as cursor:
        cursor.execute("select 1")
        result = cursor.fetchone()
        if not result:
            raise ValueError("Could not connect to database")
        if result[0] is not 1:
            raise ValueError("Could not retrieve results from database")

    # check elasticsearch
    client = Elasticsearch(settings.ELASTIC_SEARCH_HOSTS)
    info = client.info()

    if not info:
        raise ValueError("Could not connect to elasticsearch")

    return HttpResponse("OK", content_type='text/plain', status=200)


def check_data(request):
    # check bag
    if Verblijfsobject.objects.count() < 10:
        raise ValueError("Suspiciously low amount of verblijfsobjecten")

    # check elastic
    client = Elasticsearch(settings.ELASTIC_SEARCH_HOSTS)
    response = get_autocomplete_response(client, 'weesp')
    if not response:
        raise ValueError("No result for elastic queries")

    return HttpResponse("OK", content_type='text/plain', status=200)
