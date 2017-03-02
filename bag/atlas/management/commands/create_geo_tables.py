from django.core.management import BaseCommand
from django.db import ProgrammingError
from django.db import connection


class Command(BaseCommand):
    def handle(self, *args, **options):
        cursor = connection.cursor()
        tables = connection.introspection.get_table_list(cursor)

        for table_info in tables:
            if table_info.type == 'v' and table_info.name[0:4] == 'geo_':
                try:
                    cursor.execute(f'DROP TABLE {table_info.name}_mat')
                except ProgrammingError:
                    pass

                cursor.execute(
                    f'CREATE TABLE {table_info.name}_mat '
                    f'AS SELECT * FROM {table_info.name}')
                cursor.execute(
                    f'CREATE INDEX {table_info.name}_idx '
                    f'ON {table_info.name}_mat USING GIST(geometrie)')
                cursor.execute(
                    f'CLUSTER {table_info.name}_idx '
                    f'ON {table_info.name}_mat')
                cursor.execute(f'VACUUM ANALYZE {table_info.name}_mat')
                self.stdout.write(f'Created geotable {table_info.name}_mat\n')
