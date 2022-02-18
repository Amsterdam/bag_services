from django.db import connection
from django.db.models import QuerySet
from django.db.utils import InternalError as DjangoInternalError
from psycopg2 import InternalError as Psycopg2InternalError

BATCH_SIZE = 50_000


def count_qs(qs: QuerySet) -> int:
    """Workaround count(*) issue in postgresql/django by falling back to count(first_column)."""
    try:
        return qs.count()
    except (DjangoInternalError, Psycopg2InternalError):
        # Fallback: Try to compile query to sql
        from_, param = qs.query.as_sql('compiler', connection)
        return count_sql(table=f"({from_})", param=param, quote=False)


def count_sql(table: str, param=None, quote: bool = True) -> int:
    """
    Count length table or subquery based on first column.

    :param table: table or subquery (incl ())
    :param param: Optional parameters to subquery
    :param quote: quote the table if true
    :returns: number of rows in table
    """
    from_ = connection.ops.quote_name(table) if quote else table

    with connection.cursor() as cursor:
        # Get first column name from table to force count on
        # workaround query planning issue in postgresql 11.15
        # https://www.postgresql.org/message-id/2121219.1644607692%40sss.pgh.pa.us
        cursor.execute(f'SELECT * FROM {from_} cnt LIMIT 1', param)
        column = cursor.description[0][0]

        cursor.execute(f'SELECT COUNT({column}) FROM {from_} cnt', param)
        row = cursor.fetchone()

    return row[0] if row else 0
