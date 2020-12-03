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
import modules.consumerServer
import unicodedata
import pandas
from unidecode import unidecode
from itertools import tee, islice, chain
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
EVENT_LOG_FOLDER = "event_log"
PROCESS_DISCOVERY_FOLDER = "process_discovery"
SW_ROBOT_FOLDER = "SW_Robot"
UIPATH_FOLDER = "UiPath"

# ************
# Functions
# ************


def timestamp():
    """
    Generate current timestamp in ISO format (e.g. '2020-08-29T16:42:30.690')

    :return: timestamp in ISO format
    """

    #return datetime.now().strftime("%Y-%m-%d %H:%M:%S:%f")  # [:-3]
    return datetime.now().isoformat(timespec='milliseconds')


def createDirectory(path):
    """
    Create directory with the given path if it does not exist

    :param path: path of directory to be created
    """
    if not os.path.exists(path):
        try:
            os.makedirs(path)
            print(f"[UTILS] Created directory {path}")
        except OSError as exc:  # Guard against race condition
            print(f"[UTILS] Could not create directory {path}")
            if exc.errno != errno.EEXIST:
                raise


def createLogFile():
    """
    Creates new log file with the current timestamp in /logs directory at the root of the project. used by main.

    :return: path of created log
    """
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
        f.writerow(modules.consumerServer.HEADER)
    return log_filepath


def getRPADirectory(csv_file_path):
    """
    Genreate path to save RPA files.

    RPA_directory is like /Users/marco/Desktop/ComputerLogger/RPA/2020-02-25_23-21-57

    :param csv_file_path: path of event log in input
    :return: path of RPA directory
    """
    csv_filename = getFilename(csv_file_path)
    try:
        RPA_directory = os.path.join(MAIN_DIRECTORY, 'RPA', csv_filename)
    except Exception as e:
        print(e)
        print(f"[UTILS] Could not create RPA directory, saving RPA script on Desktop")
        RPA_directory = os.path.join(DESKTOP, 'RPA', csv_filename)
    return RPA_directory.strip('_combined')


def getFilename(path):
    """
    return filename of a given path without extension, like 2020-02-25_23-21-57


    :param path: path of event log
    :return: filename without extension
    """
    return os.path.splitext(os.path.basename(path))[0]


def removeWhitespaces(string):
    """
    remove spaces before and after words in a string

    :param string: input string
    :return: string without whitespaces
    """
    return " ".join(string.split())


def processClipboard(cb, remove_whitespaces=False):
    """
    convert clipboard text to unicode and remove whitespaces

    :param cb: clipboard text
    :param remove_whitespaces: boolean, if true remove whitespaces
    :return: unicode version of clipboard text
    """
    try:
        clipboard = unicodeString(cb.strip('"'))
        if remove_whitespaces:
            clipboard = removeWhitespaces(clipboard)
        return clipboard
    except Exception:
        return cb


def unicodeString(string):
    """
    Replace special accented characters with unicode version

    :param string: string to be replaced
    :return: unicode version of string with replaced accented characters
    """
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


def isPortInUse(port):
    """
    check if port is available to start server

    :param port: port number
    :return: true if given port is in use by another process
    """
    import socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('127.0.0.1', port)) == 0


def CSVEmpty(log_filepath, min_len=1):
    """
    Check if given csv is empty by counting number of rows

    :param log_filepath: csv path
    :param min_len: minimum number of rows after which csv is not considered empty
    :return: true if csv is empty
    """
    try:
        df = pandas.read_csv(log_filepath, encoding='utf-8-sig')
    except pandas.errors.EmptyDataError:
        return True
    return df.empty or len(df) <= min_len


def getFileExtension(path):
    """
    return file extension of a given path like .csv

    :param path: input path
    :return: file extension of given path (e.g. .csv)
    """
    return os.path.splitext(os.path.basename(path))[1]


def getChromeVersionMac():
    """
    return current chrome version, used to detect selenium driver

    :return: current chrome version
    """
    if os.path.exists("/Applications/Google Chrome.app"):
        plistloc = "/Applications/Google Chrome.app/Contents/Info.plist"
        pl = plistlib.readPlist(plistloc)
        pver = pl["CFBundleShortVersionString"]
        return pver
    else:
        return None


def combineMultipleCsv(list_of_csv_to_combine, combined_csv_path):
    """
    Combine multiple csv in a single file

    :param list_of_csv_to_combine: list of csv paths
    :param combined_csv_path: path where to save combined csv
    """
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
    """
    Get name and size of active window in foreground (windows only)

    :param parameter: either 'name' or 'size'
    :return: name or size of active window
    """
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
    """
    Get name of window in foreground (windows only)

    :return: name of window in foreground
    """
    try:
        hwnd = win32gui.GetForegroundWindow()
        name = win32gui.GetWindowText(hwnd)
        return name
    except Exception:
        pass


def getPythonModuleLocation(module_name):
    """
    return python module install location

    :param module_name: name of module to find
    :return: install location
    """
    module = importlib.util.find_spec(module_name)
    if module:
        return module.submodule_search_locations[0]


def getChromedriverPath():
    """
    return chromedriver path from automagica module used by selenium

    :return: hromedriver pat
    """
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
    """
    Get hostname from url

    :param url: url
    :return: hostname of url
    """
    return urlparse(url).hostname if url else url


def toAscii(string):
    """
    convert input string to ascii characters

    :param string: input string
    :return: input string with ascii characters
    """
    return unicodedata.normalize('NFD', string).encode('ascii', 'ignore')


def formatPathForCurrentOS(path, username_on_source_os):
    """
    format a given path for current OS

    :param path: input path
    :param username_on_source_os: username of user on source operating system
    :return: path with username of user of destination operating system
    """
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


def convertToWindowsPath(path, username_on_source_os):
    """
    convert path to windows path with trailing slashes

    :param path: input path
    :param username_on_source_os: username of user on source operating system
    :return: path formatted for windows
    """
    if path != "":
        if '\\' in path[:10]:  # already windows path
            return path
        else:
            return path.replace(f"/Users/{username_on_source_os}", f"C:/Users/{USER}").replace('/', '\\')
    else:
        return ""


def open_file(path):
    """
    open input file

    :param path: path of file to be opened
    """
    try:
        if WINDOWS:
            os.startfile(path)
        else:
            opener = "open" if MAC else "xdg-open"
            subprocess.call([opener, path])
    except Exception as e:
        print(f"[UTILS] Could not open file {path}: {e}")


def fixTimestampFieldXES(xes_filepath):
    import fileinput
    with fileinput.FileInput(xes_filepath, inplace=True) as file:
        for line in file:
            print(line.replace('<string key="time:timestamp"', '<date key="time:timestamp"'), end='')


# loop accessing the previous, current, and next items https://stackoverflow.com/a/1012089/1440037
def previous_and_next(some_iterable):
    prevs, items, nexts = tee(some_iterable, 3)
    prevs = chain([None], prevs)
    nexts = chain(islice(nexts, 1, None), [None])
    return zip(prevs, items, nexts)


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


def isInstalledWin(programName):
    """
    detect if program (both 32bit and 64bit) is installed checking windows registry

    :param programName: name of program to be checked
    :return: true if program is installed, else false
    """
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


def isInstalledMac(programName):
    """
    detect if program is installed in /Applications folder on mac

    :param programName: name of program to be checked
    :return: true if program is present in /Applications folder, else false
    """
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
