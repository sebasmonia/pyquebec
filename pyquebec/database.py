import pypyodbc
from collections import namedtuple
from .dbobjects import Schema, Table
from .querybuilder import QueryBuilder
from .config import get_connections, get_REPL, create_config_db
from .schema_loader import cache_schema

_connections = {name: conn for name, conn in get_connections()}


def add_database(name, connection_string, engine):
    create_config_db(name, connection_string, engine)
    cache schema(name, connection_string, engine)

def connect(connection_name, load_schema=True):
    return DataBase(connection_name, load_schema)


def new_connect(connection_name):
    return DataBase(connection_name, load_schema)


class DataBase:
    def __init__(self, connection_name, load_schema=True):
        self.db_name = connection_name
        if connection_name in _connections:
            self.connection_string = _connections[connection_name]
        else:
            self.connection_string = connection_name
        self.statement_history = []
        if load_schema:
            self._load_schema()

    def _load_schema(self):
        queries = get_REPL()
        schemas = self._run_string_query(queries['Schemas'])
        tables = self._run_string_query(queries['Tables'])
        all_columns = self._run_string_query(queries['Columns'])
        for s in schemas:
            schema_ref = Schema(s.name)
            setattr(self, s.name, schema_ref)
        for t in tables:
            schema_ref = getattr(self, t.schema)
            cols = (col.name for col in all_columns if
                    col.table == t.name and
                    col.schema == t.schema)
            table_ref = Table(self, schema_ref, t.name, cols)
            setattr(schema_ref, t.name, table_ref)

    def schemas(self):
        return {k: v for k, v in vars(self).items() if type(v) == Schema}

    def _run_string_query(self, statement, raw_result=False):
        # default values
        conn = None
        builder = None
        rows_list = []
        try:
            conn = pypyodbc.connect(self.connection_string)
            cursor = conn.cursor()
            cursor.execdirect(statement)
            odbc_rows = cursor.fetchall()
            if not odbc_rows or raw_result:
                # empty list or just tuples
                rows_list = [tuple(row) for row in odbc_rows]
            else:
                columns = (column[0] for column in
                           odbc_rows[0].cursor_description)
                unique = self._make_cols_unique(columns)
                builder = namedtuple('row', unique)
                # builder = _create_next_row_builder(unique)
                rows_list = [builder._make(row) for row in odbc_rows]
        except Exception as error:
            print(error)
            print(self.connection_string)
        finally:
            if conn is not None:
                conn.close()
            self.statement_history.append(statement)
            return rows_list

    def _run_string_non_query(self, statement):
        # default values
        conn = None
        try:
            conn = pypyodbc.connect(self.connection_string, autocommit=True)
            cursor = conn.cursor()
            value = cursor.execute(statement).rowcount
            self.statement_history.append(statement)
            return value
        except Exception as error:
            print(error)
        finally:
            if conn is not None:
                conn.close()

    def exec_query(self, statement, raw_result=False):
        return self._run_string_query(statement, raw_result)

    def new_query(self):
        if self.schemas():
            return QueryBuilder(self)
        else:
            print("Schema information not available")

    def _make_cols_unique(self, cols):
        seen = []
        for c in cols:
            counter = 1
            while c in seen:
                c = c + ("_" * counter)
                counter += 1
            seen.append(c)
        return seen
