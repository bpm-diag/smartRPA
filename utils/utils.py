# ****************************** #
# Utils
# Global utils used by the modules, provides information about current OS, installed applications and folders
# ****************************** #
import csv
import errno
from concurrent.futures.thread import ThreadPoolExecutor
from getpass import getuser
from datetime import datetime
import os
import subprocess
import plistlib
import importlib
from importlib import util
from threading import Thread
from platform import system
from urllib.parse import urlparse
import utils.config
import utils.consumerServer
import unicodedata
import pandas
from unidecode import unidecode
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
    import win32gui

    RECENT_ITEMS_PATH_WIN = shell.SHGetFolderPath(0, shellcon.CSIDL_RECENT, None, 0)
    # RECENT_ITEMS_PATH_WIN = os.path.join(HOME_FOLDER, "AppData\\Roaming\\Microsoft\\Windows\\Recent")

# return shortcut lnk full path
# def shortcut_target(filename):
#     pythoncom.CoInitialize()
#     link = pythoncom.CoCreateInstance(
#         shell.CLSID_ShellLink,
#         None,
#         pythoncom.CLSCTX_INPROC_SERVER,
#         shell.IID_IShellLink
#     )
#     link.QueryInterface(pythoncom.IID_IPersistFile).Load(filename)
#     name, _ = link.GetPath(shell.SLGP_UNCPRIORITY)
#     return name


USER = getuser()
HOME_FOLDER = os.path.expanduser("~")
DESKTOP = os.path.join(HOME_FOLDER, "Desktop")
DOCUMENTS = os.path.join(HOME_FOLDER, "Documents")
DOWNLOADS = os.path.join(HOME_FOLDER, "Downloads")
MAIN_DIRECTORY = os.getcwd()  # main file path


# ************
# Functions
# ************


# return current timestamp in the format '2020-02-12 17:11:14:465'
# used by multiple modules
def timestamp():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S:%f")  # [:-3]


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

    # current_directory = utils.config.MyConfig.get_instance().main_directory
    # if current_directory is None: current_directory = os.getcwd()
    # logs = os.path.join(current_directory, 'logs')
    logs = os.path.join(MAIN_DIRECTORY, 'logs')
    createDirectory(logs)
    filename = datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + '.csv'
    log_filepath = os.path.join(logs, filename)
    # utils.config.MyConfig.get_instance().log_filepath = log_filepath
    # create HEADER
    with open(log_filepath, 'a', newline='', encoding='utf-8-sig') as out_file:
        f = csv.writer(out_file)
        f.writerow(utils.consumerServer.HEADER)
    return log_filepath


# RPA_directory is like /Users/marco/Desktop/ComputerLogger/RPA/2020-02-25_23-21-57
def getRPADirectory(csv_file_path):
    csv_filename = getFilename(csv_file_path)
    try:
        RPA_directory = os.path.join(MAIN_DIRECTORY, 'RPA', csv_filename)
    except Exception as e:
        print(e)
        print(f"[UTILS] Could not create RPA directory, saving RPA script on Desktop")
        RPA_directory = os.path.join(DESKTOP, 'RPA', csv_filename)
    return RPA_directory.strip('_combined')


# return filename of a given path without extension, like 2020-02-25_23-21-57
def getFilename(path):
    return os.path.splitext(os.path.basename(path))[0]


def removeWhitespaces(string):
    return " ".join(string.split())


def processClipboard(cb, remove_whitespaces=False):
    try:
        clipboard = unicodeString(cb.strip('"'))
        if remove_whitespaces:
            clipboard = removeWhitespaces(clipboard)
        return clipboard
    except Exception:
        return cb


def unicodeString(string):
    try:
        return unidecode(string
                         .replace("à", "a'")
                         .replace("è", "e'")
                         .replace("ì", "i'")
                         .replace("ò", "o'")
                         .replace("ù", "u'")
                         )
    except Exception:
        return string


# check if port is available to start server
def isPortInUse(port):
    import socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('127.0.0.1', port)) == 0


def CSVEmpty(log_filepath, min_len=1):
    try:
        df = pandas.read_csv(log_filepath, encoding='utf-8-sig')
    except pandas.errors.EmptyDataError:
        return True
    return df.empty or len(df) <= min_len


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
        combined_csv = pandas.concat([pandas.read_csv(f, encoding="latin") for f in existing_csv_to_combine])
        # export to csv
        combined_csv.to_csv(combined_csv_path, index=False, encoding='utf-8-sig')
        print(f"[UTILS] {combined_csv_path} created by merging {existing_csv_to_combine}")
        return True
    except (pandas.errors.ParserError, FileNotFoundError) as e:
        print(e)
        return False


def getActiveWindowInfo(parameter):
    try:
        hwnd = win32gui.GetForegroundWindow()
        name = win32gui.GetWindowText(hwnd)
        x0, y0, x1, y1 = win32gui.GetWindowRect(hwnd)
        if parameter == "name":
            return name
        elif parameter == "size":
            return x0, y0, x1, y1
    except Exception:
        pass


def getActiveWindowName():
    try:
        hwnd = win32gui.GetForegroundWindow()
        name = win32gui.GetWindowText(hwnd)
        return name
    except Exception:
        pass


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


def getHostname(url):
    return urlparse(url).hostname if url else url


def toAscii(string):
    return unicodedata.normalize('NFD', string).encode('ascii', 'ignore')


# format a given path for current OS
def formatPathForCurrentOS(path, username_on_source_os):
    if path:
        is_windows_path = '\\' in path[:10]
        if MAC:
            if is_windows_path:
                return path.replace('\\', '/').replace(f"C:/Users/{username_on_source_os}", f"/Users/{USER}")
            else:
                return path
        elif WINDOWS:
            if is_windows_path:
                return path
            else:
                return path.replace(f"/Users/{username_on_source_os}", f"C:/Users/{USER}").replace('/', '\\')
    else:
        return ""

def open_file(path):
    try:
        if WINDOWS:
            os.startfile(path)
        else:
            opener = "open" if MAC else "xdg-open"
            subprocess.call([opener, path])
    except Exception as e:
        print(f"[UTILS] Could not open file {path}: {e}")


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
