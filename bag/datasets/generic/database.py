from typing import Union

from django.db import connection
from django.db.models import QuerySet

BATCH_SIZE = 50000


def sql_count(table: Union[QuerySet, str]) -> int:
    if isinstance(table, QuerySet):
        from_, param = table.query.as_sql('compiler', connection)
        from_ = f"({from_})"
    else:
        from_, param = connection.ops.quote_name(table), None

    with connection.cursor() as cursor:
        # Get first column name from table to force count on
        # workaround query planning issue in postgresql 11.15
        # https://www.postgresql.org/message-id/2121219.1644607692%40sss.pgh.pa.us
        cursor.execute(f'SELECT * FROM {from_} cnt LIMIT 1', param)
        column = cursor.description[0][0]

        cursor.execute(f'SELECT COUNT({column}) FROM {from_} cnt', param)
        row = cursor.fetchone()

    return row[0] if row else 0
