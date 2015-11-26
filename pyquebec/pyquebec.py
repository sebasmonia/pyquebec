from .database import DataBase
from .config import create_config_db, get_connection_string, get_uses_schema
from .schema_reader import cache_schema, read_schema_from_cache

def add(name, connection_string, engine):
    create_config_db(name, connection_string, engine)
    return refresh_cache(name)

def open(name, load_schema=True):
    if load_schema:
        cached_schema = read_schema_from_cache(name)
        return DataBase(name, cached_schema)
    else:
        return DataBase(name)

def refresh_cache(name):
    db_instance = DataBase(name, None)
    cache_schema(name, db_instance)
    return connect(name)

def list_names():
    pass