import os
import shutil

_config_folder = os.path.join(os.path.expanduser("~"), ".pyquebec")
if not os.path.isdir(_config_folder):
    module_install_dir = os.path.split(__file__)[0]
    initial_config = os.path.join(module_install_dir, "initial_config")
    shutil.copytree(initial_config, _config_folder)

# define default / minimum config
