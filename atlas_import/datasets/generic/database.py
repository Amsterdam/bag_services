from django.db import connection


def clear_models(*models):
    """
    Truncates the table associated with ``model`` and all related tables.
    """
    for model in models:
        # noinspection PyProtectedMember
        connection.cursor().execute("TRUNCATE {} CASCADE".format(model._meta.db_table))