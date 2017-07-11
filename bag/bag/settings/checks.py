from django.conf import settings
from django.core import checks

@checks.register
def check_elasticsearch(app_configs, **kwargs):
    import elasticsearch
    import elasticsearch_dsl

    try:
        client = elasticsearch.Elasticsearch(settings.ELASTIC_SEARCH_HOSTS)
        es = elasticsearch_dsl.Search()
        es.using(client).query("match", all="x").execute()
        return []
    except AttributeError as e:
        return [checks.Error("ELASTIC_SEARCH_HOSTS not in settings")]
    except BaseException as e:
        return [checks.Error(
            "No elastic search server found on {}".format(settings.ELASTIC_SEARCH_HOSTS),
        )]


@checks.register
def check_database(app_configs, **kwargs):
    from django.db import connection

    try:
        cursor = connection.cursor()
        cursor.execute("select 1")
        return []
    except BaseException as e:
        return [checks.Error(
            "No database found on {}".format(settings.DATABASES['default'].get('HOST')),
        )]
