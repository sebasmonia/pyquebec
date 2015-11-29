import os
import shutil

_config_folder = os.path.join(os.path.expanduser("~"), ".pyquebec")
if not os.path.isdir(_config_folder):
    os.mkdir(_config_folder)
    fname = "pyquebec.ini"
    module_install_dir = os.path.split(__file__)[0]
    ini_file = os.path.join(module_install_dir, fname)
    destination = os.path.join(_config_folder, fname)
    shutil.copy(ini_file, destination)

# define default / minimum config
