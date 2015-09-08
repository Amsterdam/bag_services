from django.conf import settings
from elasticsearch_dsl.connections import connections
from datasets.bag import documents, models


class ImportELLigplaatsTask(object):
    name = "EL: import ligplaatsen"

    def __init__(self):
        connections.create_connection(hosts=settings.ELASTIC_SEARCH_HOSTS)
        documents.Ligplaats.init()

    def execute(self):
        for l in models.Ligplaats.objects.all():
            doc = documents.from_ligplaats(l)
            doc.save()


class ImportELStandplaatsTask(object):
    name = "EL: import standplaatsen"

    def __init__(self):
        connections.create_connection(hosts=settings.ELASTIC_SEARCH_HOSTS)
        documents.Standplaats.init()

    def execute(self):
        for s in models.Standplaats.objects.all():
            doc = documents.from_standplaats(s)
            doc.save()


class ImportELVerblijfsobjectTask(object):
    name = "EL: import verblijfsobjecten"

    def __init__(self):
        connections.create_connection(hosts=settings.ELASTIC_SEARCH_HOSTS)
        documents.Verblijfsobject.init()

    def execute(self):
        for v in models.Verblijfsobject.objects.all():
            doc = documents.from_verblijfsobject(v)
            doc.save()