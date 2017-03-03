from django.db.migrations.operations.base import Operation

view_history = dict()


class ManageView(Operation):
    reversible = True

    def __init__(self, view_name, sql):
        super().__init__()
        self.view_name = view_name
        self.sql = sql

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
        schema_editor.execute(f'DROP VIEW IF EXISTS {self.view_name}')
        schema_editor.execute(f'DROP TABLE IF EXISTS {self.view_name}_mat')
        schema_editor.execute(f'DROP VIEW IF EXISTS {self.view_name}_mat')

        schema_editor.execute(f'CREATE VIEW {self.view_name} AS {self.sql}')
        schema_editor.execute(f'CREATE MATERIALIZED VIEW {self.view_name}_mat '
                              f'AS {self.sql}')
        self._create_mat_geo_index(schema_editor, self.view_name)

    def database_backwards(self, app_label, schema_editor, from_state,
                           to_state):
        schema_editor.execute(f'DROP VIEW IF EXISTS {self.view_name}')
        schema_editor.execute(f'DROP TABLE IF EXISTS {self.view_name}_mat')
        schema_editor.execute(f'DROP VIEW IF EXISTS {self.view_name}_mat')
        previous = self.pop_previous_sql(app_label)

        if previous:
            schema_editor.execute(f'CREATE VIEW {self.view_name} AS {previous}')
            schema_editor.execute(
                f'CREATE MATERIALIZED VIEW {self.view_name}_mat AS {previous}')

    def state_forwards(self, app_label, state):
        self.push_history(app_label)

    def describe(self):
        return f"Create normal and materialized view {self.view_name}"

    def _create_mat_geo_index(self, schema_editor, viewname, prefix='geo_'):
        if prefix and self.view_name.startswith(prefix):
            statement = f"""CREATE INDEX {viewname}_mat_idx
                            ON {viewname}_mat
                            USING  GIST (geometrie)"""

            schema_editor.execute(statement)
