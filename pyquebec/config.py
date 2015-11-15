import configparser
import os.path

_config_folder = os.path.join(os.path.expanduser("~"), ".pyquebec")
_config_file = os.path.join(_config_folder, "pyquebec.ini")
_config = configparser.ConfigParser()
_config.optionxform = str
_config.read(_config_file)

_db_sections = ('QueryTemplates', 'QueryOptions', 'SchemaQueries')

def get_config_section(section_name):
    return _config[section_name]


def _validate_config(engine):
    required = tuple("_".join((engine, s)) for s in _db_sections)
    all_sections = _config.sections()
    if not all(r in all_sections  for r in required):
        raise ValueError("Configuration incomplete for" + engine)


def create_config_db(name, connection_string, engine):
    _validate_config(engine)
    new_path = os.path.join(_config_folder, name + ".ini")
    new_cfg = configparser.ConfigParser()
    new_cfg.add_section("Connection")
    new_cfg["Connection"]["ConnectionString"]=connection_string
    for s in  _db_sections:
        new_cfg.add_section(s)
        new_cfg[s] = _config[engine + "_" + s]
    with open(new_path, "w+") as f:
        new_cfg.write(f)


def get_connections():
    return _config['Connections'].items()


def get_REPL():
    return _config['REPL_Queries']
