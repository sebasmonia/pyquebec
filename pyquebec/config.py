from collections import namedtuple
import configparser
import os.path
import shutil

_config_folder = os.path.join(os.path.expanduser("~"), ".pyquebec")
_config_file = os.path.join(_config_folder, "pyquebec.ini")
_config = configparser.ConfigParser()
_config.optionxform = str
_config.read(_config_file)

dbconfig = namedtuple("dbconfig", ['connection', 'engine', 'uses_schema',
                                   'schema_queries', 'query_templates'])

def get_config_section(section_name):
    return _config[section_name]

def get_db_config(name):
    ini_path = os.path.join(_config_folder, name + ".ini")
    ini = configparser.ConfigParser()
    ini.optionxform = str
    ini.read(ini_path)
    conn = ini["Connection"]["Connection_String"]
    engine = ini["Configuration"]["Engine_Name"]
    uses_schema = (ini["Configuration"]["Uses_Schema"] == 'True')
    schema_queries = ini["SchemaQueries"]
    query_templates = ini["QueryTemplates"]
    cfg = dbconfig(conn, engine, uses_schema, schema_queries, query_templates)
    return cfg


def create_config_db(name, connection_string, engine):
    new_cfg_path = _copy_template(name, engine)
    ini_file = os.path.join(_config_folder, name + ".ini")
    new_cfg = configparser.ConfigParser()
    new_cfg.optionxform = str
    new_cfg.read(ini_file)
    new_cfg.add_section("Connection")
    new_cfg["Connection"]["Connection_String"] = connection_string
    with open(new_cfg_path, "w+") as f:
        new_cfg.write(f)
    return new_cfg_path


def _copy_template(name, engine):
    module_install_dir = os.path.split(__file__)[0]
    template_name = engine + ".ini"
    original = os.path.join(module_install_dir, 'templates', template_name)
    destination = os.path.join(_config_folder, name + ".ini")
    shutil.copy(original, destination)
    return destination
