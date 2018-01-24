from django.core.management import BaseCommand
from django.db import ProgrammingError
from django.db import connection
from psycopg2 import sql


class Command(BaseCommand):
    def handle(self, *args, **options):
        with connection.cursor() as cursor:
            self.create_geo(cursor)

    def create_geo(self, cursor):
        tables = connection.introspection.get_table_list(cursor)

        for table_info in tables:
            if table_info.type == 'v' and table_info.name[0:4] == 'geo_':
                try:
                    cursor.execute(
                        'DROP TABLE IF EXISTS {}'.format(
                            sql.Identifier(f"{table_info.name}_mat")
                        )
                    )
                except ProgrammingError:
                    pass

                cursor.execute(
                    'CREATE TABLE {} AS SELECT * FROM {}'.format(
                        sql.Identifier(f"{table_info.name}_mat"),
                        sql.Identifier(table_info.name)
                    )
                )
                cursor.execute(
                    'CREATE INDEX {} ON {} USING GIST(geometrie)'.format(
                        sql.Identifier(f"{table_info.name}_idx"),
                        sql.Identifier(f"{table_info.name}_mat")
                    )
                )
                cursor.execute(
                    'CLUSTER {} ON {}'.format(
                        sql.Identifier(f"{table_info.name}_idx"),
                        sql.Identifier(f"{table_info.name}_mat")
                    )
                )
                cursor.execute(
                    'VACUUM ANALYZE {}'.format(
                        sql.Identifier(f"{table_info.name}_mat"),
                    )
                )
                self.stdout.write(f'Created geotable {table_info.name}_mat\n')
