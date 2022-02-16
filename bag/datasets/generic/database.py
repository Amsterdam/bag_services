from django.db import connection

BATCH_SIZE = 50000


def sql_count(table: str) -> int:
    sql_table = connection.ops.quote_name(table)

    with connection.cursor() as cursor:
        # Get first column name from table to force count on
        # workaround query planning issue in postgresql 11.15
        # https://www.postgresql.org/message-id/2121219.1644607692%40sss.pgh.pa.us
        cursor.execute(f'SELECT * FROM {sql_table} LIMIT 1')
        column = cursor.description[0][0]

        cursor.execute(f'SELECT COUNT({column}) FROM {sql_table}')
        row = cursor.fetchone()

    return row[0] if row else 0
