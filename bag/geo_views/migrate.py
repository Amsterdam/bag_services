import logging

from django.db import connection
from django.db.migrations.operations.base import Operation

view_history = dict()


class ManageView(Operation):
    reversible = True

    def __init__(self, view_name, sql):
        super().__init__()
        self.view_name = view_name
        self.sql = sql
        self.logger = logging.getLogger('datapunt.bag.ManageView')

    def push_history(self, app_label):
        view_name = '{}-{}'.format(app_label, self.view_name)
        view_history.setdefault(view_name, []).append(self.sql)

    def pop_previous_sql(self, app_label):
        view_name = '{}-{}'.format(app_label, self.view_name)
        history = view_history.get(view_name)
        if not history:
            return None

        history.pop()
        if not history:
            return None

        history.pop()
        if not history:
            return None

        return history[-1]

    def database_forwards(self, app_label, schema_editor, from_state, to_state):
        self._drop_view_and_materialized_things(schema_editor, self.view_name)
        self._create_geo_indices(schema_editor, self.view_name, self.sql)

    def database_backwards(self, app_label, schema_editor, from_state,
                           to_state):
        self._drop_view_and_materialized_things(schema_editor, self.view_name)
        previous_select = self.pop_previous_sql(app_label)

        if previous_select:
            self._create_geo_indices(schema_editor,
                                     self.view_name, previous_select)

    def state_forwards(self, app_label, state):
        self.push_history(app_label)

    def describe(self):
        return f"Create normal and materialized view {self.view_name}"

    def _drop_view_and_materialized_things(self, se, relname):
        self.logger.info(f'Cleaning up: {relname}.')
        cursor = connection.cursor()
        base_stmt = "SELECT count(relname) FROM pg_class " \
                    "WHERE relkind = '{type}' AND relname = '{relname}'"

        cursor.execute(base_stmt.format(type='v', relname=relname))
        if cursor.fetchall()[0][0] > 0:
            se.execute(f'DROP VIEW IF EXISTS {relname}')
            self.logger.info(f'View {relname} dropped.')

        cursor.execute(base_stmt.format(type='r', relname=relname))
        if cursor.fetchall()[0][0] > 0:
            se.execute(f'DROP TABLE IF EXISTS {relname}')
            self.logger.info(f'Table {relname} dropped.')

        cursor.execute(base_stmt.format(type='v', relname=f'{relname}_mat'))
        if cursor.fetchall()[0][0] > 0:
            se.execute(f'DROP MATERIALIZED VIEW IF EXISTS {relname}_mat')
            self.logger.info(f'Materialised View {relname}_mat dropped.')

        cursor.execute(base_stmt.format(type='r', relname=f'{relname}_mat'))
        if cursor.fetchall()[0][0] > 0:
            se.execute(f'DROP TABLE IF EXISTS {relname}_mat')
            self.logger.info(f'Table {relname}_mat dropped.')

    @staticmethod
    def _create_geo_indices(se, viewname, sql, prefix='geo_'):
        se.execute(f'CREATE VIEW {viewname} AS {sql}')

        # Todo: Bugfix in progress. Fails without this next line.
        se.execute(f'DROP MATERIALIZED VIEW IF EXISTS {viewname}_mat')
        se.execute(f'CREATE MATERIALIZED VIEW {viewname}_mat AS {sql}')

        if not prefix or viewname.startswith(prefix):
            se.execute(f"""CREATE INDEX {viewname}_mat_idx
                            ON {viewname}_mat
                            USING  GIST (geometrie)""")
