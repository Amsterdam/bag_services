from django.db import connection


def clear_model(model):
    """
    Truncates the table associated with ``model`` and all related tables.
    """
    # noinspection PyProtectedMember
    connection.cursor().execute("TRUNCATE {} CASCADE".format(model._meta.db_table))