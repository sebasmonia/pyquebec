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


def get_db_config(name):
    ini_file = os.path.join(_config_folder, name + ".ini")
    if not os.path.isfile(ini_file):
        print("Database", name, "has no configuration file.", end=" ")
        print("If it's a new DB, use add_database() to configure it.")
        raise ValueError("Invalid database names")
    cfg = configparser.ConfigParser()
    cfg.optionxform = str
    cfg.read(ini_file)
    return ini_file, cfg

def get_db_engine(name):
    ini_file = os.path.join(_config_folder, name + ".ini")
    cfg = configparser.ConfigParser()
    cfg.read(ini_file)
    return cfg["Configuration"]["Engine_Name"]

def get_queries(name):
    ini_file = os.path.join(_config_folder, name + ".ini")
    cfg = configparser.ConfigParser()
    cfg.read(ini_file)
    return cfg["SchemaQueries"]


def create_config_db(name, connection_string, engine):
    new_cfg_path = _copy_template(name, engine)
    new_cfg = configparser.ConfigParser()
    new_cfg.optionxform = str
    new_cfg.read(new_path)
    new_cfg.add_section("Connection")
    new_cfg["Connection"]["ConnectionString"] = connection_string
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


def get_connections():
    return _config['Connections'].items()


def get_REPL():
    return _config['REPL_Queries']
