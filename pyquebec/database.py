import pypyodbc
from collections import namedtuple
from .querybuilder import QueryBuilder
from .config import get_db_config


class DataBase:
    def __init__(self, name, cached_schema=None):
        self.db_name = name
        self.config = get_db_config(name)
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
            conn = pypyodbc.connect(self.config.connection)
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
        if self.config.uses_schema:
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

    def __str__(self):
        return "DataBase " + self.db_name

    def __repr__(self):
        return self.__str__()