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
# import utils.config
import modules.consumerServer
import unicodedata
import pandas as pd
from unidecode import unidecode
from itertools import tee, islice, chain
# asynchronous session.post requests to log server, used by multiple modules
from requests_futures.sessions import FuturesSession

# screenshot recording feature for single screen
from PIL import Image
import os
import hashlib
from datetime import datetime
from screeninfo import get_monitors
import utils.config

# screenshot recording feature for multiple screen
from PIL import ImageGrab

# Data Validation
import re
import validators

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

if not MAC:
    import dxcam

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

# Global variable for camera on taking screenshots
camera = None

# ************
# Functions
# ************


def timestamp(format=None):
    """
    Generate current timestamp in ISO format (e.g. '2020-08-29T16:42:30.690')

    :param format: format (Default None) specifies the datetime format, if none it is ISO Format

    :return: timestamp in (ISO) format
    """
    if format == None:
        return datetime.now().isoformat(timespec='milliseconds')
    else:
        return datetime.now().strftime(format)


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

    filename = timestamp("%Y-%m-%d_%H-%M-%S") + '.csv'

    
    # If config capture_screenshots = True, we create a screenshot and screenshots sub folder
    screenshots_dir = os.path.join(MAIN_DIRECTORY, 'screenshots')
    createDirectory(screenshots_dir)
    subdirectory = os.path.splitext(filename)[0]
    # Added to store screenshot files in the same named folder
    # if config capture_screenshots = TRUE create a dir, otherwise do not:
    screenshots_subdir = os.path.join(screenshots_dir, subdirectory)
    createDirectory(screenshots_subdir)

    log_filepath = os.path.join(logs, filename)
    # utils.config.MyConfig.get_instance().log_filepath = log_filepath
    # create HEADER
    with open(log_filepath, 'a', newline='', encoding='utf-8-sig') as out_file:
        f = csv.writer(out_file)
        f.writerow(modules.consumerServer.HEADER)
    return log_filepath, screenshots_subdir

def getRPADirectory(csv_file_path):
    """
    Genreate path to save RPA files.

    RPA_directory is like /Users/marco/Desktop/ComputerLogger/RPA/2020-02-25_23-21-57

    :param csv_file_path str: path of event log in input
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


def CSVEmpty(log_filepath, min_len=0):
    """
    Check if given csv is empty by counting number of rows

    :param log_filepath: csv path
    :param min_len: minimum number of rows after which csv is not considered empty
    :return: true if csv is empty
    """
    try:
        df = pd.read_csv(log_filepath, encoding='utf-8-sig')
    except pd.errors.EmptyDataError:
        return True
    print(len(df))
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
        combined_csv = pd.concat([pd.read_csv(f, encoding="latin") for f in existing_csv_to_combine])
        # export to csv
        combined_csv.to_csv(combined_csv_path, index=False, encoding='utf-8-sig')
        print(f"[UTILS] {combined_csv_path} created by merging {existing_csv_to_combine}")
        return True
    except (pd.errors.ParserError, FileNotFoundError) as e:
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
    automagica_path = getPythonModuleLocation('automagica')
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

# Methods copied from https://github.com/RPA-US/screen-action-logger
def get_last_directory_name(path):
    """
    Returns the name of the last directory within a given directory path.
    """
    directories = [d for d in os.listdir(path) if os.path.isdir(os.path.join(path, d))]
    if directories:
        last_directory = max(directories, key=lambda d: os.path.getmtime(os.path.join(path, d)))
        return os.path.basename(last_directory)
    else:
        return None

def get_last_directory_name(path):
    """
    Returns the name of the last directory within a given directory path.

    :param path: Path to the parent folder
    :return: "Newest" directory file name
    :rtype: String
    """
    directories = [d for d in os.listdir(path) if os.path.isdir(os.path.join(path, d))]
    if directories:
        last_directory = max(directories, key=lambda d: os.path.getmtime(os.path.join(path, d)))
        return os.path.basename(last_directory)
    else:
        return None

def calculateImageHash(img):
    # Calculamos el hash de la imagen
    sha256_hash = hashlib.sha256()
    sha256_hash.update(img)
    return sha256_hash.hexdigest()

def takeScreenshot(save_image: bool = utils.config.read_config("capture_screenshots",bool), scrshtFormat: str ="png"):
    """
    Takes a screenshot and saves it to a directory with a filename based on its hash, current date/time and order of capture.

    :param scrshtFormat: (Optional) File format of screenshot, Default type is png
    :param save_image: (Boolean) Default True
    :return: Name of the screenshot file
    """
    # Future improvement: use onlx dxcam to capture multiple screens, because it is faster
    filename = ""
    if save_image:
        directory = os.path.join("screenshots", get_last_directory_name("screenshots"))
        if not os.path.exists(directory):
            os.makedirs(directory)

        if not MAC and len(get_monitors()) == 1:
            global camera  # usa la variable global camera

            # Si no hay instancia de cámara, crear una nueva instancia
            if camera is None:
                camera = dxcam.create()
                print("Creating new camera instance")
            img = camera.grab()

            # Acortar el hash para el nombre
            short_hash = calculateImageHash(img)

            # Guardar la imagen en el directorio correspondiente. Nombre dependiente de hash
            # directory = "screenshots/"
            if not os.path.exists(directory):
                createDirectory(directory)
            stamp = timestamp("%Y-%m-%d_%H-%M-%S")
            # counter = len([filename for filename in os.listdir(directory) if filename.endswith('.png')])
            filename = os.path.join(directory, f"{short_hash}_{stamp}." + scrshtFormat)
            
            # Guarda la imagen y elimina compresión
            Image.fromarray(img).save(filename, compress_level=0)

        else:
            # If there are more than two screens attached it is easier to use the pillow impage capture
            screenshot = ImageGrab.grab(all_screens=True)
            # Have to use tobytes as the PIL image cannot be hashed using sha256_hash method
            short_hash = calculateImageHash(screenshot.tobytes())
            stamp = timestamp("%Y-%m-%d_%H-%M-%S")
            filename = os.path.join(directory, f"{short_hash}_{stamp}." + scrshtFormat)
            screenshot.save(filename, format=scrshtFormat)

    return filename

def add_json_element(node, key, value):
    """
    Adds a JSON element to the specified node.

    Args:
        node (dict): The node to add the element to.
        key (str): The key of the element.
        value (any): The value of the element.
    """

    if isinstance(node, dict):
        node[key] = value
    else:
        raise TypeError("Node must be a dictionary")

def concatIntoNoiseDf(noiseDf: pd.DataFrame, value: str, colName: str, rowId: int) -> pd.DataFrame:
    """
    Takes as input a df and a col/row/value combination and addes the row to the noiseDf

    :param noiseDf: Dataframe with Cols Value, Column Name, and Row ID
    :param value: value of the cell that is noise
    :param colName: Column name of the noisy cell
    :param rowId: Row ID of the noisy cell
    :return: noiseDf with the added row 
    """
    errorDf = pd.DataFrame([[value,colName,rowId]], columns=["Value","Column Name","Row ID"])
    return pd.concat([noiseDf,errorDf], ignore_index=True)

# Needs Testing
def staticNoiseIdentification(uilog: pd.DataFrame) -> pd.DataFrame:
    """
    Gets a UI log and identifies all cells containing static noise
    Static noise is noise that is identified using attributes default formats
    
    :param uilog: User interaction log dataframe
    :return: Dataframe with value, col, row that are considered noise
    """
    noiseDf = pd.DataFrame(columns=["Value","Column Name","Row ID"])
    # RegEx for Data validation
    excel_cell = r'^[a-zA-Z]+\d+$'  # Any combination of text + number without special characters
    slides_regex = r'^[0-9,\s]+$' # Any sequence of numbers seperated with ",", may contain spaces
    mouseCoord_regex = r'/[\-?\[0-9]+,\s?\-?[0-9]+]' # Any positiv/negative combo of [x,y] coords
    
    # Check if each timestamp and ID (unnamed: 0) can be converted to a Python Primitive Data
    for i, row in uilog.iterrows():
        # Value casting tests
        try: pd.to_numeric(row['Unnamed: 0'], downcast="integer")
        except ValueError:
            noiseDf = concatIntoNoiseDf(noiseDf,row['Unnamed: 0'],'Unnamed: 0',i)
        try: pd.to_datetime(row['time:timestamp'])
        except ValueError:
            noiseDf = concatIntoNoiseDf(noiseDf,row['time:timestamp'],'time:timestamp',i)
        
        # RegEx Tests
        if not pd.isnull(row["cell_range"]) and not re.match(excel_cell, str(row["cell_range"])):
            noiseDf = concatIntoNoiseDf(noiseDf,row['cell_range'],'cell_range',i)
        if not pd.isnull(row["slides"]) and not re.match(slides_regex, str(row["slides"])):
            noiseDf = concatIntoNoiseDf(noiseDf,row['slides'],'slides',i)
        if not pd.isnull(row["mouse_coord"]) and not re.match(mouseCoord_regex, str(row["slides"])):
            noiseDf = concatIntoNoiseDf(noiseDf,row['mouse_coord'],'mouse_coord',i)
        
        # Length Tests
        if not pd.isnull(row["workbook"]) and len(row["workbook"]) > 255:
            # https://learn.microsoft.com/en-gb/windows/win32/fileio/naming-a-file?redirectedfrom=MSDN
            noiseDf = concatIntoNoiseDf(noiseDf,row['workbook'],'workbook',i)
        if not pd.isnull(row["current_worksheet"]) and len(row["current_worksheet"]) > 255:
            # https://learn.microsoft.com/en-gb/windows/win32/fileio/naming-a-file?redirectedfrom=MSDN
            noiseDf = concatIntoNoiseDf(noiseDf,row['current_worksheet'],'current_worksheet',i) 

        # Package based tests
        if not pd.isnull(row["browser_url"]) and not validators.url(row["browser_url"]):
            noiseDf = concatIntoNoiseDf(noiseDf,row['browser_url'],'browser_url',i) 
        
        # Data Comparison Checks
        if not pd.isnull(row["tag_category"]) and str(row["tag_category"]).lower() not in HTMLElements:
            noiseDf = concatIntoNoiseDf(noiseDf,row['tag_category'],'tag_category',i) 
        if not pd.isnull(row["concept:name"]) and str(row["concept:name"]).lower() not in conceptNames:
            noiseDf = concatIntoNoiseDf(noiseDf,row['concept:name'],'concept:name',i) 

    # After reading the UI log all values are stored in STR format
    # Some columns should be converted into other datatypes
    # For each column with standard format a method is called to check on the data

    return noiseDf, uilog

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

# Sets for static noise filtering
# https://stackoverflow.com/questions/52928550/js-get-list-of-all-available-standard-html-tags Fighter178 Answer
HTMLElements = {
    "!DOCTYPE","a","abbr","abbr","acronym", # NOT HTML5
    "address", #"applet", # NOT HTML5 (NOT MAJORLY SUPPORTED)
    "area","article","aside","audio","b","base","basefont", # NOT HTML5
    "bdi","bdo","big", # NOT HTML5
    "blockquote","body","br","button","canvas","caption","center", # NOT HTML5
    "cite","code","col","colgroup","data","datalist","dd","del","details","dfn","dialog",#"dir", NOT HTML5 (use "ul" instead)
    "div","dl","dt","em","embed","fieldset","figcaption","figure",#"font", // NOT HTML5 (use CSS)
    "footer","form",#"frame", // NOT HTML5 #"frameset", // NOT HTML5
    "h1","h2","h3","h4","h5","h6","head","header","hr","html","i","iframe","img","input","ins","kbd","label",
    "legend","li","link","main","map","mark","meta","meter","nav",#"noframes", # NOT HTML5
    "noscript","object","ol","optgroup","option","output","p","param","picture","pre","progress","q","rp",
    "rt","ruby","s","samp","script","section","select","small","source","span", #"strike", # NOT HTML5 (Use <del> or <s> instead)
    "strong","style","sub","summary","sup","svg","table","tbody","td","template","textarea","tfoot","th","thead","time",
    "title","tr","track",#"tt", # NOT HTML5 (Use CSS)
    "u","ul","var","video","wbr"
    } # Total of 116 (excluding non-html5 and also comments, which are "<!-- [comment] -->").

# https://github.com/bpm-diag/smartRPA/blob/master/images/SmartRPA_events.pdf
# beforeSaveWorkbook was missing from the tags in the PDF
conceptNames = {
    'beforeSaveWorkbook','urlHashChange','contextMenu','clickCheckboxButton','clickRadioButton','navigateTo','link','typed','form','reload','clickTextField',
    'clickButton','clickLink','selectOptions','selectText','submit','changeField','doubleClick','dragElement','cancelDialog','fullscreen','attachTab',
    'detachTab','newBookmark','removeBookmark','modifyBookmark','moveBookmark','startDownload','erasedDownload','installBrowserExtension','uninstallBrowserExtension',
    'enableBrowserExtension','disableBrowserExtension','closedNotification','clickedNotification','newWindow','closeWindow','newTab','closeTab','moveTab',
    'mutedTab','unmutedTab','pinnedTab','unpinnedTab','audibleTab','zoomTab','changeHistory','created','modified','deleted','Mount','Unmount','moved',
    'programOpen','programClose','selectFile','selectFolder','hotkey','insertUSB','printSubmitted','openFile','openFolder','copy','paste','cut','openWindow','closeWindow',
    'resizeWindow','newWorkbook','openWorkbook','addWorksheet','saveWorkbook','printWorkbook','closeWorkbook','activateWorkbook','deactivateWorkbook','modelChangeWorkbook',
    'newChartWorkbook','afterCalculate','selectWorksheet','deleteWorksheet','doubleClickCellWithValue','doubleClickEmptyCell','rightClickCellWithValue',
    'rightClickEmptyCell','sheetCalculate','editCellSheet','deselectWorksheet','followHiperlinkSheet','pivotTableValueChangeSheet','getRange',
    'getCell','worksheetTableUpdated','addinInstalledWorkbook','addinUninstalledWorkbook','XMLImportWorkbook','XMLExportWorkbook','activateWindow',
    'deactivateWindow','doubleClickWindow','rightClickWindow','newDocument','openDocument','changeDocument','saveDocument','printDocument','activateWindow',
    'deactivateWindow','rightClickPresentation','doubleClickPresentation','newPresentation','newPresentationSlide','closePresentation','savePresentation',
    'openPresentation','printPresentation','slideshowBegin','nextSlideshow','clickNextSlideshow','previousSlideshow','slideshowEnd','SlideSelectionChanged',
    'startupOutlook','quitOutlook','receiveMail','sendMail','logonComplete','newReminder'
    }

HTMLElements = [x.lower() for x in HTMLElements]
conceptNames = [x.lower() for x in conceptNames]
