import pypyodbc
from collections import namedtuple
from .dbobjects import Schema, Table
from .querybuilder import QueryBuilder
import configparser
import sys

_config_file_path = __file__.replace(".py", ".ini")
_config = configparser.ConfigParser()
_config.optionxform = str
_config.read(_config_file_path)

_connections = {name: conn for name, conn in _config['Connections'].items()}


def connect(connection_name, load_schema=True):
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
        queries = _config['REPL_Queries']
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
                builder = _create_next_row_builder(unique)
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


def _create_next_row_builder(columns):
    module_self = sys.modules[__name__]
    var_name = "_row_builder"
    for num in range(1000):
        var_name = "_row_builder" + str(num)
        if not hasattr(module_self, var_name):
            break
    builder = namedtuple('row', columns)
    setattr(module_self, var_name, builder)
    return builder
