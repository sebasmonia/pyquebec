from .database import DataBase
from .config import create_config_db as _create_config_db
from .config import list_dbs as _list_dbs
from .schema_reader import cache_schema as _cache_schema
from .schema_reader import read_schema_from_cache as _read_schema_from_cache


def add(name, connection_string, engine='default'):
    _create_config_db(name, connection_string, engine)
    return refresh_cache(name)


def open(name, load_schema=True):
    if load_schema:
        cached_schema = _read_schema_from_cache(name)
        return DataBase(name, cached_schema)
    else:
        return DataBase(name)


def refresh_cache(name):
    db_instance = DataBase(name, None)
    _cache_schema(name, db_instance)
    return open(name)


def database_list():
    return _list_dbs()

