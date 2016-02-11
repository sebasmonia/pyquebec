import os.path
import json
from .dbobjects import Schema, Table
from collections import namedtuple

_cache_folder = os.path.join(os.path.expanduser("~"), ".pyquebec")
_cachecolumn = namedtuple('cachecolumn', ['schema', 'table', 'name'])


def cache_schema(name, db_instance):
    engine_name = db_instance.config.engine
    schema_objects = _loaders.get(engine_name, _load_queries_only)(db_instance)
    _serialize_schema(name, schema_objects)


def _load_queries_only(db):
    queries = db.config.schema_queries
    schemas = db.exec_sql(queries['Schemas'])
    tables = db.exec_sql(queries['Tables'])
    all_columns = db.exec_sql(queries['Columns'])
    objects = {}
    objects['Schemas'] = [s.name for s in schemas]
    objects['Tables'] = [(t.schema, t.name) for t in tables]
    objects['Columns'] = [(c.schema, c.table, c.name) for c in all_columns]
    return objects


def _load_SQLite(db):
    objects = {}
    objects['Schemas'] = None
    queries = db.config.schema_queries
    tables = db.exec_sql(queries['Tables'])
    objects["Tables"] = [(None, t.name) for t in tables]
    objects["Columns"] = []
    for t in tables:
        cols = db.exec_sql("PRAGMA table_info(" + t.name + ")")
        c = [(None, t.name, c.name) for c in cols]
        objects["Columns"].extend(c)

    return objects


def _serialize_schema(name, objs):
    cache_path = os.path.join(_cache_folder, name + ".schema")
    with open(cache_path, "w+") as c:
        json.dump(objs, c, indent=4)


def read_schema_from_cache(name):
    cache_path = os.path.join(_cache_folder, name + ".schema")
    with open(cache_path) as c:
        cache = json.load(c)
    if cache['Schemas']:
        objects = _load_with_schema(cache)
    else:
        objects = _load_without_schema(cache)
    return objects


def _load_with_schema(cache):
    objs = [Schema(name) for name in cache['Schemas']]
    all_cols = [_cachecolumn._make(c) for c in cache['Columns']]
    for schema, table in cache['Tables']:
        schema_ref = [x for x in objs if x.schema_name == schema][0]
        cols = (col.name for col in all_cols if
                col.table == table and
                col.schema == schema)
        table_ref = Table(None, schema_ref, table, cols)
        setattr(schema_ref, table, table_ref)
    return objs


def _load_without_schema(cache):
    objs = []
    all_cols = [_cachecolumn._make(c) for c in cache['Columns']]
    for _, table in cache['Tables']:
        cols = (col.name for col in all_cols if
                col.table == table)
        table_ref = Table(None, None, table, cols)
        objs.append(table_ref)
    return objs


_loaders = {
    "MSSQL": _load_queries_only,
    "SQLite": _load_SQLite
}
