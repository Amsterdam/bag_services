# Python
import logging
# Packages
from django.conf import settings
from django.db import connection
from django.http import HttpResponse
from elasticsearch import Elasticsearch
from elasticsearch.exceptions import TransportError, NotFoundError
from elasticsearch_dsl import Search
# Project
from datasets.bag.models import Verblijfsobject


log = logging.getLogger(__name__)


def health(request):
    # check database
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            assert cursor.fetchone()
    except:
        log.exception("Database connectivity failed")
        return HttpResponse(
            "Database connectivity failed",
            content_type="text/plain", status=500)

    # check elasticsearch
    try:
        client = Elasticsearch(settings.ELASTIC_SEARCH_HOSTS)
        assert client.info()
    except:
        log.exception("Elasticsearch connectivity failed")
        return HttpResponse(
            "Elasticsearch connectivity failed",
            content_type="text/plain", status=500)

    # check debug
    if settings.DEBUG:
        log.exception("Debug mode not allowed in production")
        return HttpResponse(
            "Debug mode not allowed in production",
            content_type="text/plain", status=500)

    return HttpResponse(
        "Health OK", content_type='text/plain', status=200)


def check_data(request):
    # check bag
    try:
        assert Verblijfsobject.objects.count() > 10000
    except:
        log.exception("No BAG data found")
        return HttpResponse(
            "No BAG data found",
            content_type="text/plain", status=500)

    # check elastic
    client = Elasticsearch(settings.ELASTIC_SEARCH_HOSTS)
    for index in settings.ELASTIC_INDICES.values():
        try:
            assert (
                Search()
                .using(client) .index(index)
                .query("match_all", size=0)
            )
        except (TransportError, NotFoundError):
            log.exception("Index missing!")
            return HttpResponse(
                "Elastic Index missing ",
                content_type="text/plain", status=500)

    return HttpResponse("Data OK", content_type='text/plain', status=200)
