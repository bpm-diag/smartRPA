# ******************************
# Fix automagica permissions script
# Must be executed only the first time, used to set correct permissions
# ******************************

import subprocess
import sys, os
from platform import system
from importlib import util

try:
    from automagica import *
except ImportError as e:
    print("[SETUP] Please install 'automagica' module running 'pip3 install -U automagica' and run this script again.")
    print("[SETUP] If you get 'openssl' error check here https://github.com/bpm-diag/smartRPA#automagica")
    sys.exit()


# return python module install location
def getPythonModuleLocation(module_name):
    import importlib
    module = importlib.util.find_spec(module_name)
    if module:
        return module.submodule_search_locations[0]


# automagica post install
if __name__ == '__main__':
    if system() == "Windows":
        print("[SETUP] You're ready!")
    else:
        automagica_path = getPythonModuleLocation('automagica')
        print(f"[SETUP] automagica module is installed in: {automagica_path} ")

        # Make binaries executable
        print("[SETUP] Setting chromedriver permissions")
        binaries_path = os.path.join(automagica_path, "bin")
        subprocess.call(["chmod", "-R", "+x", binaries_path])

        # Make lab-folder writeable (required by Jupyter Notebook)
        print("[SETUP] Setting lab-folder permissions")
        lab_path = os.path.join(automagica_path, "lab")
        subprocess.call(["chmod", "-R", "777", lab_path])

        # check if binaries are now executable
        if os.access(binaries_path, os.X_OK):
            print("[SETUP] You're ready!")
        else:
            print(
                f"[SETUP] Something went wrong when setting executable permissions, try to set the manually executing 'chmod -R +x {binaries_path}' ")
