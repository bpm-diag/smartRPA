# ******************************
# Setup script
# Must be executed only the first time, used to set correct permissions
# ******************************

import utils
from utils.utils import WINDOWS
import subprocess
import sys, os

try:
    from automagica import *
except ImportError as e:
    print("[SETUP] Please install 'automagica' module running 'pip3 install -U automagica' and run this script again.")
    print("[SETUP] If you get 'openssl' error check here https://github.com/marco2012/ComputerLogger#RPA")
    sys.exit()


# automagica post install
if __name__ == '__main__':
    if WINDOWS:
        print("[SETUP] You're ready!")
    else:
        automagica_path = utils.utils.getPythonModuleLocation('automagica')
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
            print(f"[SETUP] Something went wrong when setting executable permissions, try to set the manually executing 'chmod -R +x {binaries_path}' ")
