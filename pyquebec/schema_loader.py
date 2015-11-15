import os.path

_cache_folder = os.path.join(os.path.expanduser("~"), ".pyquebec")


def cache_schema():
    return DataBase(connection_name, load_schema)