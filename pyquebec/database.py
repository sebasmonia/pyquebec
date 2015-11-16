import pypyodbc
from collections import namedtuple
from .querybuilder import QueryBuilder
from .config import create_config_db, get_connection_string, get_uses_schema
from .schema_reader import cache_schema, read_schema_from_cache


def add_database(name, connection_string, engine):
    create_config_db(name, connection_string, engine)
    db_instance = DataBase(name, None)
    cache_schema(name, db_instance)
    return connect(name)


def connect(name, load_schema=True):
    if load_schema:
        cached_schema = read_schema_from_cache(name)
        return DataBase(name, cached_schema)
    else:
        return DataBase(name)


class DataBase:
    def __init__(self, name, cached_schema=None):
        self.db_name = name
        self.connection_string = get_connection_string(name)
        self.statement_history = []
        self.has_schema_info = bool(cached_schema)
        if self.has_schema_info:
            self._load_schema(cached_schema)

    def _load_schema(self, cached_schema):
        if hasattr(cached_schema[0], "schema_name"):
            for obj in cached_schema:
                setattr(self, obj.schema_name, obj)
                for tbl in obj.tables().values():
                    tbl.db_instance = self
        else:
            for obj in cached_schema:
                setattr(self, obj.table_name, obj)
                obj.db_instance = self

    def exec_query(self, statement, raw_result=False):
        conn = None
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
                rows_list = [builder._make(row) for row in odbc_rows]
        except Exception as error:
            print(error)
        finally:
            if conn is not None:
                conn.close()
            self.statement_history.append(statement)
            return rows_list

    def new_query(self):
        if self.has_schema_info:
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

    def table_finder(self, name, partial_name=True):
        if not self.has_schema_info:
            print("Schema information not available")
            return []
        tables = []
        if get_uses_schema(self.db_name):
            for s in (v for v in vars(self).values() if
                      hasattr(v, "schema_name")):
                tables.extend(s.tables().values())
        else:
            tables = [t for t in vars(self).values() if
                      hasattr(t, "table_name")]

        table_name = name.lower()
        if partial_name:
            return [tbl for tbl in tables
                    if table_name in tbl.table_name.lower()]
        else:
            return [tbl for tbl in tables
                    if table_name == tbl.table_name.lower()]
