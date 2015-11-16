import configparser
import os.path
import shutil

_config_folder = os.path.join(os.path.expanduser("~"), ".pyquebec")
_config_file = os.path.join(_config_folder, "pyquebec.ini")
_config = configparser.ConfigParser()
_config.optionxform = str
_config.read(_config_file)


def get_config_section(section_name):
    return _config[section_name]


def _open_db_config(name):
    ini_file = os.path.join(_config_folder, name + ".ini")
    cfg = configparser.ConfigParser()
    cfg.optionxform = str
    cfg.read(ini_file)
    return cfg


def get_connection_string(name):
    return _open_db_config(name)["Connection"]["Connection_String"]


def get_db_engine(name):
    return _open_db_config(name)["Configuration"]["Engine_Name"]


def get_uses_schema(name):
    value = _open_db_config(name)["Configuration"]["Uses_Schema"]
    return (value == 'True')

def get_schema_queries(name):
    return _open_db_config(name)["SchemaQueries"]


def get_query_templates(name):
    return _open_db_config(name)["QueryTemplates"]


def create_config_db(name, connection_string, engine):
    new_cfg_path = _copy_template(name, engine)
    new_cfg = _open_db_config(name)
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
