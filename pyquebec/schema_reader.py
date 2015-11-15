import os.path
import json
#from .config import get_db_engine, get_queries, update_cache_location


_cache_folder = os.path.join(os.path.expanduser("~"), ".pyquebec")


def cache_schema(name):
    cfg = get_db_config(name)
    engine = cfg["Configuration"][""]
    db = DataBase(connection_name, false)
    schema_objects = _loaders[engine](db, queries)
    

def _load_MSSQL(db, queries):
    queries = get_queries()
    schemas = db.exec_query(queries['Schemas'])
    tables = db.exec_query(queries['Tables'])
    all_columns = db.exec_query(queries['Columns'])
    objects = {}
    objects['Schemas'] = [s.name for s in schemas]
    objects['Tables'] = [(t.schema, t.name) for t in tables]
    objects['Columns'] = [(c.schema, c.table, c.name) for c in columns]
    return objects

def _load_SQLite(db):
    objects = {}
    objects['Schemas'] = None
    queries = get_queries(db.db_name)
    tables = db.exec_query(queries['Tables'])
    objects["Tables"] = [(None, t.name) for t in tables]
    objects["Columns"] = []
    for t in tables:
        cols = db.exec_query("PRAGMA table_info(" + t.name + ")")
        c = [(None, t.name, c.name) for c in cols]
        objects["Columns"].extend(c)

    return objects


def _serialize_schema(name, objs):
    cache_path = os.path.join(_cache_folder, name + ".cache")
    with open(cache_path, "w+") as c:
        json.dump(objs, c, indent=4)

def _read_schema_from_cache(name):
    cache_path = os.path.join(_cache_folder, name + ".cache")
    with open(cache_path) as c:
        return json.load(c)


_loaders = {
    "MSSQL": _load_MSSQL, 
    "SQLite" : _load_SQLite
}