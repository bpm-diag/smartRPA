# ****************************** #
# Utils
# Global utils used by the modules, provides information about current OS, installed applications and folders
# ****************************** #
import csv
import errno
from getpass import getuser
from datetime import datetime
import os
import plistlib
import importlib
from threading import Thread
from platform import system
import utils.config
import utils.consumerServer
import pandas as pd
# asynchronous session.post requests to log server, used by multiple modules
from requests_futures.sessions import FuturesSession
session = FuturesSession()


# ************
# Constants
# ************


WINDOWS = (system() == "Windows")
MAC = (system() == "Darwin")
LINUX = (system() == "Linux")

if WINDOWS:
    import winreg
    from win32com.shell import shell, shellcon
    RECENT_ITEMS_PATH_WIN = shell.SHGetFolderPath(0, shellcon.CSIDL_RECENT, None, 0)
    # RECENT_ITEMS_PATH_WIN = os.path.join(HOME_FOLDER, "AppData\\Roaming\\Microsoft\\Windows\\Recent")

USER = getuser()
HOME_FOLDER = os.path.expanduser("~")
DESKTOP = os.path.join(HOME_FOLDER, "Desktop")
DOCUMENTS = os.path.join(HOME_FOLDER, "Documents")
DOWNLOADS = os.path.join(HOME_FOLDER, "Downloads")
MAIN_DIRECTORY = utils.config.MyConfig.get_instance().main_directory  # main file path


# ************
# Functions
# ************


# return current timestamp in the format '2020-02-12 17:11:14:465'
# used by multiple modules
def timestamp():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S:%f")[:-3]


# Create directory with the given path if it does not exist
def createDirectory(path):
    if not os.path.exists(path):
        try:
            os.makedirs(path)
            print(f"[UTILS] Created directory {path}")
        except OSError as exc:  # Guard against race condition
            print(f"[UTILS] Could not create directory {path}")
            if exc.errno != errno.EEXIST:
                raise


# used by main, creates new log file with the current timestamp in /logs directory at the root of the project.
def createLogFile():
    # filename to use in current session until the 'stop' button is pressed. must be set here because the filename
    # uses the current timestamp and it must remain the same during the whole session
    current_directory = utils.config.MyConfig.get_instance().main_directory
    logs = os.path.join(current_directory, 'logs')
    createDirectory(logs)
    filename = datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + '.csv'
    utils.config.MyConfig.get_instance().log_filepath = os.path.join(logs, filename)
    # create HEADER
    with open(utils.config.MyConfig.get_instance().log_filepath, 'a', newline='') as out_file:
        f = csv.writer(out_file)
        f.writerow(utils.consumerServer.HEADER)


# return filename of a given path without extension, like 2020-02-25_23-21-57
def getFilename(path):
    return os.path.splitext(os.path.basename(path))[0]


# return file extension of a given path like .csv
def getFileExtension(path):
    return os.path.splitext(os.path.basename(path))[1]


# return current chrome version, used to detect selenium driver
def getChromeVersionMac():
    if os.path.exists("/Applications/Google Chrome.app"):
        plistloc = "/Applications/Google Chrome.app/Contents/Info.plist"
        pl = plistlib.readPlist(plistloc)
        pver = pl["CFBundleShortVersionString"]
        return pver
    else:
        return None


def combineMultipleCsv(list_of_csv_to_combine, combined_csv_path):
    # make sure that given csv to combine actually exist in system
    existing_csv_to_combine = [p for p in list_of_csv_to_combine if os.path.exists(p)]
    try:
        # combine all files in the list
        combined_csv = pd.concat([pd.read_csv(f) for f in existing_csv_to_combine])
        # export to csv
        combined_csv.to_csv(combined_csv_path, index=False, encoding='utf-8-sig')
        print(f"[UTILS] Multiple csv combined in {combined_csv_path}")
        return True
    except (pd.errors.ParserError, FileNotFoundError) as e:
        print(e)
        return False

# return python module install location
def getPythonModuleLocation(module_name):
    module = importlib.util.find_spec(module_name)
    if module:
        return module.submodule_search_locations[0]


# return chromedriver path from automagica module used by selenium
def getChromedriverPath():
    automagica_path = utils.utils.getPythonModuleLocation('automagica')
    chromedriver_relative = ""
    if WINDOWS:
        chromedriver_relative = "bin/win32/chromedriver.exe"
    elif MAC:
        chromedriver_relative = "bin/mac64/chromedriver"
    elif LINUX:
        chromedriver_relative = "bin/linux64/chromedriver"
    chromedriver = os.path.join(automagica_path, chromedriver_relative)
    # if MAC: os.chmod(chromedriver, 755)
    return chromedriver


# ************
# Class
# ************


class ThreadWithReturnValue(Thread):
    def __init__(self, group=None, target=None, name=None,
                 args=(), kwargs={}, Verbose=None):
        Thread.__init__(self, group, target, name, args, kwargs)
        self._kwargs = kwargs
        self._args = args
        self._target = target
        self._return = None

    def run(self):
        if self._target is not None:
            self._return = self._target(*self._args,
                                        **self._kwargs)

    def join(self, *args):
        Thread.join(self, *args)
        return self._return


# ************
# Detect installed programs
# ************


# detect if program (both 32bit and 64bit) is installed checking windows registry
def isInstalledWin(programName):
    def _getInstalledProgramsWin(hive, flag):
        registry = winreg.ConnectRegistry(None, hive)
        registry_key = winreg.OpenKey(registry, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall", 0,
                                      winreg.KEY_READ | flag)
        registry_subkeys_number = winreg.QueryInfoKey(registry_key)[0]
        software_list = []
        for i in range(registry_subkeys_number):
            try:
                asubkey_name = winreg.EnumKey(registry_key, i)
                subkey = winreg.OpenKey(registry_key, asubkey_name)
                software_name = winreg.QueryValueEx(subkey, "DisplayName")[0]
                software_list.append(software_name)
            except EnvironmentError:
                continue
        return software_list

    software_list = _getInstalledProgramsWin(winreg.HKEY_LOCAL_MACHINE, winreg.KEY_WOW64_32KEY) + \
                    _getInstalledProgramsWin(winreg.HKEY_LOCAL_MACHINE, winreg.KEY_WOW64_64KEY) + \
                    _getInstalledProgramsWin(winreg.HKEY_CURRENT_USER, 0)

    return bool(list(filter(lambda program: programName in program.lower(), software_list)))


# detect if program is installed in /Applications folder
def isInstalledMac(programName):
    output = os.popen("ls -1 /Applications").read().split('\n')
    return bool(list(filter(lambda program: programName in program.lower(), output)))


# needs testing
def isInstalledLinux(programName):
    return os.subprocess.call(f"dpkg -s {programName} > /dev/null 2>&1", shell=True) == 0


# set boolean variables for available programs, used by GUI to enable/disable checkboxes
if WINDOWS:
    OFFICE = isInstalledWin('office')
    CHROME = isInstalledWin('chrome')
    FIREFOX = isInstalledWin('firefox')
    EDGE = isInstalledWin('edge')
    OPERA = isInstalledWin('opera')
elif MAC:
    OFFICE = isInstalledMac('excel')  # on MacOS only excel events can be logged through an addin
    CHROME = isInstalledMac('chrome')
    FIREFOX = isInstalledMac('firefox')
    EDGE = isInstalledMac('edge')
    OPERA = isInstalledMac('opera')
else:
    OFFICE = False
    CHROME = isInstalledLinux('chrome')
    FIREFOX = isInstalledLinux('firefox')
    EDGE = False
    OPERA = isInstalledLinux('opera')
