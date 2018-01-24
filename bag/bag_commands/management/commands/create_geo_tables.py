from django.core.management import BaseCommand
from django.db import ProgrammingError
from django.db import connection
from psycopg2.extensions import quote_ident


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
                            quote_ident(f"{table_info.name}_mat", cursor)
                        )
                    )
                except ProgrammingError:
                    pass

                cursor.execute(
                    'CREATE TABLE {} AS SELECT * FROM {}'.format(
                        quote_ident(f"{table_info.name}_mat", cursor),
                        quote_ident(table_info.name, cursor)
                    )
                )
                cursor.execute(
                    'CREATE INDEX {} ON {} USING GIST(geometrie)'.format(
                        quote_ident(f"{table_info.name}_idx", cursor),
                        quote_ident(f"{table_info.name}_mat", cursor)
                    )
                )
                cursor.execute(
                    'CLUSTER {} ON {}'.format(
                        quote_ident(f"{table_info.name}_idx", cursor),
                        quote_ident(f"{table_info.name}_mat", cursor)
                    )
                )
                cursor.execute(
                    'VACUUM ANALYZE {}'.format(
                        quote_ident(f"{table_info.name}_mat", cursor),
                    )
                )
                self.stdout.write(f'Created geotable {table_info.name}_mat\n')
