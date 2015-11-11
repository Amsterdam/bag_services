import logging

from django.conf import settings
from django.db import connection
from django.http import HttpResponse
from elasticsearch import Elasticsearch

from atlas_api.views import get_autocomplete_response
from datasets.bag.models import Verblijfsobject


log = logging.getLogger(__name__)


def health(request):
    # check database
    try:
        with connection.cursor() as cursor:
            cursor.execute("select 1")
            assert cursor.fetchone()
    except:
        log.exception()
        return HttpResponse("Database connectivity failed", content_type="text/plain", status=500)

    # check elasticsearch
    try:
        client = Elasticsearch(settings.ELASTIC_SEARCH_HOSTS)
        assert client.info()
    except:
        log.exception()
        return HttpResponse("Elasticsearch connectivity failed", content_type="text/plain", status=500)

    return HttpResponse("Connectivity OK", content_type='text/plain', status=200)


def check_data(request):
    # check bag
    try:
        assert Verblijfsobject.objects.count() > 10
    except:
        log.exception()
        return HttpResponse("No BAG data found", content_type="text/plain", status=500)

    # check elastic
    try:
        client = Elasticsearch(settings.ELASTIC_SEARCH_HOSTS)
        assert get_autocomplete_response(client, 'weesp')
    except:
        log.exception()
        return HttpResponse("Autocomplete failed", content_type="text/plain", status=500)

    return HttpResponse("Data OK", content_type='text/plain', status=200)
