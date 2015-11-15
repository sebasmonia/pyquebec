import os.path

_cache_folder = os.path.join(os.path.expanduser("~"), ".pyquebec")


def cache_schema(name, connection_string, engine):
    db = DataBase(connection_name, false)


def _load_MSSQL():
    pass


def _load_SQLite():
    pass
    

_loaders = {
    "MSSQL": _load_MSSQL, 
    "SQLite" : _load_SQLite
}